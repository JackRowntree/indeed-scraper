import re 
import json
import time
import random
from selenium import webdriver,common
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime
from bs4 import BeautifulSoup
from urllib3.exceptions import ProtocolError,MaxRetryError
from numpy import ceil
from scraper.scraper import ScrapeCompany
import pytest


@pytest.fixture(scope='session')
def scraper():
	scraper = ScrapeCompany()
	scraper.driver.get('https://www.indeed.co.uk/?sq=1')
	yield scraper
	scraper.driver.quit()

@pytest.fixture(scope='session')
def is_displayed(scraper,term,element=None):
	def is_disp(scraper,term,element=None):
		element = element or scraper.driver
		return scraper.driver.find_element_by_css_selector(term).is_displayed()
	return is_disp
 
@pytest.fixture(scope='session')
def listing(scraper):
	listing = scraper.driver.find_element_by_css_selector('#resultsCol .jobsearch-SerpJobCard')
	return listing

@pytest.mark.parametrize("css_selec", ['#text-input-what,#what','#text-input-where,#where','.icl-WhatWhere-button,.input_submit'])
def test_search_term_input(is_displayed):
	assert is_displayed(css_selec)

def test_search_results(scraper,is_displayed):
	scraper.driver.get('https://www.indeed.co.uk/jobs?q=example&l=')
	assert is_displayed('#searchCountPages')

#run test for each listing type parameter
@pytest.mark.parametrize("listing", ['.jobtitle','.date','.company'])
def test_listing_jobtitle(scraper,is_displayed,listing):
	listing = listing()
	assert is_displayed('.jobtitle', element = listing)


