# PassordSkap

Dette er et personlig prosjekt for å øve på apputvikling. Denne appen er en passordlagrings app, som bruker PySide2, og er under utvikling. 

# Plan for videreutvikling
Det første man burde se på er om man klarer å gjøre key behandlingen mer internt. Per nå så deles key mellom forskjellige widget. Planen foreløpig er å gjøre key privat til login widget for så å lage en encryption helper som vi kan sende videre til de andre widgetene som kan hjelpe med å kryptere og dekryptere.

## Funksjonalitet
- Kan registrere flere brukere.
- Minimumslengde for passord til PassordSkapet.
- Brute force beskyttelse for innlogging.
- Kan lagre, søke/vise passord, kopiere innhold til utklippsbrett ved dobbeltklipp i tabell.
- Kan generere nye passord.
- Kan gå til nettside og kopiere passord fra tabell.
- Mulighet for backup.
- Mulighet for å synkronisere mellom enheter ved hjelp av backup.
- Kan bytte farge tema i appen (bare default er implementert, men man kan lett legge til nye i styles.py THEMES).
- Kan endre på skriftstørrelse.

## Liste over funksjoner som kan implementeres
- add_password_widget: 
    - Bruker tilpasset ordbok for generering av nye passordfraser.
    - Filtrering på emne feltet i tabellen.
- settings_widget: Automatisk utlogging etter en gitt tid.
- Ny widget: En wiki for passordsikkerhte og appen.


## Fargepalett
- se default i styles.py

## Bilder fra app
### Legg til passord
![Legg til passord](../images/add_password_widget.png)

### Vis passord
![Vis passord](../images/show_password_widget.png)

### Backup
![Backup](../images/backup_widget.png)

### Settings
![Settings](../images/settings_widget.png)

## Lisens

Dette prosjektet er dual-lisensiert under følgende lisenser:

### 1. Åpen Kildekode Lisens (Non-Commercial)
PassordSkap er tilgjengelig for ikke-kommersiell bruk under [Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0)](LICENSE-CC-BY-NC.txt). Dette tillater bruk, deling og modifikasjon av programvaren så lenge den ikke brukes kommersielt.

### 2. Proprietær Lisens
For kommersiell bruk, lisensiering eller andre spesialtilpasninger, vennligst kontakt meg på [stiankk@protonmail.com](mailto:stiankk@protonmail.com). En proprietær lisens må inngås for å bruke PassordSkap kommersielt.

## Bidra

Vi setter pris på bidrag! Vennligst se [CONTRIBUTING.md](CONTRIBUTING.md) for retningslinjer.

## Kontakt

For spørsmål, vennligst kontakt meg på [stiankk@protonmail.com](mailto:stiankk@protonmail.com).

## Opphavsrett

© 2024 skk. Alle rettigheter reservert.