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

class ScrapeCompany:
   'Common base class for scraper'
   #class attribute to ensure that employer data is not re-scraped
   employers_scraped=[]
   def __init__(self, name,location,search_term=None,):

      self.manual=False
      if search_term:
         self.search_term = search_term
         self.manual=True
      elif name:
         self.search_term = name.replace('\'','')
      else:
         self.search_term = None

      #headerless browsing
      options = webdriver.ChromeOptions()
      options.add_argument("headless")
      self.driver = webdriver.Chrome('/usr/local/bin/chromedriver',chrome_options=chrome_options)
      
      self.location = location
      self.jobs_totals = []
      self.full_jobs_data = []
      self.indeed_base_url = 'https://www.indeed.co.uk/?sq=1'
      self.page_size = 50

   def indeed_search(self,term):
      """interacts with the indeed search inputs, catches some common indeed-bot gotchas"""
      #search term
      try:
         self.driver.find_element_by_css_selector('#text-input-what,#what').clear()
         self.driver.find_element_by_css_selector('#text-input-what,#what').send_keys(term)
      except (
         common.exceptions.StaleElementReferenceException,
         ProtocolError
         ) as e:
         try:
            self.driver.get(self.indeed_base_url)
         except MaxRetryError:
            time.sleep(3)
            self.driver.get(self.indeed_base_url)
         self.driver.find_element_by_css_selector('#text-input-what,#what').clear()
         self.driver.find_element_by_css_selector('#text-input-what,#what').send_keys(term)
      #location
      self.driver.find_element_by_css_selector('#text-input-where,#where').clear()
      self.driver.find_element_by_css_selector('#text-input-where,#where').send_keys(self.location)
      #click
      self.safeclick('.icl-WhatWhere-button,.input_submit')

   def safeclick(self,selector):
      #tries to click, gets round popups if unsuccessful
      #click
      try:
         self.driver.find_element_by_css_selector(selector).click()
      #escape and click
      except common.exceptions.ElementClickInterceptedException as e:
         actions = ActionChains(self.driver)
         actions.send_keys(Keys.ESCAPE)
         actions.perform()
         self.driver.find_element_by_css_selector(selector).click()

   def indeed_scrape(self):
      """runs the scraping scripts sequentially,
      protocol for companies of interest"""
      #get total listings data
      self.driver.get(self.indeed_base_url)
      self.get_indeed_totals()
      self.all_total = self.jobs_totals[0]['total']
      self.get_indeed_totals(append=True)
      self.ws_total = self.jobs_totals[1]['total']
      self.mode = 'clients'
      #get full listing data
      self.get_indeed_full()
      self.driver.quit()
      return self.jobs_totals, self.full_jobs_data

   def indeed_scrape_control(self):
      """runs the scraping scripts sequentially,
      protocol for control companies/jobs"""\
      #get total listings data
      self.driver.get(self.indeed_base_url)
      self.get_indeed_totals()
      self.all_total = self.jobs_totals[0]['total']
      #max out at 1000
      if self.all_total > 1000:
         self.all_total = 1000
      self.mode = 'control'
      self.is_ws = None
      #get full listing data
      self.iter_scrape(self.all_total)
      self.driver.quit()
      return self.full_jobs_data

   def indeed_extract_total(self):
      """extracts the summary info from indeed search result"""
      try:
         text=self.driver.find_element_by_id('searchCountPages').get_attribute('innerHTML')
         return int(
         re.search('((?<=of ).+(?= jobs))',text)
         .group(1)
         .replace(',','')
         )
      except common.exceptions.NoSuchElementException:
         return 0

   def indeed_gen_search_term(self):
      """makes search term fit with indeed search logic"""
      search =self.search_term
      terms=False
      if self.search_term.contains('|'):
         terms = [x.strip() for x in self.search_term.split('|')]
         search = terms[0]
      output = 'company:(' + search + ')'
      if terms:
         output += (' ' + terms+1)

   def get_indeed_totals(self, append=False):
      """scrapes the summmary info of indeed search"""
      job_total={}
      job_total['is_wagestream'] = 0
      job_total['search_term'] = self.search_term
      job_total['date_scraped'] = datetime.now()
      job_total['country'] = self.location
      job_total['date_scraped'] = datetime.now().strftime("%Y-%m-%d")
      job_total['website'] = 'indeed'

      search_term = self.search_term
      if not self.manual:
         search_term = 'company:(' + self.search_term + ')'
      if append:
         job_total['is_wagestream'] = 1
         if self.all_total == 0:
            job_total['total'] = 0
            self.jobs_totals.append(job_total)
            return
         search_term += ' wagestream'

      self.indeed_search(search_term)
      job_total['total'] = self.indeed_extract_total()     
      self.jobs_totals.append(job_total)

   def get_indeed_full(self):
      """runs the scraping of indeed job tables and iterations thereof"""
      if self.all_total == 0:
         return
      search_2 = 'company:(' + self.search_term + ') -wagestream'
      self.is_ws = 1
      self.iter_scrape(self.ws_total)
      self.is_ws = 0
      self.indeed_search(search_2)
      self.iter_scrape(self.all_total - self.ws_total)
      return self.full_jobs_data

   def get_n_reviews(self,job):
      """interacts with listing to get html to show"""
      try:
         job.click()
      except common.exceptions.ElementClickInterceptedException as e:
         pass
      try:
         text=WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".slNoUnderline"))).text
      except common.exceptions.TimeoutException:
         text=None
      return(text)
   def indeed_scrape_jobs_table(self):
      """scrapes through one page of glassdoor job table"""
      #check if there is something to scrape

      #scrape the full jobs table
      jobs_table = self.driver.find_elements_by_css_selector('#resultsCol .jobsearch-SerpJobCard')
      if len(jobs_table) == 0:
         return False
      #scrape all the listings within table
      for job in jobs_table:
         jobinfo = {'website':'indeed','properties':{}}
         #get stars rating
         try:
            jobinfo['properties']['rating'] = float(job.find_element_by_class_name('ratingsContent').text)
         except common.exceptions.NoSuchElementException as e:
            jobinfo['properties']['rating'] = None
         except ValueError:
            jobinfo['properties']['rating'] = None
         jobinfo['jobid'] = job.get_attribute('id')
         jobinfo['date_scraped'] = datetime.now().strftime("%Y-%m-%d")
         jobinfo['search_term'] = self.search_term
         jobinfo['country'] = self.location
         jobinfo['jobtitle']= job.find_element_by_class_name('jobtitle').text
         jobinfo['properties']['posted_at']= job.find_element_by_css_selector('.date').text
         #get salary if exists
         try:
            salary = job.find_element_by_css_selector('.salaryText').text
            jobinfo['properties']['salary'] = salary
         except common.exceptions.NoSuchElementException as e:
            jobinfo['properties']['salary'] = None
         #get employer name and number of reviews
         if self.manual:
            employer=job.find_element_by_class_name('company').text
            jobinfo['properties']['employer'] = employer
            if employer not in self.employers_scraped:
               self.employers_scraped.append(employer)
               jobinfo['properties']['reviews'] = self.get_n_reviews(job)
         else:
            #has employer info already been scraped
            if self.search_term not in self.employers_scraped:
               self.employers_scraped.append(self.search_term)
               jobinfo['properties']['reviews'] = self.get_n_reviews(job)
         jobinfo['properties'] = json.dumps(jobinfo['properties'])
         jobinfo['is_wagestream'] = self.is_ws
         self.full_jobs_data.append(jobinfo)
      return True

   def random_scrape(self):
      """this method randomly selects pages of search results """
      url = self.driver.current_url + '&limit=50&filter=0'
      self.driver.get(url)
      #injectable url for iteration
      newurl=self.driver.current_url+'&start={start}'
      #keep randomly scraping until hit max listins
      max = ceil(self.all_total/50)
      total = self.all_total
      i=0
      while (i * self.page_size) < total:
         start = random.randint(1,max)*50
         self.driver.get(newurl.format(start=start))
         valid = self.indeed_scrape_jobs_table()
         i+=1

   def iter_scrape(self,total):
      """this method loops through pages of jobs tables"""
      #determines if there is naything to scrape
      if self.mode =='clients':
         if (
            (self.is_ws == 1 and self.ws_total == 0)
            or 
            (self.is_ws == 0 and self.ws_total == self.all_total)
            ):
            return
      i=1
      #start scraping with this urk
      url = self.driver.current_url + '&limit=50&filter=0'
      self.driver.get(url)
      #sometimes indeed tries anti-bot popups
      try:
         WebDriverWait(self.driver, 1).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".icl-CloseButton.popover-x-button-close"))).click()
      except common.exceptions.TimeoutException:
         pass
      #did the first page return anything
      valid = self.indeed_scrape_jobs_table()
      #new injectable url for iteration
      newurl=self.driver.current_url+'&start={start}'
      #loop through pages until hit max listungs
      while valid and (i * self.page_size) < total:
         start = i*self.page_size
         self.driver.get(newurl.format(start=start))
         valid = self.indeed_scrape_jobs_table()
         i+=1

   