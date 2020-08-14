# indeed-scraper
Some handy scripts to scrape indeed job listing metadata.

If using for companies employers, save your desired search terms in `companies_to_search.csv`

If using for non-specific sampling, save search terms in `control_search_terms.csv`

To use, run the following in `../indeed_scraper/` to create you virtual environment and get scraping!:
```
python3 -m venv .
source env/bin/activate
pip install -r requirements.txt
python run.py
```
