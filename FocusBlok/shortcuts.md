# Shortcuts instellen

> Menunamen kunnen per iOS-versie iets verschillen.

## 1. Focus-modus "FocusBlok"
*Instellingen → Focus → + → Aangepast* → naam **FocusBlok**
- **Personen:** sta toe wie je wilt (bijv. alle contacten, of favorieten) en zet *Oproepen van iedereen* aan
- **Apps:** sta Telefoon, Berichten, WhatsApp en andere chatapps toe
- **Schermen → Beginscherm:** kies alleen pagina's waar TikTok en Instagram **niet** op staan

## 2. Shortcut "FocusBlok Aan"
Deze opdracht wordt gebruikt door de toggle en door de kwartier-check.
1. **Stel focus in**: FocusBlok → **Aan** → *Tot ik het uitzet*
2. **Tekst**: `aan` → **Bewaar bestand** naar `Shortcuts/focusblok.txt` (*Vraag waar te bewaren* uit, *Overschrijf* aan)
3. **Toon melding**: "FocusBlok aan"

## 3. Shortcut "FocusBlok Toggle"
1. **Haal bestand op**: `Shortcuts/focusblok.txt`, met *Foutmelding als niet gevonden* **uit**
2. **Tekst**: zet hierin de variabele `Bestand` (zo wordt de inhoud als tekst gelezen)
3. **Als** `Tekst` **bevat** `aan`
   - **Stel focus in**: FocusBlok → **Uit**
   - **Tekst**: `uit` → **Bewaar bestand** naar `Shortcuts/focusblok.txt` (overschrijven)
   - **Formatteer datum**: `Huidige datum` → notatie **ISO 8601**, *Tijd opnemen* aan
   - **Bewaar bestand**: `Geformatteerde datum` naar `Shortcuts/focusblok_uit.txt` (overschrijven)
   - **Start timer**: 15 minuten
   - **Toon melding**: "FocusBlok uit, je hebt 15 minuten"
4. **Anders**
   - **Voer opdracht uit**: *FocusBlok Aan*
5. **Einde Als**

## 4. Automatisering: blok aantikken
*Opdrachten → Automatisering → + → NFC → Scan* → tik de tag aan → geef hem een naam
- **Voer direct uit** (niet "Vraag voor uitvoeren")
- Actie: **Voer opdracht uit** → *FocusBlok Toggle*

### Meerdere tags
Een NFC-automatisering hoort bij precies één tag. Herhaal deze stap dus **per tag**, met dezelfde actie (*FocusBlok Toggle*). Geef elke tag een herkenbare naam:

| Tag | Plek |
|---|---|
| `FocusBlok Thuis` | Vaste plek in huis, bijv. gang of keuken |
| `FocusBlok Tas` | Draagbare versie, altijd in de tas |
| `FocusBlok Weerstation` | In het weerstation (PicoConnect) |

Omdat alle tags dezelfde Shortcut en hetzelfde `focusblok.txt` gebruiken, kun je met de ene tag aanzetten en met de andere uitzetten.

## 5. Automatisering: TikTok/Instagram tegenhouden
*Automatisering → + → App* → kies **TikTok** en **Instagram** → *Is geopend* → **Voer direct uit**
1. **Haal bestand op**: `Shortcuts/focusblok.txt` (*Foutmelding als niet gevonden* uit)
2. **Tekst**: zet hierin de variabele `Bestand`
3. **Als** `Tekst` **bevat** `aan`
   - **Ga naar beginscherm**
   - **Toon melding**: "FocusBlok staat aan 📵"
4. **Anders** (focus staat uit: is het kwartier al om?)
   - **Haal bestand op**: `Shortcuts/focusblok_uit.txt` (*Foutmelding als niet gevonden* uit)
   - **Haal datums op uit invoer**: `Bestand`
   - **Haal tijd tussen datums op**: van `Datums` tot `Huidige datum`, in **minuten**
   - **Als** `Tijd tussen datums` **is groter dan** `14`
     - **Voer opdracht uit**: *FocusBlok Aan*
     - **Ga naar beginscherm**
     - **Toon melding**: "Je kwartier is om ⏰"
   - **Einde Als**
5. **Einde Als**

## 6. Automatisering: elke dag om 08:30 aan
*Automatisering → + → Tijdstip* → **08:30**, **Dagelijks** → **Voer direct uit**
- Actie: **Voer opdracht uit** → *FocusBlok Aan*

## Tijdelijk alternatief: QR-code
Heb je nog geen werkende NFC-tag? Maak dan een QR-code met deze link:
```
shortcuts://run-shortcut?name=FocusBlok%20Toggle
```
Druk hem af en plak hem op het blok. Scan hem met de camera en tik op de link. Dat werkt hetzelfde, alleen met een extra tik.
