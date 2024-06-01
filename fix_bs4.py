import json

with open(r"C:\Git\prog-rock-network\bs4_input.json",  encoding="utf8") as f:
    data = json.load(f)

for k,v in data.items():
    if "spans" in v.keys():
        v["tags"] = {
            l : {
                "tag" : "span",
                "new_label" : u
            } for l, u in v["spans"].items()
        }

        del v["spans"]

with open(r"C:\Git\prog-rock-network\new_bs4_input.json", "w",  encoding="utf8") as f:
    json.dump(data , f, ensure_ascii=False)