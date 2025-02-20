## DOGE.gov Federal Payments Data Scraper - Safari

### Setup
```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Usage
```sh
python3 download_doge_links.py
python3 data_parse.py
```

Safari will be loaded, and the links followed one by one.

Pages will be downloaded into the "data" folder along with the doge.gov page's HTML the link was captured from.

The `data_parse.py` script will then parse the HTML page from the fpds.gov page and turn it into a table.

### Reference
[FPDS-NG Data Dictionary](https://www.fpds.gov/wiki/index.php/V1.4_FPDS-NG_Data_Dictionary)

### TODOs
- Enable Chrome-based browser support