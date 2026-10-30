# FocusBlok

Een zelfgebouwd alternatief voor Brick: een fysiek blok waar je je iPhone tegen tikt om social media te blokkeren. Bellen en berichten blijven gewoon doorkomen.

## Doel
- Minder dan 5 uur schermtijd per dag, vooral minder social media
- Bereikbaar blijven voor mensen (calls, berichten, WhatsApp)
- Drempel verhogen tegen verveling, uitstelgedrag en gewoontegebruik

## Hoe het werkt
1. **Tik op het blok** (NFC-tag), dan gaat de focus aan:
   - De Focus-modus "FocusBlok" wordt ingeschakeld. Die laat alleen mensen en berichtenapps door en verbergt de pagina's met social apps.
   - De status wordt opgeslagen (`focusblok.txt` in iCloud Drive → Shortcuts).
2. **Open je Instagram/TikTok/...** terwijl de focus aan staat, dan stuurt een automatisering je direct terug naar het beginscherm.
3. **Nog een keer tikken** zet de focus uit. Het blok ligt op een vaste plek, zodat stoppen moeite kost.
4. **Maximaal een kwartier uit.** Er loopt een timer van 15 minuten. Wie daarna TikTok/Instagram opent, krijgt de focus automatisch weer aan.
5. **Elke dag om 08:30** gaat de focus automatisch aan.
6. **Meerdere tags** (thuis, tas, weerstation) zetten allemaal dezelfde focus aan of uit.

Aanvullend: grijstinten (driemaal op de zijknop drukken) en one sec.

## Beperkingen
- De echte Brick gebruikt Apple's Screen Time API. Daarvoor heb je een eigen iOS-app nodig, en dus een Mac, Xcode en een developer-account. Deze versie werkt met Shortcuts. Die kun je in theorie omzeilen door de automatisering uit te zetten. Het gaat erom dat er een drempel is, niet dat je volledig wordt opgesloten.
- Shortcuts-automatiseringen kun je niet als bestand meeleveren. Je stelt ze met de hand in via [shortcuts.md](shortcuts.md).
