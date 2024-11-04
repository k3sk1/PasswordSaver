Her kommer retningslinjer for hvordan man kan bidra til prosjektet.

## Innholdsfortegnelse

- [Testing](#testing)


## Testing

`pytest` blir brukt for testing. Testene kjører automatisk via GitHub Actions når du pusher til GitHub. For å kjøre testene lokalt, følg disse trinnene:

1. **Sørg for at du er i det virtuelle miljøet**:

   ```bash
   # For Windows
   venv\Scripts\activate
   ```

2. **Installer nødvendige pakker (hvis du ikke allerede har gjort det)**

    ```
    pip install --upgrade pip
    pip install -r requirements.txt --extra-index-url https://download.qt.io/official_releases/QtForPython/pyside2/5.15.2
    ```

3. **Kjør testene**

    ```
    pytest tests/
    ```

4. **Struktur for testene**
    ```
    Testfilene ligger i mappen tests/ og starter med test_
    ```

5. **Kjør testene i GitHub Actions**
    ```
    Testene kjøres automatisk når man pysher til main branch
    Workflow filen ligger i .github/workflows/python-test.yml
    ```
