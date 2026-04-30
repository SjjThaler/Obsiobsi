import requests
import re
from datetime import datetime, timezone

users = {
    "Stefan": {'id': 1246121},
    "Jojo":   {'id': 1237698},
}

url = "https://observation.org/users/"

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

# Build HTML — categories as rows, users as columns
categories = list(queries.keys())
sorted_users = sorted(users.items(), key=lambda x: -x[1].get('Species', 0))

user_headers = "".join(f"<th>{u}</th>" for u, _ in sorted_users)

rows = ""
for cat in categories:
    cells = "".join(f"<td>{data.get(cat, 0):,}</td>" for _, data in sorted_users)
    emphasis = ' class="total"' if cat == 'Species' else ''
    rows += f"  <tr{emphasis}><th scope='row'>{cat}</th>{cells}</tr>\n"

updated = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Species Leaderboard</title>
<style>
  :root {{
    --bg: #fafafa;
    --fg: #222;
    --muted: #666;
    --line: #e0e0e0;
    --accent: #2a7a3a;
    --row-alt: #f4f4f4;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: -apple-system, system-ui, sans-serif;
    background: var(--bg);
    color: var(--fg);
    margin: 0;
    padding: 1em;
    line-height: 1.4;
  }}
  .wrap {{ max-width: 700px; margin: 0 auto; }}
  h1 {{ margin: .2em 0; font-size: 1.6em; }}
  .meta {{ color: var(--muted); font-size: .85em; margin-bottom: 1.5em; }}
  table {{
    width: 100%;
    border-collapse: collapse;
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,.06);
  }}
  th, td {{
    padding: .7em .9em;
    text-align: right;
    border-bottom: 1px solid var(--line);
  }}
  thead th {{
    background: var(--accent);
    color: white;
    font-weight: 600;
  }}
  thead th:first-child {{ text-align: left; }}
  tbody th {{
    text-align: left;
    font-weight: 500;
    background: var(--row-alt);
  }}
  tbody tr:last-child th, tbody tr:last-child td {{ border-bottom: none; }}
  tr.total th, tr.total td {{
    background: #eaf5ec;
    font-weight: 700;
    font-size: 1.05em;
  }}
  @media (max-width: 480px) {{
    body {{ padding: .6em; }}
    h1 {{ font-size: 1.3em; }}
    th, td {{ padding: .55em .6em; font-size: .9em; }}
  }}
</style>
</head>
<body>
<div class="wrap">
  <h1>🐦 Species Leaderboard</h1>
  <p class="meta">Data from observation.org · Updated {updated}</p>
  <table>
    <thead>
      <tr><th>Category</th>{user_headers}</tr>
    </thead>
    <tbody>
{rows}    </tbody>
  </table>
</div>
</body>
</html>"""

with open("index.html", "w") as f:
    f.write(html)

print("Wrote index.html")
