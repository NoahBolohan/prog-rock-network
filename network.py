from pyvis.network import Network
import json

net = Network()

with open("./input.json", encoding = 'utf-8') as f:
    data = json.load(f)

for i, (band, info) in enumerate(data.items()):

    net.add_node(
        band,
        label = band,
        group = band,
        # title = info["title"],
        shape = "circularImage",
        image = f"static/{band.replace(' ', '').replace('.', '')}.png",
        size = 30
    )

    for j, (member, info) in enumerate(info["members"].items()):
        net.add_node(
            member,
            label = member,
            size = 10
        )

        edge_header = f"<b>{member} ({band})</b>"
        
        if isinstance(info['years_active'],str):
            years_active_str = "<b>Years active:</b><br>" + info['years_active']
        else:
            years_active_str = "<b>Years active:</b><br>" + ',<br>'.join(info['years_active'])

        instruments_str = "<b>Instruments:</b><br>" + ',<br>'.join(info['instruments'])

        if isinstance(info['instruments'],str):
            instruments_str = "<b>Instruments:</b><br>" + info['instruments']
        else:
            instruments_str = "<b>Instruments:</b><br>" + ',<br>'.join(info['instruments'])

        title_str = '<br><br>'.join(
            [
                edge_header,
                years_active_str,
                instruments_str
            ]
        )

        net.add_edge(
            band,
            member,
            width = 3,
            title = title_str
        )

net.show(
    r"index.html",
    notebook = False
)