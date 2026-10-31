# PokemonBinderPlace
Small Python script that tells me exactly where a Pokémon card belongs in my binder. The binder is sorted by Pokédex number and every page holds 4x4 cards, so the script looks up the Pokédex number and turns it into a page, row and column.

# Setup
1. Install Python 3 (no extra packages needed, only the standard library is used)
2. Make sure you have an internet connection, the Pokédex number is fetched from [PokéAPI](https://pokeapi.co/)

# Usage
```
python main.py
```

Type the name of a Pokémon (or its Pokédex number) and press Enter. Type `q` to quit.

```
Which pokemon do you want to add? pidgey
Pidgey (#16): page 1, row 4, column 4
Which pokemon do you want to add? slowpoke
Slowpoke (#79): page 5, row 4, column 3
Which pokemon do you want to add? mr mime
Mr-mime (#122): page 8, row 3, column 2
```

Names are not case sensitive and spaces are turned into dashes, so `Mr Mime` works too. Some Pokémon have a special name in PokéAPI, for example `nidoran-f` and `nidoran-m`.

# How it works
1. The name is sent to `https://pokeapi.co/api/v2/pokemon-species/<name>`, which returns the Pokédex number
2. Because the Pokédex starts at 1, the number is lowered by 1 so the math starts at 0
3. Page, row and column are calculated from that index:
   ```python
   page = index // slotsPerPage + 1
   slot = index % slotsPerPage
   row = slot // slotsPerRow + 1
   column = slot % slotsPerRow + 1
   ```

Rows are counted from top to bottom and columns from left to right. A binder with a different page layout only needs `slotsPerRow` and `slotsPerColumn` changed at the top of `main.py`.