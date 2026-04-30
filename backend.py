import requests
import re
from datetime import datetime, timezone

users = {
    "Stefan": {'id': 1246121},
    "Jojo":   {'id': 1237698},
}

url = "https://observation.org/users/"

queries = {
    'Species':              r'(?<=species/">)(\d+)',
    'Birds':                r'species_group_id=1"[\s\S]*?<td class="text-right">(\d+)</td>',
    'Other Arthropods':     r'species_group_id=13"[\s\S]*?<td class="text-right">(\d+)</td>',
    'Bees/Wasps/Ants':      r'species_group_id=17"[\s\S]*?<td class="text-right">(\d+)</td>',
    'Mammals':              r'species_group_id=2"[\s\S]*?<td class="text-right">(\d+)</td>',
    'Moths':                r'species_group_id=8"[\s\S]*?<td class="text-right">(\d+)</td>',
    'Flies':                r'species_group_id=18"[\s\S]*?<td class="text-right">(\d+)</td>',
    'Plants':               r'species_group_id=10"[\s\S]*?<td class="text-right">(\d+)</td>',
    'Reptiles/Amphibians':  r'species_group_id=3"[\s\S]*?<td class="text-right">(\d+)</td>',
    'Butterflies':          r'species_group_id=4"[\s\S]*?<td class="text-right">(\d+)</td>',
    'Insects (other)':      r'species_group_id=6"[\s\S]*?<td class="text-right">(\d+)</td>',
    'Molluscs':             r'species_group_id=7"[\s\S]*?<td class="text-right">(\d+)</td>',
    'Beetles':              r'species_group_id=16"[\s\S]*?<td class="text-right">(\d+)</td>',
    'Bugs/Cicadas':         r'species_group_id=15"[\s\S]*?<td class="text-right">(\d+)</td>',
    'Other Invertebrates':  r'species_group_id=20"[\s\S]*?<td class="text-right">(\d+)</td>',
}

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

for u, data in users.items():
    r = requests.get(url + str(data['id']) + "/", headers=headers)
    print(f"{u}: HTTP {r.status_code}, length {len(r.text)}")
    if r.status_code != 200:
        continue
    if 'species_group_id' not in r.text:
        print(f"  -> page loaded but no species data (logged out / blocked?)")
        continue
    for name, query in queries.items():
        m = re.search(query, r.text)
        data[name] = int(m.group(1)) if m else 0

# Build HTML
categories = list(queries.keys())
sorted_users = sorted(users.items(), key=lambda x: -x[1].get('Species', 0))

rows = ""
for u, data in sorted_users:
    cells = "".join(f"<td>{data.get(c, 0)}</td>" for c in categories)
    rows += f"  <tr><td><strong>{u}</strong></td>{cells}</tr>\n"

headers_html = "".join(f"<th>{c}</th>" for c in categories)
updated = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Species Leaderboard</title>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 1100px; margin: 2em auto; padding: 0 1em; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ padding: .5em .8em; border-bottom: 1px solid #ddd; text-align: right; }}
th:first-child, td:first-child {{ text-align: left; }}
th {{ background: #f4f4f4; position: sticky; top: 0; }}
tr:hover {{ background: #fafafa; }}
.meta {{ color: #666; font-size: .9em; }}
</style></head>
<body>
<h1>🐦 Species Leaderboard</h1>
<p class="meta">Data from observation.org · Updated {updated}</p>
<table>
  <tr><th>User</th>{headers_html}</tr>
{rows}</table>
</body></html>"""

with open("index.html", "w") as f:
    f.write(html)

print("Wrote index.html")
