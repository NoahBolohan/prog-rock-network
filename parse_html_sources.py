import requests
from bs4 import BeautifulSoup
import json

with open("./bs4_input.json") as f:
    data = json.load(f)

bands = {}

# Iterate over BS4 band configs in `bs4_input.json`
for band, info in data.items():
    page = requests.get(info["url"])

    soup = BeautifulSoup(page.content, "html.parser")

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
                    year_values = [
                        s.get_text() for s in td_list[2].find_all('li')
                    ] if len(
                        td_list[2].find_all('li')
                    ) > 0 else td_list[2].get_text()

                    # Prepare to propagate year rowspans
                    if td_list[2].has_attr("rowspan"):
                        skip_year = int(td_list[2]["rowspan"]) - 1
                        

                if skip_instrument:
                    skip_instrument-=1
                else:
                    instrument_values = [
                        s.get_text() for s in td_list[instrument_idx].find_all('li')
                    ] if len(
                        td_list[instrument_idx].find_all('li')
                    ) > 0 else td_list[instrument_idx].get_text()

                    # Prepare to propagate instrument rowspans
                    if td_list[instrument_idx].has_attr("rowspan"):
                        skip_instrument = int(td_list[instrument_idx]["rowspan"]) - 1
                        skip_instrument_values = [s.get_text() for s in td_list[instrument_idx].find_all('li')] if len(td_list[instrument_idx].find_all('li')) > 0 else td_list[instrument_idx].get_text()

            else:
                # Normal row, save year and instrument values
                year_values = [
                    s.get_text() for s in td_list[2].find_all('li')
                ] if len(
                    td_list[2].find_all('li')
                ) > 0 else td_list[2].get_text()

                instrument_values = [
                    s.get_text() for s in td_list[instrument_idx].find_all('li')
                ] if len(
                    td_list[instrument_idx].find_all('li')
                ) > 0 else td_list[instrument_idx].get_text()

                # Prepare to propagate year rowspans
                if td_list[2].has_attr("rowspan"):
                    skip_year = int(td_list[2]["rowspan"]) - 1

                # Prepare to propagate instrument rowspans
                if td_list[instrument_idx].has_attr("rowspan"):
                    skip_instrument = int(td_list[instrument_idx]["rowspan"]) - 1
                    skip_instrument_values = [s.get_text() for s in td_list[instrument_idx].find_all('li')] if len(td_list[instrument_idx].find_all('li')) > 0 else td_list[instrument_idx].get_text()

            members_dict[name]["years_active"] = year_values
            members_dict[name]["instruments"] = instrument_values
            members_dict[name]["member type"] = info["spans"][span]


    bands[band] = members_dict

with open("./input_test.json", "w",  encoding="utf8") as f:
    json.dump(bands , f, ensure_ascii=False) 