import json
import urllib.error
import urllib.request

slotsPerRow = 4
slotsPerColumn = 4

slotsPerPage = slotsPerRow * slotsPerColumn

def getPokemon(search):
    url = f"https://pokeapi.co/api/v2/pokemon-species/{search}"
    request = urllib.request.Request(url, headers={"User-Agent": "PokemonBinderPlace"}) # PokeAPI blocks requests without a user agent
    with urllib.request.urlopen(request) as response:
        data = json.load(response)
    return data["name"], data["id"]

while True:
    search = input("Which pokemon do you want to add? ").strip().lower().replace(" ", "-")
    if search == "q":
        break

    try:
        name, pokedexNumber = getPokemon(search)
    except urllib.error.HTTPError:
        print("Pokemon not found, try again.")
        continue
    except urllib.error.URLError:
        print("Could not reach PokeAPI, check your internet connection.")
        continue

    index = pokedexNumber - 1 # pokedex starts at 1, binder math starts at 0
    page = index // slotsPerPage + 1
    slot = index % slotsPerPage
    row = slot // slotsPerRow + 1
    column = slot % slotsPerRow + 1

    print(f"{name.capitalize()} (#{pokedexNumber}): page {page}, row {row}, column {column}")
