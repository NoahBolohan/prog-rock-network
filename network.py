from pyvis.network import Network
import json

net = Network()

with open("./input.json") as f:
    data = json.load(f)

for i, (band, info) in enumerate(data.items()):

    net.add_node(
        band,
        label = band,
        group = band,
        title = info["title"],
        size = 30,
        shape = "circularImage",
        image = f"static/{band.replace(' ', '')}.png"
    )

    for j, (member, info) in enumerate(info["members"].items()):
        net.add_node(
            member,
            label = member,
            size = 10
        )

        years_active_str = "Years active: " + ', '.join(
            [
                f"{info['years_active'][2*ya_idx]} - {info['years_active'][2*ya_idx + 1]}" for ya_idx in range(int(len(info['years_active'])/2))
            ]
        )

        net.add_edge(
            band,
            member,
            width = 3,
            title = years_active_str
        )

net.show(
    r"index.html",
    notebook = False
)