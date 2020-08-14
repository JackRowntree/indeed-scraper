import pandas as pd
import boto3
import time
from numpy import repeat
from classes.scraper import Scraper
from psycopg2.extensions import AsIs
from psycopg2 import connect
from json import loads

def upsert_totals(dict):
	"""upserts indeed total listings value
	using psycopg formatting"""
	sql = """
	    INSERT INTO
	        job_listings_totals
	    VALUES (
		TIMESTAMP '{date_scraped}',
		'{website}',
		'{country}',
		'{company_id}',
		'{company_name}',
		'{search_term}',		
		'{is_wagestream}',
		{total} 
	    )
	    ON CONFLICT ON CONSTRAINT site_job
	    DO UPDATE SET
	        total = {total}
	""".format(**dict)
	cursor.execute(sql)
	
def upsert_listing(dict):
	"""upserts indeed job metadata
	using psycopg formatting"""
	sql = u"""
	    INSERT INTO
	        job_listings_full
	      	(
		      	website,
		      	properties,
		      	jobid,
		      	date_scraped,
		      	search_term,
		      	country,
		      	jobtitle,
		      	is_wagestream,
		      	company_id,
		      	company_name
	      	)
	    VALUES (
			%s,
			%s::jsonb,
			%s,
			TIMESTAMP %s,
			%s,
			%s,
			%s,
			%s::boolean,
			%s,
			%s
	    )
	    ON CONFLICT ON CONSTRAINT site_job2
	    DO NOTHING
	"""
	cursor.execute(sql,tuple(dict.values()))
	
def get_company_data():
	"""extract target companies and run scraping"""
	company_data=pd.read_csv('companies_to_search.csv')
	#iterate over location and companies
	for location in locations:
		for search_term,company_id,company_name in company_data:
			company =  Scraper(None,'united kingdom',search_term=term)
			#scrape total and listing-granularity data
			indeed_totals,indeed_full = company.indeed_scrape()
			upsert_totals(indeed_totals)
			for entry in indeed_full:
				entry['company_id'] = company_id
				upsert_listing(entry)	
			#close chrome tab
			company.driver.quit()
				
def get_control_data():
	"""extract non-specific search terms and run scraping"""
	search_terms = pd.read_csv('control_search_terms.csv')
	for location in locations:
		for term in search_terms:
			control=Scraper(None,'united kingdom',search_term=term)
			#scrape listing granularity data
			indeed_control=control.indeed_scrape_control()
			for entry in indeed_control:
				entry['company_id'] = None
				entry['company_name'] = None
				upsert_listing(entry)	
			#close chrome tab
			control.driver.quit()

if __name__ == "__main__":
	#get db creds
	creds = loads(os.getenv('CREDS'))
	connection = connect(**creds)
	connection.autocommit = True
	cursor = connection.cursor()
	#set locations
	locations = ['united kingdom']
	get_company_data()
	get_control_data()



