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


def get_pvp_data(leagues=PVP_TARGETS):
    """
    Obtiene los Pokémon PVP de Moonani cuyo nombre contiene
    alguna de las ligas indicadas en `leagues` (por defecto GL1 y UL1,
    es decir, el comportamiento original de mezclar ambas ligas).

    `leagues` puede ser un string ("GL1") o una tupla/lista de strings
    ("GL1", "UL1") para filtrar solo esas ligas.
    """

    if isinstance(leagues, str):
        leagues = (leagues,)

    leagues = tuple(league.strip().upper() for league in leagues if league)
    if not leagues:
        leagues = PVP_TARGETS

    league_pattern = "|".join(re.escape(league) for league in leagues)


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


        pokemon_img = name_cell.find("img")
        image_url = pokemon_img.get("src") if pokemon_img else None


        name = name_cell.get_text(" ", strip=True)

        target_match = re.search(
            rf"\b({league_pattern})\b",
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

        # Validar formato de coordenadas
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
                "image_url": image_url,
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


def get_pvp_gl1_data():
    """Obtiene unicamente los Pokemon PVP de la Great League (GL1)."""
    return get_pvp_data(leagues=("GL1",))


def get_pvp_ul1_data():
    """Obtiene unicamente los Pokemon PVP de la Ultra League (UL1)."""
    return get_pvp_data(leagues=("UL1",))


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
            print(f"Imagen    : {pokemon['image_url']}")
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