import requests
import json
import markdownify
import re
import luadata

print("Script started.")

url = "https://starscape-roblox.fandom.com"


def get_pages(url, continuefrom=""):
    url += "/api.php"
    params = {
        "action": "query",
        "list": "allpages",
        "aplimit": "max",
        "format": "json",
        }
    
    if not continuefrom == "":
        params["continue"] = "-||"
        params["apcontinue"] = continuefrom

    response = requests.get(url, params=params)
    print(response.url + "\n")        
    return response

def get_content(url, title):
    url += f"/rest.php/v1/page/{title}/html"
    print(url + "\n")
    
    response = requests.get(url)
    html = response.text
    stripped_html = html.split("<script>")[0]
    markdown = markdownify.markdownify(stripped_html, heading_style="ATX")
    stripped_markdown = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', markdown)
    return stripped_markdown


def dictkey_exists(dictobj, keys):
    try:
        for key in keys:
            dictobj = dictobj[key]
        return True
    except KeyError:
        return False
        

    
print("Functions initialised \n\n")

count = 1
print(f"Sending request {count}")

data = get_pages(url)
parsed = data.json()
final = parsed["query"]["allpages"]

while dictkey_exists(parsed, ["continue"]):
    count += 1
    print(f"Sending request {count}")
    
    data = get_pages(url, parsed["continue"]["apcontinue"])
    parsed = data.json()
    final += parsed["query"]["allpages"]
    FINAL_JSON = final

print(f"\nPages from the Starscape Wiki ({url}) indexed.")
print(str(len(final)) + " total pages indexed. \n")

with open("@DATA/page_list.json", "w") as file:
    json.dump(final , file, indent=4)
print("JSON file updated. \n\n")





modules = ["Turret", "Ship"]

turret_data = {}
ship_data = {}

for module in modules:
    content = get_content(url, f"Module:{module}%2fData")

    content = content.rsplit("}", 1)[0] + "}"

    content = result = content[content.find("{}"):]

    lua = content[3:]

    lua_list = re.findall(r"\{(.*?)\}", lua, flags=re.DOTALL)
    for i in lua_list:
        index = lua_list.index(i)
        lua_list[index] = "{" + lua_list[index] + "}"

    for i in lua_list:
        data = luadata.unserialize(i, encoding="utf-8", multival=False)
        changes = {"KOR": "Korrelite",
           "REK": "Reknite",
           "GEL": "Gellium",
           "AXN": "Axnit",
           "NAR": "Blue Narcor (Blucor)",
           "RNAR": "Red Narcor (Redcor)",
           "VEX": "Vexnium",
           "WTR": "Water",
           "Subsys": "Subsystems",
           "WEP": "Weapon module slots",
           "DEF": "Defence module slots",
           "ENG": "Engine module slots",
           "RCT": "Reactor (energy) module slots",
           "Time": "Crafting time",
           "Cargo": "Cargo slots"}
        for i in data.copy():
            if i in changes:
                data[changes[i]] = data.pop(i)
        if "Type" in data:
            data["Ship Turret Type"] = data.pop("Type")
            turret_data[data["Ship Turret Type"]] = data
        if "name" in data:
            data["Ship Name"] = data.pop("name")
            ship_data[data["Ship Name"]] = data



combined = turret_data | ship_data
for i in combined:
    title = i
    title = title.replace("/", "-")
    page_content = combined[i]
    
    string = ""
    for q in page_content:
        val = page_content[q]
        string += f"{q}: {val}\n"
    with open(f"data/{title}-stats.md", "w", encoding="utf-8") as file:
        file.write(string)


with open("@DATA/module data/turret_data.json", "w") as file:
    json.dump(turret_data, file, indent=4)
with open("@DATA/module data/ship_data.json", "w") as file:
    json.dump(ship_data, file, indent=4)


##for i in FINAL_JSON:
##    title = i["title"]
##    title = title.replace("/", "-")
##    page_content = get_content(url, title)
##    with open(f"@DATA/pages/{title}.md", "w", encoding="utf-8") as file:
##        file.write(page_content)
    



            

