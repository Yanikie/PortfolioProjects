import pypokedex

slotsPerRow = 4
slotsPerColumn = 4

slotsPerPage = slotsPerRow * slotsPerColumn

while True:
    pokedexName = input("Which pokemon do you want to add? ")
    if pokedexName == "q":
        break
    pokemon = pypokedex.get(name=pokedexName)
    pokemonID = pokemon.dex
    print(f"page {int(pokemonID / slotsPerPage) + 1}, slot {pokemonID % slotsPerPage}")