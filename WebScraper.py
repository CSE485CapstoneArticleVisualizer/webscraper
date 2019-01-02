from WebScraperDataSource import WebScraperDataSource
from bs4 import BeautifulSoup, NavigableString
from Utility import recursiveGetString, recursiveGetStringGivenList
from Article import Article
from WebScraperLogger import WebScraperLogger
from WebScraperLogger import Priority
import time
import re
import Globals
import signal
import sys 

from selenium import webdriver
from selenium.webdriver.firefox.options import Options  
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class WebScraper():
  citation_count_pattern = r"[^\d]*(\d+,?\d*)[^\d]*"
  citation_count_regex = re.compile(citation_count_pattern)

  def exit_handler(self):
    print('Thread #{0} closing...'.format(self.ID))

    if self.driver is not None:
      self.driver.close()
      self.driver.quit()
      self.driver = None

    sys.exit(0)

    print("Thread successfully exit.")

  def __init__(self, data_source, logger, ID=0):

    logger.log("Initializing WebScraper #{0}...".format(ID))
    self.ARTICLE_RESET_COUNT = 20 # After X articles
    self.RESET_COUNT = 500 # After loading 500 webpages reset
    self.MAX_CITATION_COUNT = 5000
    self.loadCount = 0
    self.ID = ID
    self.logger = logger
    self.options = Options()
    self.options.add_argument("--headless")
    self.driver = webdriver.Firefox(firefox_options=self.options)
    self.data_source = data_source
    self.start()

  def start(self):
    total_attempts = 0 # Number of attempts across multiple pages
    retry_attempt = 0 # Number of attempts for 1 page

    # Made for initial startup when there aren't enough pages available for each web scraper
    wait_count = 0
    max_wait_count = 10
    wait_sleep = 30

    page = self.data_source.getPage()
    self.logger.log("Started scraper #{0}".format(self.ID), priority=Priority.HIGH)

    while ((page is not None and page != "") or wait_count < max_wait_count) and not Globals.end_threads:
      # If a page wasn't currently available, sleep for a minute and try again
      if page is None:
        wait_count += 1
        self.logger.log("[Scraper #{0}] [Attempt {1}/{2}] Waiting for page to become available...".format(self.ID, wait_count, max_wait_count), priority=Priority.LOW)

        time.sleep(wait_sleep)
        page = self.data_source.getPage()
        continue

      wait_count = 0 # A page was made available
      # Recreate drivers every 20 web scraping attempts (Prevent memory leak)
      total_attempts += 1
      if total_attempts >= self.ARTICLE_RESET_COUNT:
        self.recreateDrivers()
        total_attempts = 0

      # Attempt to read the information off of the pages
      try:
        time.sleep(1)
        self.retrieveInfoFromPage(page)
        self.logger.log("[Scraper #{0}] Successfully scraped page {1}".format(self.ID, page) , priority=Priority.NORMAL)
        # Save the visited page
        self.data_source.saveVisitedPage(page)

        retry_attempt = 0
        page = self.data_source.getPage()

      except KeyboardInterrupt:
        self.data_source.savePage(page)
        global end_save_thread
        end_save_thread = True
        
        self.logger.log("\n------------------------------------\nKeyboard Interrupt Detected", priority=Priority.CRITICAL)
        self.logger.log("[Scraper #{0}] Exit Save Thread: {1}".format(self.ID, end_save_thread), priority=Priority.CRITICAL)
        break
      except Exception as e:
        self.logger.log("[Scraper #{0}] Page Scraping Attempt FAILED: {1}/3.... {2}".format(self.ID, retry_attempt, str(e)), priority=Priority.DEBUG)

        retry_attempt += 1

        self.data_source.savePage(page)
        self.logger.log("[Scraper #{0}] An error has occured while parsing this page: {1}\n{2}".format(self.ID, page, str(e)), priority=Priority.DEBUG)

        # After 3 reattempts, recreate the web drivers to make sure they aren't glitching out
        if retry_attempt > 3:
          retry_attempt = 0
          page = self.data_source.getPage()
          self.recreateDrivers()
    #### END WHILE LOOP ####

    self.logger.log("[Scraper #{0}] ERROR: No pages found in the last 5 minutes! The thread will now be closing ".format(self.ID), priority=Priority.HIGH)
    try:
      self.exit_handler()
      self.logger.log("Successfully closed scraper #{0}".format(self.ID), priority=Priority.CRITICAL)

    except Exception as e:
      self.logger.log("[Scraper #{0}] An error has occured while closing the driver:\n{1}".format(self.ID, str(e)), priority=Priority.CRITICAL)
      sys.exit(666)

  def recreateDrivers(self):
    self.logger.log("[Scraper #{0}] Recreating web drivers from scratch...".format(self.ID), priority=Priority.NORMAL)
    if self.driver is not None:
      self.driver.close()
      self.driver.quit()
      self.driver = None

    time.sleep(0.5)
    # In the case that the web drivers closed on themselves, recreate them
    #if self.driver is None:
    try:
      self.logger.log("[Scraper #{0}] Creating primary driver...".format(self.ID), priority=Priority.NORMAL)
      self.driver = webdriver.Firefox(firefox_options=self.options)
    except Exception as e:
      self.logger.log("[Scraper #{0}] An error has occured while reopening the primary driver:\n{1}".format(self.ID, str(e)), priority=Priority.CRITICAL)
      self.recreateDrivers()

  '''
  Simply retrieves the titles of the papers that cite the designated paper
  '''
  def getReferencesForPaper(self, webpage, expected_count):
    references = set()

    self.logger.log("\n[Scraper #{0}] Loading webpage in REFERENCE_DRIVER: {1}".format(self.ID, webpage), priority=Priority.NORMAL)

    self.driver.get(webpage)
    #self.logger.log("\n[Scraper #{0}] CURRENT WEBPAGE: {1}".format(self.ID, self.driver.current_url), priority=Priority.NORMAL)

    # Wait for web page to load  
    #@#######
    self.loadWebPage(self.driver, webpage=webpage)
    #self.logger.log("\n[Scraper #{0}] CURRENT WEBPAGE 2: {1}".format(self.ID, self.driver.current_url), priority=Priority.NORMAL)
    
    # Loop until no more reference pages
    more_pages = True
    while more_pages and len(references) < self.MAX_CITATION_COUNT:
      if Globals.end_threads:
        return None
      self.logger.log("[Scraper #{0}] Found next page...".format(self.ID), priority=Priority.NORMAL)

      more_pages = False
      
      # Retrieve info
      #self.logger.log("\n[Scraper #{0}] CURRENT WEBPAGE 3: {1}".format(self.ID, self.driver.current_url), priority=Priority.NORMAL)
      self.driver.refresh()
      time.sleep(1)
      #self.logger.log("\n[Scraper #{0}] CURRENT WEBPAGE 4: {1}".format(self.ID, self.driver.current_url), priority=Priority.NORMAL)
      html = self.driver.page_source

      titles = self.retrieveTitles(html)

      references = references.union(titles)

      # Save current page to be fully looked at later
      future_link = self.driver.current_url

      if not self.data_source.alreadyVisitedPage(future_link):
        #self.logger.log("[Scraper #{0}] Saving page for later {1}: ".format(self.ID, future_link), priority=Priority.LOW)
        self.data_source.savePage(future_link)

      self.logger.log("[Scraper #{0}] Attempting to find next page... Current reference count: {1}/{2}... MAX {3}".format(self.ID, len(references), expected_count, self.MAX_CITATION_COUNT), priority=Priority.NORMAL)
      more_pages = self.pressNext(self.driver)

    self.logger.log("[Scraper #{0}] Found end of references. Total Count: {1}".format(self.ID, len(references)), priority=Priority.NORMAL)
    return references

  def pressNext(self, web_driver):
    if Globals.end_threads:
      return False
    # Check if the 'Next' button exists
    try:
      nextButton = web_driver.find_element(By.CSS_SELECTOR, '.pagination > li > a[aria-label="Next"]')
      if nextButton is not None:
        #driver.execute_script("document.querySelectorAll('.pagination > li:nth-child(8) > a:nth-child(1)')[0].click()")
        web_driver.execute_script("document.querySelectorAll('.pagination > li > a[aria-label=\"Next\"]')[0].click()")
        self.logger.log("[Scraper #{0}] FOUND NEXT PAGE".format(self.ID), priority=Priority.LOW)
        self.loadWebPage(web_driver) 

        return True
        
    # No 'Next' button present
    except Exception as e: 
      self.logger.log("[Scraper #{0}] No next button found:{1}".format(self.ID, str(e)), priority=Priority.LOW)

    return False

  def loadWebPage(self, web_driver = None, webpage=None):
    self.loadCount += 1

    time.sleep(1)
    if web_driver is None:
      web_driver = self.driver

    if self.loadCount >= self.RESET_COUNT:
      if webpage is None:
        webpage = web_driver.current_url
      self.recreateDrivers()
      self.loadCount = 0

    if webpage is not None:
      web_driver.get(webpage)

    #self.logger.log("[Scraper #{0}] Loading webpage {1}... ".format(self.ID, web_driver.current_url), priority=Priority.LOW)

    attempt_count = 1
    max_attempts = 2
    while attempt_count != -1 and attempt_count <= max_attempts and not Globals.end_threads:
      try:
        _ = WebDriverWait(web_driver, 2).until(
            #EC.presence_of_element_located((By.CSS_SELECTOR, '.content-main section.paper-tile'))
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.result-stats:nth-child(2)'))
            #EC.presence_of_element_located((By.CSS_SELECTOR, 'div.result-stats'))
        )
        attempt_count = -1
        self.logger.log("[Scraper #{0}] Dynamic loading completed".format(self.ID), priority=Priority.LOW)
      except Exception as e:
        self.logger.log(("[Scraper #{0}] Failed to load page for attempt #{1}/{2}...".format(self.ID, str(attempt_count), str(max_attempts))), priority=Priority.DEBUG)
        attempt_count += 1

        web_driver.refresh()
        time.sleep(1)
        continue
        
  def castStringToInt(self, string):
    try:
      return int(string.replace(',',''))
    except Exception as e:
      print("Exception occured while casting string {} to int: {}".format(string, e))
      return -1

  '''
    Retrieves all of the information for each paper on the page
  '''
  def retrieveInfoFromPage(self, webpage):
    if webpage is None:
      return None

    self.logger.log("\n[Scraper #{0}] Loading webpage in PRIMARY_DRIVER: {1}\n".format(self.ID, webpage), priority=Priority.NORMAL)

    self.loadWebPage(self.driver, webpage)

    # Initialize Beautiful Soup for this page 
    html = str(self.driver.page_source)
    soup = BeautifulSoup(html, 'html.parser')
    papers = soup.select('paper-tile')

    # Before web scraping all the articles on this page... Save next page to be looked at later
    if self.pressNext(self.driver):
      future_link = self.driver.current_url

      if not self.data_source.alreadyVisitedPage(future_link):
        self.data_source.savePage(future_link)

      #self.logger.log("ADDED FUTURE LINK: " + future_link)
      self.driver.back()

    ################### Per-paper web scraping
    for paper in papers:
      if Globals.end_threads:
        return None

      # Title
      title = paper.select(".paper-title span[data-bind]")
      title_str = recursiveGetStringGivenList(title)
      self.logger.log("[Scraper #{0}] Retrieving information on paper with Title: {1}".format(self.ID, title_str), priority=Priority.NORMAL)

      # If we have already web scraped this paper, skip it
      if self.data_source.alreadyScrapedArticle(title_str):
        continue

      # Author/Journal/Year
      authors_list = paper.select(".paper-authors")
      authors = []
      associations = []
      for author in authors_list:
        #author_list, journal = getAuthorsAndJournal(authors)
        x = author.select("a.button-link")
        if len(x) > 0:
          authors.append(recursiveGetString(x[0]))
        if len(x) > 1:
          associations.append(recursiveGetString(x[1]))

      self.logger.log("Authors: " + " ".join(authors), priority=Priority.ARTICLE_DETAILS)
      self.logger.log("Associations: " + " ".join(associations), priority=Priority.ARTICLE_DETAILS)

      journal = paper.select(".paper-venue li a")
      journal_str = recursiveGetStringGivenList(journal)
      self.logger.log("Journal: " + journal_str, priority=Priority.ARTICLE_DETAILS)

      #date = paper.select(".paper-date")
      #date_str = recursiveGetStringGivenList(date)
      date = paper.select(".paper-year span")
      date_str = 'Jan 1 0000'
      if len(date) > 0:
        date_str = date[0]['title']
        self.logger.log("Date Published: " + date_str, priority=Priority.ARTICLE_DETAILS)
      
      # Abstract
      abstract = paper.select(".paper-abstract span")
      abstract_str = recursiveGetStringGivenList(abstract)
      self.logger.log("Abstract: " + abstract_str, priority=Priority.ARTICLE_DETAILS)

      citationCount = paper.select(".paper-actions a.c-count span")
      
      citation_count_str = self.getCitationCount(recursiveGetStringGivenList(citationCount))
      self.logger.log("Citation Count: " + citation_count_str, priority=Priority.ARTICLE_DETAILS)

      citations = paper.select(".paper-actions a.c-count")
      self.logger.log('', priority=Priority.ARTICLE_DETAILS)








      # Generate and save the new article
      newArticle = Article(title=title_str, abstract=abstract_str, authors=authors, journal=journal_str, date=date_str, citationCount=citation_count_str)
      
      #--------------------------------------------------------------------------- Paper References 
      paper_anchor = paper.select(".paper-title a")
      try:
        #print("[Scraper #{0}] CURRENT DRIVER LOCATION 1: ".format(self.ID) + self.driver.current_url)
        link = 'https://academic.microsoft.com/' + paper_anchor[0]['href']
        self.driver.get(link)
        #print("[Scraper #{0}] CURRENT DRIVER LOCATION 2: ".format(self.ID) + self.driver.current_url)

        attempt_count = 1
        max_attempts = 2
        while attempt_count != -1 and attempt_count <= max_attempts and not Globals.end_threads:
          try:
            elem = WebDriverWait(self.driver, 2).until(
              EC.presence_of_element_located((By.CSS_SELECTOR, 'div.pure-u-md-4-24:nth-child(1) > a:nth-child(2)'))
              #EC.presence_of_element_located((By.CSS_SELECTOR, 'ma-ulist.ulist-paper:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(3) > a:nth-child(1)'))
              
            )
            reference_count_elem = WebDriverWait(self.driver, 1).until(
              EC.presence_of_element_located((By.CSS_SELECTOR, 'div.pure-u-md-4-24:nth-child(1) > h1:nth-child(1)'))
              #EC.presence_of_element_located((By.CSS_SELECTOR, 'ma-ulist.ulist-paper:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(3) > a:nth-child(1)'))
            )
            newArticle.referenceCount = self.getCitationCount(reference_count_elem.text)

            if elem is not None:
              #self.logger.log("[Scraper #{0}] CLICKED ON REFERENCE".format(self.ID), priority=Priority.DEBUG)
              self.driver.execute_script("document.querySelectorAll('div.pure-u-md-4-24:nth-child(1) > a:nth-child(2)')[0].click()")
              #time.sleep(2)
              self.loadWebPage(self.driver) 
              #time.sleep(2)
              #self.logger.log("[Scraper #{0}] SUCCESSFULLY LOADED REFERENCE".format(self.ID), priority=Priority.DEBUG)
              #print("[Scraper #{0}] CURRENT DRIVER LOCATION 3: ".format(self.ID) + self.driver.current_url)

              link = self.driver.current_url

              newArticle.cites = list(self.getReferencesForPaper(link, expected_count=self.castStringToInt(newArticle.referenceCount)))
              newArticle.citesCount = len(newArticle.cites)
              #self.logger.log("[Scraper #{0}] -> Reference Page -> Dynamic loading completed -> Reference Start Page: {1}".format(self.ID, link), priority=Priority.LOW)
              self.logger.log("[Scraper #{0}] Found {1}/{2} 'cites' papers".format(self.ID, newArticle.citesCount, newArticle.referenceCount), priority=Priority.HIGH)

            attempt_count = -1
          except Exception as e:
            self.logger.log(("[Scraper #{0}] -> Reference Page -> Failed to load page for attempt #".format(self.ID)) + str(attempt_count) + "/" + str(max_attempts) + "...\n" + str(e), priority=Priority.DEBUG)
            attempt_count += 1

            self.driver.refresh()
            time.sleep(1)
            continue

      except Exception as e:
        self.logger.log(("[Scraper #{0}] Failed to load primary page for paper:\n{1}").format(self.ID, str(e)), priority=Priority.CRITICAL)



      #--------------------------------------------------------------------------- Paper CitedBy
      if len(citations) > 0:
        link = 'https://academic.microsoft.com/' + citations[0]['href']
        newArticle.citedBy = list(self.getReferencesForPaper(link, expected_count=self.castStringToInt(citation_count_str)))
        num_cited_by = len(newArticle.citedBy)
        newArticle.citedByCount = num_cited_by
        self.logger.log("[Scraper #{0}] Found {1}/{2} 'citedBy' papers".format(self.ID, num_cited_by, citation_count_str), priority=Priority.HIGH)
      
      #--------------------------------------------------------------------------- END Paper CitedBy 

      newArticle.save()




      # Add this article to the web_scraped_articles set
      self.data_source.saveScrapedArticle(title_str)

      self.logger.log("\n\n----------------------------------------------------------------------\n\n", priority=Priority.NORMAL)

  def getCitationCount(self, citation_string):
    
    result = self.citation_count_regex.match(citation_string)
      
    if result: # This if statement ensures there is at least one match
      return result.groups(0)[0].strip()

    return "N/A"

  def retrieveTitles(self, html):

    # Initialize Beautiful Soup for this page 
    soup = BeautifulSoup(html, 'html.parser')

    titles = set()
    ################### Per-paper web scraping
    papers = soup.select('paper-tile')
    for paper in papers:
      # Title
      title = paper.select(".paper-title span[data-bind]")
      title_str = recursiveGetStringGivenList(title)
      self.logger.log("[Scraper #{0}] Retrieved Title: {1}".format(self.ID, title_str), priority=Priority.LOW)
      titles.add(title_str)

    #self.logger.log("\n[Scraper #{0}] TITLES: {1}", priority=Priority.NORMAL)

    return titles
