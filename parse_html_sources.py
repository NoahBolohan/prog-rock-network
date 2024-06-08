import requests
import json
import re
import dateutil.parser
import os

from bs4 import BeautifulSoup
from datetime import datetime
from time import sleep

def split_date_string(date_string):
    try:
        if len(ds_split := date_string.split('-')) > 1:
            start = dateutil.parser.parse(ds_split[0].split(';')[0])
            if ds_split[1].split(';')[0] == "present":
                end = datetime.today()
            else:
                end = dateutil.parser.parse(ds_split[1].split(';')[0])
        else:
            start = dateutil.parser.parse(ds_split[0].split(';')[0])
            end = start
        return start, end
    except:
        start = dateutil.parser.parse(re.search(r"[0-9]{4}$", date_string)[0])
        end = start
        return start, end

def range_in_range(a, b, x, y):
    start_a = min(a,b)
    end_a = max(a,b)

    start_c = min(x,y)
    end_c = max(x,y)

    return (start_a<=start_c and end_c<end_a) or (start_a<start_c and end_c<=end_a) or (start_a<start_c and end_c<end_a)
    
def td_specs(td_list,idx):
    values = [
        re.sub(r"[\[].*?[\]]", "", s.get_text().strip()) for s in td_list[idx].find_all('li')
    ] if len(
        td_list[idx].find_all('li')
    ) > 0 else re.sub(r"[\[].*?[\]]", "", td_list[idx].get_text().strip())

    if td_list[idx].has_attr("rowspan"):
        skip = int(td_list[idx]["rowspan"]) - 1
    else:
        skip = 0

    return values, skip

def parse_member_page(soup, info):
    members_dict = {}
    
    # Iterate over member type
    for tag, tag_info in info["tags"].items():

        from_members = soup.select(f"{tag_info["tag"]}#{tag}")[0]

        member_table = from_members.find_next("table", class_="wikitable")

        # Some tables have `rowspan>1` so we need to propagate those values
        skip_year = 0
        skip_instrument = 0

        for row in member_table.find_all("tr")[1:]:

            td_list = row.find_all("td")

            name = td_list[1].find_next('a').get_text() if len(td_list[1].find_all('a')) > 0 else td_list[1].get_text().strip()

            # Create dict entry for member
            members_dict[name] = {}

            instrument_idx = 3

            if skip_year or skip_instrument:
                if skip_year:
                    instrument_idx = 2
                    skip_year-=1
                else:
                    year_values, skip_year = td_specs(td_list, 2)
                        

                if skip_instrument:
                    skip_instrument-=1
                else:
                    instrument_values, skip_instrument = td_specs(td_list, instrument_idx)

            else:
                year_values, skip_year = td_specs(td_list, 2)
                instrument_values, skip_instrument = td_specs(td_list, instrument_idx)

            members_dict[name]["years_active"] = year_values
            members_dict[name]["instruments"] = instrument_values
            members_dict[name]["member type"] = tag_info["new_label"]

    return members_dict

def parse_main_page(soup, info):
    members_dict = {}

    # Iterate over member type
    for tag, tag_info in info["tags"].items():

        if tag_info["tag"] == "span":
            from_members = soup.select(f"{tag_info["tag"]}#{tag}")[0]
        else:
            from_members = soup.findAll(tag_info["tag"],string=tag)[0]

        next_ul = from_members.find_next("ul")

        if "n_ul" in info.keys():
            n_ul = info["n_ul"]
        else:
            n_ul = 1
        
        while n_ul > 0:
            member_list = next_ul.find_all('li')

            for member in member_list:
                names = member.get_text().split('-')[0].split(', ')
                details = re.sub(r"[\[].*?[\]]", "", '-'.join(member.get_text().split('-')[1:]).strip())

                if "years_active" in info.keys():
                    year_values = info["years_active"]
                else:
                    year_values = [s.strip("()").split(',') for s in re.findall(r"\(.*?\)", details)]
                    year_values = [s.strip() for list_of_s in year_values for s in list_of_s if s.strip() != '']

                    for year_value_checked in year_values:
                        for year_value_against in year_values:
                            if range_in_range(*split_date_string(year_value_against), *split_date_string(year_value_checked)):
                                year_values.remove(year_value_checked)

                if '(' in details or ')' in details:
                    instrument_values = [s.split(', ') for s in re.findall(r'(.*?)\(.*?\)', details)]
                    instrument_values = [s.strip() for list_of_s in instrument_values for s in list_of_s if s.strip() != '']
                else:
                    instrument_values = details.split(', ')

                for name in names:
                    members_dict[name.strip()] = {
                        "years_active" : year_values,
                        "instruments" : instrument_values,
                        "member type" : tag_info["new_label"]
                    }

            n_ul -= 1
            next_ul = next_ul.find_next("ul")
            
    return members_dict

def parse_html(
        member_pages = True,
        non_member_pages = True,
        bs4_input_fp = "./bs4_input.json",
        bs4_output_fp = "./input.json",
        local_html_dir = ""
):
    with open(bs4_input_fp) as f:
        data = json.load(f)

    bands = {}

    # Iterate over BS4 band configs in `bs4_input.json`
    for band, info in data.items():

        if (info["members_page"] == 'y' and member_pages) or (info["members_page"] == 'n' and non_member_pages):
            bands[band] = {
                "title" : info["title"],
                "members" : {}
            }

        if os.path.isfile(rf"{local_html_dir}\{band}.html"):
            from_file = True
        else:
            from_file = False
        
        if from_file:
            with open(rf"{local_html_dir}\{band}.html", encoding='utf-8') as fp:
                soup = BeautifulSoup(fp, 'html.parser')
        else:
            page = requests.get(info["members_url"])

            soup = BeautifulSoup(page.content, "html.parser")

            with open(rf"{local_html_dir}\{band}.html", "w", encoding='utf-8') as file:
                file.write(str(soup))
            
            sleep(1)

        for a in soup.find_all(string=re.compile('–')):
            a.replace_with(a.replace('–', '-'))

        if info["members_page"] == 'y':
            if member_pages:
                bands[band]["members"] = parse_member_page(soup, info)
        else:
            if non_member_pages:
                bands[band]["members"] = parse_main_page(soup, info)

    with open(bs4_output_fp, "w",  encoding="utf8") as f:
        json.dump(bands , f, ensure_ascii=False)