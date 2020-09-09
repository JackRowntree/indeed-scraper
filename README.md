# indeed-scraper
Some handy scripts to scrape indeed job listing metadata.

## Installation
To use, run the following in `../indeed_scraper/` to create you virtual environment:
```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```
## Testing
Before data collection, it is good to know whether indeed.co.uk html layout has changed (seems to be pretty stable compared to other job sites)
This repo includes a test suite to ensure everything is as expected - simply run the following:
```
pytest test/
```
## Parameter entry
If using for specific companies' employers, save your desired search terms in `companies_to_search.csv`
If using for non-specific sampling, save search terms in `control_search_terms.csv`

## Execution
```
python run.py
```

