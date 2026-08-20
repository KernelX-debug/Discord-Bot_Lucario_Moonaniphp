# 🤖 Lucario - Moonani Discord Pokemon Go Coordinates Bot
![Discord](https://img.shields.io/badge/-Discord-5865F2?style=flat-square&logo=discord&logoColor=ffffff)
![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=ffffff)

Discord bot developed in Python that queries the Moonani PokeList and iFlowGo endpoints to get Pokemon spawns, raids, quests and more; it extracts coordinates and posts them to Discord through commands.

Before you start, remember you can join our Discord server to check out how the bot works live 👇

<a href="https://discord.gg/ZbHNXpUexC" target="_blank">
  <img src="https://scontent.flim30-1.fna.fbcdn.net/v/t1.6435-9/43149276_1607597072873203_5129584054131228672_n.png?stp=dst-jpg_tt6&cstp=mx777x249&ctp=s777x249&_nc_cat=111&ccb=1-7&_nc_sid=127cfc&_nc_ohc=YiNjScvrMtkQ7kNvwFrQAzw&_nc_oc=AdqbuyLStVs_atOMtkq__89vnsy2e3RKrvOkH_Mbzl6rw8MCV_4QpQptEcX1Iz2AS2o&_nc_zt=23&_nc_ht=scontent.flim30-1.fna&_nc_gid=X74IKmr7aL-lMUQXMDdW0g&_nc_ss=7b289&oh=00_AQHWoXefum_YFLnvJbaipkpWiMqiH5wcC-vxF0NoBODPqA&oe=6AAA036C" width="150" alt="Discord">
</a>



## What does this project do. What am I aiming for?

- Queries the `https://moonani.com/PokeList/ajax.php?page=pokemon&action=load` endpoint
- Queries the 40 pages of the `https://pokecoords.iflowgo.com/iflowgopokecoords/api/v1/pokemon-search` endpoint
- If needed, for more demanding tasks it queries `https://pokecoords.iflowgo.com/iflowgopokecoords/api/v1/nearby?lat=40.7&lon=-89.65&radius_km=25&layers=spawns%2Craids%2Cquests&limit=800`, where the `lat` and `lon` variables vary according to the 189 entries in the `hotspots.json` file hosted in this repository.
- Queries rocket, raid and quest information from the Moonani website
- Cleans up the HTML returned by Moonani in fields such as name, IV, coordinates and country
- Extracts copy-paste-ready coordinates, plus a redirect link to Google Maps
- Allows searching by partial name
- Currently filters randomiv, iv100, iv0 and pvp rank1 Pokemon
- Responds on Discord with compact, direct messages
- Has the ability to send multimedia content matching the Pokemon that spawned in the wild

## Essential project structure

- `discord_bot.py`: bot entry point and command definitions
- `moonani_client.py`: HTTP client and result parsing/filtering logic
- `poketest.py`: clean base script used to validate the original idea
- `raidtest.py`: clean base script used to validate the raid feature idea in the game
- `rockettest.py`: clean base script used to validate the rocket feature idea in the game
- `questtest.py`: clean base script used to validate the quest feature idea in the game
- `.env`: environment variables (do not share this data with third parties)
- `requirements.txt`: project dependencies

## 🔎 Commands available on Discord (22)
**Commands for all Discord users (@everyone)**

- `/ping`: checks whether the bot is online
- `/pokemon100`: shows results with a rich format for iv100 Pokemon
- `/pokemon0`: shows results with a rich format for iv0 Pokemon
- `/buscar`: searches for a Pokemon by name and minimum IV across all of iFlowGo's global hotspots
- `/coordsiv100`: returns coordinates in a compact format for iv100 Pokemon, easy to copy
- `/coordsiv0`: returns coordinates in a compact format for iv0 Pokemon, easy to copy
- `/raid`: shows results with a rich format for raids at a global level
- `/rocket`: shows results with a rich format for rockets at a global level
- `/quest`: shows results with a rich format for quests at a global level
  
**Commands for administrative use on Discord (administrator permissions)**

- `/agregar_canal_iv100`: lets you configure a specific channel to send iv100 Pokemon alerts continuously and up to date
- `/agregar_canal_iv0`: lets you configure a specific channel to send iv0 Pokemon alerts continuously and up to date
- `/ver_canales_iv`: shows the saved global iv100 and iv0 channels
- `/quitar_canal_iv100`: disables global iv100 alerts on the previously configured channel
- `/quitar_canal_iv0`: disables global iv0 alerts on the previously configured channel
- `/agregar_canal_pvp_gl1`: lets you configure a specific channel to send alerts for rank1 Pokemon in the Great League
- `/agregar_canal_pvp_ul1`: lets you configure a specific channel to send alerts for rank1 Pokemon in the Ultra League
- `/ver_canales_pvp`: shows the saved global pvp GL1 and UL1 channels
-`/quitar_canal_pvp_gl1`: disables pvp GL1 alerts on the configured channel
-`/quitar_canal_pvp_ul1`: disables pvp UL1 alerts on the configured channel
- `/agregar_seguimiento`: adds alerts for a specific iv100 Pokemon in a channel
- `/ver_seguimientos`: view all configured iv100 Pokemon watches
- `/quitar_seguimiento`: removes alerts for a specific iv100 Pokemon from the channel

## Requirements

- Windows OS (Recommended)
- Python 3.13 (recommended)
- A bot created in the [Discord Developer Portal](https://discord.com/developers/applications) (Required)
- A Railway account or another "cloud platform" to run the bot 24/7 without keeping your computer on (Optional)
- Administrative access on the Discord server where you want to add this service (Required)

# IF YOU'RE LOOKING TO GO STRAIGHT TO THE BOT'S DISCORD SETUP YOU CAN SKIP THIS PART AND GO [HERE](https://github.com/KernelX-debug/Discord-Bot_Lucario_Moonaniphp#instalacion-para-uso-como-bot-de-discord)‼️

## Quick functionality test for Pokemon

Before using the Discord bot, it's possible to validate the extraction and parsing of data from the Moonani endpoint from scratch with a standalone script. This test does not require cloning the full repository or setting up Discord.

### 1. Create a working folder

```powershell
mkdir prueba_moonani
cd prueba_moonani
```

### 2. Create the pre_poketest.py file
Create a Python file called `pre_poketest.py` with this content:

```python
import requests
import re
import html

def extraer_coords(texto):
    match = re.search(r'data-clipboard-text="([^"]+)"', texto)
    return match.group(1) if match else ""

def limpiar_nombre(texto):
    
    texto = html.unescape(texto)
    
    texto = re.sub(r'<[^>]+>', '', texto)
    
    return texto.strip()

def extraer_pais(texto):
    texto = html.unescape(texto)
    texto = re.sub(r'<[^>]+>', '', texto).strip()
    return texto if texto else "??"

url = "https://moonani.com/PokeList/ajax.php?page=pokemon&action=load"
payload = {
    "iv": 100,
    "pvp": 0,
    "pokemons": "",
    "start": 0,
    "length": 230,
    "draw": 1
}
headers = {
    "Referer": "https://moonani.com/PokeList/index.php",
    "Content-Type": "application/x-www-form-urlencoded"
}

r = requests.post(url, data=payload, headers=headers)
data = r.json().get("data", [])

print(f"Total pokémones recibidos: {len(data)}\n")

for p in data:
    nombre = limpiar_nombre(p["Name"])
    coords = extraer_coords(p["Coords"])
    shiny  = "✨ SHINY" if p["Shiny"] == "Yes" else ""
    pais   = extraer_pais(p["Country"])

    print(f"{'='*50}")
    print(f"🎯 {nombre} #{p['Number']} {shiny}")
    print(f"📍 {coords}")
    print(f"⚡ CP: {p['CP']} | Nivel: {p['Level']}")
    print(f"💪 ATK:{p['Attack']} DEF:{p['Defense']} HP:{p['HP']}")
    print(f"⏱️  Inicio: {p['Start Time']}")
    print(f"⏱️  Fin:    {p['End Time']}")
    print(f"🌍 País: {pais}")
    print(f"🗺️  https://maps.google.com/?q={coords}")
```

### 3. Install the required dependency

```powershell
py -3.13 -m pip install requests
```

### 4. Run the test

```powershell
py -3.13 pre_poketest.py
```

## Expected result
- A direct HTTP request is made to the Moonani endpoint.
- The received JSON response is processed.
- The embedded HTML in fields such as Name, Coords and Country is cleaned up.
- A list of Pokemon is printed to the console with name, coordinates, CP, level, stats, spawn time and a Google Maps link.
- This test lets you technically verify that the endpoint responds correctly and that the base parsing works before integrating the logic into the Discord bot.

## Reference image

<p align="center">
  <img src="assets/testmoonami.png" alt="test de moonami" width="100%">
</p>

## Quick functionality test for rank1 pvp GL1 and UL1 Pokemon

Before using the Discord bot, it's also possible to validate the extraction and parsing of data from the pvp section of the Moonani website from scratch with a standalone script. This test does not require cloning the full repository or setting up Discord.

### 1. Create a working folder

```powershell
mkdir prueba_moonani
cd prueba_moonani_pvp
```

### 2. Create the pre_pvptest.py file
Create a Python file called `pre_poketest.py` with this content:

```python
import re
import time
import random
import requests
from bs4 import BeautifulSoup

URL = "https://moonani.com/PokeList/pvp.php"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Referer": "https://moonani.com/PokeList/",
}

PVP_TARGETS = ("GL1", "UL1")

session = requests.Session()
session.headers.update(HEADERS)

def get_pvp_data():
    """
    Obtiene los Pokémon PVP de Moonani cuyo nombre contiene
    GL1 o UL1.
    """

    time.sleep(random.uniform(1.5, 3.5))

    response = session.get(URL, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    pokemon_list = []

    rows = soup.select("#customers tbody tr")

    for row in rows:

        cells = row.find_all("td")

        if len(cells) < 16:
            continue


        name_cell = cells[1]

        name = name_cell.get_text(" ", strip=True)

        target_match = re.search(
            r"\b(GL1|UL1)\b",
            name,
            re.IGNORECASE
        )

        if not target_match:
            continue

        league = target_match.group(1).upper()

        try:
            pokemon_id = int(cells[2].get_text(strip=True))
        except ValueError:
            pokemon_id = None

        coords = None

        button = cells[3].find("button")

        if button:
            coords = button.get("data-clipboard-text")

        if not coords:
            continue

        if not re.fullmatch(
            r"-?\d+(?:\.\d+)?,-?\d+(?:\.\d+)?",
            coords
        ):
            continue

        try:
            cp = int(cells[4].get_text(strip=True))
        except ValueError:
            cp = None

        try:
            level = int(cells[5].get_text(strip=True))
        except ValueError:
            level = None

        try:
            attack = int(cells[6].get_text(strip=True))
        except ValueError:
            attack = None

        try:
            defense = int(cells[7].get_text(strip=True))
        except ValueError:
            defense = None

        try:
            hp = int(cells[8].get_text(strip=True))
        except ValueError:
            hp = None

        iv_text = cells[9].get_text(" ", strip=True)

        iv_match = re.search(r"(\d+(?:\.\d+)?)\s*%", iv_text)

        if iv_match:
            iv_percent = float(iv_match.group(1))
        else:
            iv_percent = None

        shiny_text = cells[10].get_text(" ", strip=True)

        shiny = shiny_text.lower() == "yes"


        pvp_value = cells[11].get_text(" ", strip=True)

        try:
            pvp_rank = int(cells[12].get_text(strip=True))
        except ValueError:
            pvp_rank = None

        start_time = cells[13].get_text(strip=True)
        end_time = cells[14].get_text(strip=True)

        country = None

        flag_img = cells[15].find("img")

        if flag_img:
            flag_src = flag_img.get("src", "")

            flag_match = re.search(
                r"flags/([a-z]{2})\.png",
                flag_src,
                re.IGNORECASE
            )

            if flag_match:
                country = flag_match.group(1).upper()

        pokemon_list.append(
            {
                "name": name,
                "league": league,
                "pokemon_id": pokemon_id,
                "coords": coords,
                "cp": cp,
                "level": level,
                "attack": attack,
                "defense": defense,
                "hp": hp,
                "iv_percent": iv_percent,
                "shiny": shiny,
                "pvp": pvp_value,
                "pvp_rank": pvp_rank,
                "start_time": start_time,
                "end_time": end_time,
                "country": country,
                "maps_url": f"https://maps.google.com/?q={coords}",
            }
        )

    return pokemon_list

if __name__ == "__main__":

    try:
        pvp_data = get_pvp_data()

        print(
            f"\nSe encontraron "
            f"{len(pvp_data)} Pokémon PVP GL1/UL1:\n"
        )

        for pokemon in pvp_data:

            print("=" * 60)

            print(f"Nombre    : {pokemon['name']}")
            print(f"Liga      : {pokemon['league']}")
            print(f"ID        : {pokemon['pokemon_id']}")
            print(f"Coords    : {pokemon['coords']}")
            print(f"CP        : {pokemon['cp']}")
            print(f"Nivel     : {pokemon['level']}")

            print(
                f"IVs       : "
                f"{pokemon['attack']}/"
                f"{pokemon['defense']}/"
                f"{pokemon['hp']}"
            )

            print(f"IV        : {pokemon['iv_percent']}%")
            print(f"Shiny     : {pokemon['shiny']}")
            print(f"PVP       : {pokemon['pvp']}")
            print(f"PVP Rank  : {pokemon['pvp_rank']}")
            print(f"Inicio    : {pokemon['start_time']}")
            print(f"Fin       : {pokemon['end_time']}")
            print(f"País      : {pokemon['country']}")
            print(f"Maps      : {pokemon['maps_url']}")

    except requests.RequestException as e:
        print(f"Error HTTP: {e}")

    except Exception as e:
        print(f"Error: {e}")
```

### 3. Install the required dependency

```powershell
pip install requests beautifulsoup4
```

### 4. Run the test

```powershell
py -3.13 pre_pvptest.py
```

## Expected result
- A direct HTTP request is made to the Moonani pvp page.
- The received HTML is processed using BeautifulSoup.
- The data embedded in the pvp table is extracted and cleaned up.
- The Great League and Ultra League rank1 pvp Pokemon are correctly detected.
- Coordinates are extracted from the `data-clipboard-text` attributes.
- The start and end times of each wild spawn are correctly obtained.
- An organized list is printed to the console with the matching league, cp, iv, stats, coordinates, country, spawn time, expiration time and a Google Maps link.
- This test lets you technically verify that the page responds correctly and that the base parsing works before integrating the logic into the Discord bot.

## Reference image

<p align="center">
  <img src="assets/testpvp.png" alt="test de moonami" width="100%">
</p>


## Quick functionality test for rockets

Before using the Discord bot, it's possible to validate the extraction and parsing of the dynamic table data from Moonani's rockets section from scratch with a standalone script. This test does not require cloning the full repository or setting up Discord.

### 1. Create a working folder

```powershell
mkdir prueba_rockets_moonani
cd prueba_rockets_moonani
```

### 2. Install the required dependencies

```powershell
pip install requests beautifulsoup4
```

### 3. Create the rockettest.py file

```powershell
New-Item pre_rockettest.py -ItemType File
```

### 4. Edit the file with Windows' native Notepad

```powershell
notepad pre_rockettest.py
```

**Paste the following content:**

```python
import re
import time
import random
import requests
from bs4 import BeautifulSoup

URL = "https://moonani.com/PokeList/rocket.php"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/136.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://moonani.com/PokeList/",
}

COORDS_REGEX = re.compile(r"(-?\d+\.\d+,-?\d+\.\d+)")

session = requests.Session()
session.headers.update(HEADERS)


def clean_text(value):
    return value.strip().replace("\n", " ").replace("\t", " ")


def get_rocket_data():
    time.sleep(random.uniform(1.5, 3.5))

    response = session.get(URL, timeout=20)

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    rockets = []

    rows = soup.find_all("tr")

    for row in rows:
        cells = row.find_all("td")

        if len(cells) < 7:
            continue

        try:

            rocket_type = clean_text(cells[0].get_text())

            number = clean_text(cells[1].get_text())

            coords_match = COORDS_REGEX.search(str(cells[2]))

            if not coords_match:
                continue

            coords = coords_match.group(1)

            start_time = clean_text(cells[4].get_text())

            end_time = clean_text(cells[5].get_text())

            country = clean_text(cells[6].get_text()).upper()

            rockets.append(
                {
                    "rocket_type": rocket_type,
                    "number": number,
                    "coords": coords,
                    "start_time": start_time,
                    "end_time": end_time,
                    "country": country,
                    "maps_url": f"https://maps.google.com/?q={coords}",
                }
            )

        except Exception:
            continue

    return rockets


if __name__ == "__main__":
    try:
        rocket_data = get_rocket_data()

        print(f"\nSe encontraron {len(rocket_data)} Rockets:\n")

        for rocket in rocket_data:
            print("=" * 60)
            print(f"Tipo Rocket : {rocket['rocket_type']}")
            print(f"Número      : {rocket['number']}")
            print(f"Coords       : {rocket['coords']}")
            print(f"Inicio       : {rocket['start_time']}")
            print(f"Fin          : {rocket['end_time']}")
            print(f"País         : {rocket['country']}")
            print(f"Maps         : {rocket['maps_url']}")

    except Exception as e:
        print(f"Error: {e}")
```

**IT'S IMPORTANT TO SAVE THE NOTEPAD CONTENT WITH `ctrl+g` OR VIA FILE/SAVE**

### 5. Run the Python script

```powershell
python pre_rockettest.py
```

## Expected result

- A direct HTTP request is made to the Moonani Rocket page.
- The received HTML is processed using BeautifulSoup.
- The data embedded in the Rockets table is extracted and cleaned up.
- Rocket types and Rocket leaders (Arlo, Cliff, Sierra and Giovanni) are correctly detected.
- Coordinates are extracted from the `data-clipboard-text` attributes.
- The start and end times of each Rocket are correctly obtained.
- An organized list is printed to the console with the Rocket type, Rocket leader, coordinates, country, spawn time, expiration time and a Google Maps link.
- This test lets you technically verify that the page responds correctly and that the base parsing works before integrating the logic into the Discord bot.

**IMPORTANT UPDATE: Lately there have been errors in the amount of information in Moonani's rockets section dynamic table; this issue is out of my hands since I'm not an official developer of this web platform.**
* You can check the page status at [Moonani Rockets Status](https://moonani.com/PokeList/rocket.php)

*"if you're not paying for the product, you are the product"*

## Reference image

<p align="center">
  <img src="assets/testrocket.png" alt="test de rocket" width="100%">
</p>

## Quick functionality test for raids

Before using the Discord bot, it's possible to validate the extraction and parsing of Moonani's dynamic table data in the raids section from scratch with a standalone script, using the `BeautifulSoup` library. This test does not require cloning the full repository or setting up Discord.

### 1. Create a working folder

```powershell
mkdir prueba_raids_moonani
cd prueba_raids_moonani
```

### 2. Create the pre_raidtest.py file
Create a Python file called `pre_raidtest.py` with this content:

```python
import re
import time
import random
import requests
from bs4 import BeautifulSoup

URL = "https://moonani.com/PokeList/raid.php"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/136.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://moonani.com/PokeList/",
}

session = requests.Session()
session.headers.update(HEADERS)


def clean_text(value):
    return re.sub(r"\s+", " ", value).strip()


def get_raid_data():

    time.sleep(random.uniform(1.5, 3.5))

    response = session.get(URL, timeout=20)

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    raids = []

    rows = soup.find_all("tr")

    for row in rows:

        cells = row.find_all("td")

        if len(cells) < 7:
            continue

        try:

            raid_name = clean_text(
                cells[0].get_text(" ", strip=True)
            )

            level = clean_text(
                cells[2].get_text(" ", strip=True)
            )

            coords_button = cells[3].find(
                attrs={"data-clipboard-text": True}
            )

            if not coords_button:
                continue

            coords = coords_button[
                "data-clipboard-text"
            ].strip()

            country_match = re.search(
                r'flags/([a-z]{2})\.png',
                str(cells[6]),
                re.IGNORECASE
            )

            country = (
                country_match.group(1).upper()
                if country_match else "N/A"
            )

            raids.append(
                {
                    "raid_name": raid_name,
                    "level": level,
                    "coords": coords,
                    "country": country,
                    "maps_url": (
                        f"https://maps.google.com/?q={coords}"
                    ),
                }
            )

        except Exception:
            continue

    return raids


if __name__ == "__main__":

    try:

        raid_data = get_raid_data()

        print(f"\nSe encontraron {len(raid_data)} Raids:\n")

        for raid in raid_data:

            print("=" * 60)

            print(f"Raid         : {raid['raid_name']}")
            print(f"Nivel        : {raid['level']}")
            print(f"Coords       : {raid['coords']}")
            print(f"País         : {raid['country']}")
            print(f"Maps         : {raid['maps_url']}")

    except Exception as e:

        print(f"Error: {e}")
```

### 3. Install the required dependency

```powershell
pip install requests beautifulsoup4
```

### 4. Run the test

```powershell
py -3.13 pre_raidtest.py
```

## Expected result
- A direct HTTP request is made to the Moonani Raids page.
- The received HTML is processed using BeautifulSoup.
- The data embedded in the Raids table is extracted and cleaned up.
- Raid bosses and their raid level are correctly detected.
- Coordinates are extracted from the `data-clipboard-text` attributes.
- The start and end times of each Raid are correctly obtained.
- An organized list is printed to the console with the raid boss, level, coordinates, country, start time, expiration time and a Google Maps link.
- This test lets you technically verify that the page responds correctly and that the base parsing works before integrating the logic into the Discord bot.

## Reference image

<p align="center">
  <img src="assets/testraid.png" alt="test de moonami" width="100%">
</p>

## Quick functionality test for quests

Before using the Discord bot, it's possible to validate the extraction and parsing of Moonani's dynamic table data in the quests section with a standalone script, using the `BeautifulSoup` library. This test does not require cloning the full repository or setting up Discord.

### 1. Create a working folder

```powershell
mkdir prueba_quests_moonani
cd prueba_quests_moonani
```

### 2. Create the pre_questtest.py file
Create a Python file called `pre_questtest.py` with this content:

```python
import re
import requests
from bs4 import BeautifulSoup

URL = "https://moonani.com/PokeList/quest.php"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/136.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://moonani.com/PokeList/",
}

session = requests.Session()
session.headers.update(HEADERS)


def limpiar_texto(texto):
    return re.sub(r"\s+", " ", texto).strip()


def obtener_quests():
    response = session.get(URL, timeout=20)

    if response.status_code != 200:
        print(f"[!] Error HTTP: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    filas = soup.find_all("tr")

    quests = []

    for fila in filas:
        columnas = fila.find_all("td")

        if len(columnas) < 6:
            continue

        try:
            pokemon = limpiar_texto(columnas[0].get_text())
            pokemon_id = limpiar_texto(columnas[1].get_text())
            quest = limpiar_texto(columnas[2].get_text())
            coords = limpiar_texto(columnas[3].get_text())
            fecha_inicio = limpiar_texto(columnas[4].get_text())
            fecha_fin = limpiar_texto(columnas[5].get_text())

            pais = "Desconocido"
            if len(columnas) >= 7:
                pais = limpiar_texto(columnas[6].get_text())

            if "," not in coords:
                continue

            lat, lon = coords.split(",", 1)

            maps = f"https://maps.google.com/?q={lat},{lon}"

            quests.append({
                "pokemon": pokemon,
                "pokemon_id": pokemon_id,
                "quest": quest,
                "coords": coords,
                "inicio": fecha_inicio,
                "fin": fecha_fin,
                "pais": pais.upper(),
                "maps": maps
            })

        except Exception:
            continue

    return quests


def mostrar_quests(quests):
    print("\n")
    print("=" * 75)
    print("                    POKÉMON GO QUEST SCANNER")
    print("=" * 75)

    print(f"\n[+] Quests encontradas: {len(quests)}\n")

    for i, q in enumerate(quests, start=1):

        print("╔" + "═" * 70 + "╗")
        print(f"║ QUEST #{i}".ljust(71) + "║")
        print("╠" + "═" * 70 + "╣")

        print(f"║ Pokémon      : {q['pokemon']}".ljust(71) + "║")
        print(f"║ Pokémon ID   : {q['pokemon_id']}".ljust(71) + "║")
        print(f"║ Quest        : {q['quest']}".ljust(71) + "║")
        print(f"║ Coordenadas  : {q['coords']}".ljust(71) + "║")
        print(f"║ País         : {q['pais']}".ljust(71) + "║")
        print(f"║ Inicio       : {q['inicio']}".ljust(71) + "║")
        print(f"║ Expira       : {q['fin']}".ljust(71) + "║")
        print(f"║ Google Maps  : {q['maps']}".ljust(71) + "║")

        print("╚" + "═" * 70 + "╝")
        print()

    print(f"[✓] Total mostrado: {len(quests)} quests")


if __name__ == "__main__":
    try:
        quests = obtener_quests()

        if quests:
            mostrar_quests(quests)
        else:
            print("[!] No se encontraron quests.")

    except Exception as e:
        print(f"[!] Error: {e}")

```

### 3. Install the required dependency

```powershell
pip install requests beautifulsoup4
```

### 4. Run the test

```powershell
py -3.13 pre_questtest.py
```

## Expected result
- A direct HTTP request is made to the Moonani Quests page.
- The received HTML is processed using BeautifulSoup.
- The data embedded in the Quests table is extracted and cleaned up.
- The quest reward and its duration are correctly detected.
- Coordinates are extracted from the `data-clipboard-text` attributes.
- The start and end times of each quest are correctly obtained.
- An organized list is printed to the console with the quest reward, ID, coordinates, country, start time, expiration time and a Google Maps link.
- This test lets you technically verify that the page responds correctly and that the base parsing works before integrating the logic into the Discord bot.

## Reference image

<p align="center">
  <img src="assets/testquest.png" alt="test de moonami" width="100%">
</p>


## Installation for use as a Discord bot
### Clone the repository

```powershell
git clone https://github.com/KernelX-debug/Discord-Bot_Lucario_Moonaniphp.git
```
### Edit files and install dependencies

1. In the project folder.

```powershell
cd Discord-Bot_Lucario_Moonaniphp
```

2. Install the dependencies.

```powershell
py -3.13 -m pip install -r requirements.txt
```

3. Edit the `.env` file.
```powershell
@"
DISCORD_BOT_TOKEN=pega_aqui_el_token_de_tu_bot
DISCORD_GUILD_ID=pega_aqui_el_id_del_servidor_discord
MOONANI_TIMEOUT=20
MOONANI_PAGE_SIZE=100
MOONANI_MAX_SCAN_RECORDS=10000
MOONANI_RESOLVE_COUNTRIES=false
MOONANI_GEOCODER_ENDPOINT=https://nominatim.openstreetmap.org/reverse
MOONANI_GEOCODER_USER_AGENT=Lucario Discord Bot/1.0
LUCARIO_SETTINGS_PATH=lucario_guild_settings.json
LUCARIO_MONITOR_INTERVAL_SECONDS=45
LUCARIO_ALERT_LIMIT_100IV=250
LUCARIO_ALERT_LIMIT_0IV=250
"@ | Set-Content .env

```

## What the variables mean

- `DISCORD_BOT_TOKEN`: your bot's private token
- `DISCORD_GUILD_ID`: optional, speeds up the appearance of slash commands on a specific server
- `MOONANI_TIMEOUT`: maximum wait time for HTTP requests
- `MOONANI_PAGE_SIZE`: how many records to request per block from the endpoint
- `MOONANI_MAX_SCAN_RECORDS`: maximum number of records to scan in a search
- `MOONANI_RESOLVE_COUNTRIES`: tries to resolve the country from coordinates when Moonani doesn't return it (UNDER MAINTENANCE DUE TO REQUEST LIMIT {e409}, USE "false" BY DEFAULT)
- `MOONANI_GEOCODER_ENDPOINT`: reverse geocoding endpoint
- `MOONANI_GEOCODER_USER_AGENT`: HTTP identifier for the geocoder
- `LUCARIO_SETTINGS_PATH=lucario_guild_settings.json`: variables for the server ID and Discord channels assigned to send iv100/iv0 coordinates
- `LUCARIO_MONITOR_INTERVAL_SECONDS=45`: constant polling set to 45 seconds
- `LUCARIO_ALERT_LIMIT_100IV=250`: limit of 100iv alerts per batch.
- `LUCARIO_ALERT_LIMIT_0IV=250`: limit of 0iv alerts per batch.
## Running it

```powershell
py -3.13 discord_bot.py
```

## Usage examples

```text
/pokemon100 nombre: wiglett cantidad: 3
/coordsiv100 nombre: pikachu cantidad:5
/raid nombre: kyurem cantidad: 2
/quest nombre: kecleon cantidad: 4
/rocket tipo: Arlo cantidad: 5
/buscar nombre: gyarados miniv: 70 cantidad: 5
```

## How it works

<p align="center">
  <img src="assets/chikoritasearch.png" alt="Busqueda de Chikorita" width="45%">
  <img src="assets/agregar_canal_iv100.png" alt="Agregar canal iv100" width="41.5%">
</p>

## 🔓 How to invite the bot to your server

1. Open your application in the [Discord Developer Portal](https://discord.com/developers/applications).
2. Go to `OAuth2` > `URL Generator`.
3. Check the `bot` and `applications.commands` scopes.
4. Grant permissions such as `View Channels`, `Send Messages`, `Embed Links` and `Read Message History`.
5. Open the generated link and select your server.

## 🚀 Future improvements

- A solution to the rockets issue could be looked into, since the filters for them do appear in the pokelist app 🤔
- As of today, this is already considered an official version of the project 🥳🥳

## ⚙️ Notes

- If Moonani doesn't return a country, the bot shows `Unknown`. You can enable `MOONANI_RESOLVE_COUNTRIES=true` to try to resolve the country from the coordinates using reverse geocoding.
- The public Nominatim endpoint may return `429 Too Many Requests` if it receives too many queries. For a public bot, it's best to use your own geocoder, a self-hosted one, or a provider with an adequate quota.
- The rockets section may have temporary issues with the dynamic table data, as mentioned earlier; this is due to the page itself.
- If you run into `CommandInvokeError` when running a command on Discord, I recommend checking Windows Defender's actions and allowing Python's actions on the computer; either way, this doesn't affect the bot's functioning. In the case of a server deployment this isn't a major issue either.
- You can check the assets folder to see multimedia content of this bot being used on Discord.
- If you're reading this at just the right moment, be careful with the earthquakes that have been happening over the past few weeks, brother..


<p align="left">
  <img src="https://media1.tenor.com/m/Qr0iBlPVDgUAAAAd/emperors-new-groove-kuzco.gif" alt="Kuzco" width="300" style="margin-left: 20px;">
</p>


## ☁️ Free 24/7 test hosting

To keep the bot active without needing to keep your PC on, you can use [Railway](https://railway.app). Just connect your GitHub repository and add the following environment variables with their respective values in the **Variables** section:

`DISCORD_BOT_TOKEN`,
`DISCORD_GUILD_ID`,
`MOONANI_TIMEOUT`,
`MOONANI_PAGE_SIZE`,
`MOONANI_MAX_SCAN_RECORDS`,
`MOONANI_RESOLVE_COUNTRIES`,
`MOONANI_GEOCODER_ENDPOINT`,
`MOONANI_GEOCODER_USER_AGENT`,
`LUCARIO_SETTINGS_PATH`,
`LUCARIO_MONITOR_INTERVAL_SECONDS`,
`LUCARIO_ALERT_LIMIT_100IV`,
`LUCARIO_ALERT_LIMIT_0IV`

## 👉 Sponsor me ♡

<p align="left">
  <a href="https://buymeacoffee.com/ghericasas" target="_blank">
    <img src="https://github.com/user-attachments/assets/6db1edad-4682-4a4f-803f-b7c416c19cd3" alt="Buy Me A Coffee" width="217">
  </a>
</p>

## 📜 License
**MIT License**

[MIT License org](https://mit-license.org/license.txt)
