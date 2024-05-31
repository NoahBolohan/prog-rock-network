import requests
from bs4 import BeautifulSoup
import json
import re
import dateutil.parser

def split_date_string(date_string):
    if len(ds_split := date_string.split('–')):
        start = dateutil.parser.parse(ds_split[0].split(';')[0])
        end = dateutil.parser.parse(ds_split[1].split(';')[0])
    else:
        start = dateutil.parser.parse(ds_split[0].split(';')[0])
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
    for span in info["spans"].keys():

        from_members = soup.select(f"span#{span}")[0]

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
            members_dict[name]["member type"] = info["spans"][span]

    return members_dict

def parse_main_page(soup, info):
    members_dict = {}

    # Iterate over member type
    for span in info["spans"].keys():

        from_members = soup.select(f"span#{span}")[0]
        member_list = from_members.find_next("ul").find_all('li')

        for member in member_list:
            name = member.get_text().split(' – ')[0]
            details = re.sub(r"[\[].*?[\]]", "", '–'.join(member.get_text().split(' – ')[1:]))

            year_values = [s.strip("()").split(',') for s in re.findall(r"\(.*?\)", details)]
            year_values = [s.strip() for list_of_s in year_values for s in list_of_s if s.strip() != '']

            for year_value_checked in year_values:
                for year_value_against in year_values:
                    if range_in_range(*split_date_string(year_value_against), *split_date_string(year_value_checked)):
                        year_values.remove(year_value_checked)


            instrument_values = [s.split(', ') for s in re.findall(r'(.*?)\(.*?\)', details)]
            instrument_values = [s.strip() for list_of_s in instrument_values for s in list_of_s if s.strip() != '']

            members_dict[name] = {
                "years_active" : year_values,
                "instruments" : instrument_values,
                "member type" : info["spans"][span]
            }
            
    return members_dict

with open("./bs4_input.json") as f:
    data = json.load(f)

bands = {}

# Iterate over BS4 band configs in `bs4_input.json`
for band, info in data.items():

    bands[band] = {
        "title" : info["title"],
        "members" : {}
    }
    
    page = requests.get(info["members_url"])

    soup = BeautifulSoup(page.content, "html.parser")

    if info["members_page"] == 'y':
        bands[band]["members"] = parse_member_page(soup, info)
        continue
    else:
        bands[band]["members"] = parse_main_page(soup, info)

with open("./input.json", "w",  encoding="utf8") as f:
    json.dump(bands , f, ensure_ascii=False) 