# indeed-scraper
Some handy scripts to scrape indeed job listing metadata.

## Installation
To use, run the following in `../indeed_scraper/` to create you virtual environment:
```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## Parameter entry
If using for specific companies' employers, save your desired search terms in `companies_to_search.csv`
If using for non-specific sampling, save search terms in `control_search_terms.csv`

# Execution
```
python run.py
```

