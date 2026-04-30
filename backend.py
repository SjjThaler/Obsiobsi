import requests
import re
from datetime import datetime, timezone

users = {
    "Stefan": {'id': 1246121},
    "Jojo":   {'id': 1237698},
    "Wastl": {'id': 1231639},
    "Sophie": {'id': 1229820},
}

url = "https://observation.org/users/"

# Build patterns programmatically — same shape for every category
def pat(group_id):
    return rf'species_group_id={group_id}"[\s\S]*?<td class="text-right">(\d+(?:,\d+)*)</td>'

queries = {
    'Species':              r'(?<=species/">)(\d+(?:,\d+)*)',
    'Birds':                pat(1),
    'Mammals':              pat(2),
    'Reptiles/Amphibians':  pat(3),
    'Butterflies':          pat(4),
    'Dragonflies':          pat(5),
    'Insects (other)':      pat(6),
    'Molluscs':             pat(7),
    'Moths':                pat(8),
    'Fish':                 pat(9),
    'Plants':               pat(10),
    'Fungi':                pat(11),
    'Mosses/Lichens':       pat(12),
    'Other Arthropods':     pat(13),
    'Locusts/Crickets':     pat(14),
    'Bugs/Cicadas':         pat(15),
    'Beetles':              pat(16),
    'Bees/Wasps/Ants':      pat(17),
    'Flies':                pat(18),
    'Algae/Seaweeds':       pat(19),
    'Other Invertebrates':  pat(20),
}

headers = {
    "User-Agent": "curl/8.5.0",
    "Accept-Language": "en-US,en;q=0.9",
}

for u, data in users.items():
    r = requests.get(url + str(data['id']) + "/", headers=headers)
    print(f"{u}: HTTP {r.status_code}, length {len(r.text)}")
    if r.status_code != 200:
        continue
    if 'species_group_id' not in r.text:
        print(f"  -> response preview: {r.text[:500]}")
        continue
    for name, query in queries.items():
        m = re.search(query, r.text)
        data[name] = int(m.group(1).replace(',', '')) if m else 0

# Build HTML
categories = list(queries.keys())
sorted_users = sorted(users.items(), key=lambda x: -x[1].get('Species', 0))

rows = ""
for u, data in sorted_users:
    cells = "".join(f"<td>{data.get(c, 0):,}</td>" for c in categories)
    rows += f"  <tr><td><strong>{u}</strong></td>{cells}</tr>\n"

headers_html = "".join(f"<th>{c}</th>" for c in categories)
updated = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Species Leaderboard</title>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 1400px; margin: 2em auto; padding: 0 1em; }}
table {{ border-collapse: collapse; width: 100%; font-size: .9em; }}
th, td {{ padding: .4em .6em; border-bottom: 1px solid #ddd; text-align: right; }}
th:first-child, td:first-child {{ text-align: left; }}
th {{ background: #f4f4f4; position: sticky; top: 0; }}
tr:hover {{ background: #fafafa; }}
.meta {{ color: #666; font-size: .9em; }}
.scroll {{ overflow-x: auto; }}
</style></head>
<body>
<h1>Pokedex-Board</h1>
<p class="meta">Data from observation.org · Updated {updated}</p>
<div class="scroll"><table>
  <tr><th>User</th>{headers_html}</tr>
{rows}</table></div>
</body></html>"""

with open("index.html", "w") as f:
    f.write(html)

print("Wrote index.html")
