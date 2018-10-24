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

    print("Thread successfully exit.")

  def __init__(self, data_source, logger, ID=0):

    logger.log("Initializing WebScraper #{0}...".format(ID))
    self.RESET_COUNT = 500
    self.loadCount = 0
    self.ID = ID
    self.logger = logger
    self.options = Options()
    self.options.add_argument("--headless")
    self.driver = webdriver.Firefox(firefox_options=self.options)
    self.data_source = data_source
    self.start()

  def start(self):
    total_attempts = 0
    retry_attempt = 0
    page = self.data_source.getPage()
    self.logger.log("Started scraper #{0}".format(self.ID), priority=Priority.HIGH)

    while page is not None and not Globals.end_threads:

      # Recreate drivers every 20 web scraping attempts (Prevent memory leak)
      total_attempts += 1
      if total_attempts == 20:
        self.recreateDrivers()
        total_attempts = 0

      # Attempt to read the information off of the pages
      try:
        time.sleep(1)
        self.retrieveInfoFromPage(page)
        self.logger.log("[Scraper #{0}] Successfully scraped page {1}".format(self.ID, page) , priority=Priority.DEBUG)

        retry_attempt = 0
        page = self.data_source.getPage()

      except KeyboardInterrupt:
        self.data_source.savePage(page)
        global end_save_thread
        end_save_thread = True
        
        self.logger.log("\n------------------------------------\nKeyboard Interrupt Detected", priority=Priority.CRITICAL)
        self.logger.log("[Scraper #{0}] Exit Save Thread: {1}".format(self.ID, end_save_thread), priority=Priority.CRITICAL)
        break
      except:
        self.logger.log("[Scraper #{0}] Page Scraping Attempt: {1}/3".format(self.ID, retry_attempt), priority=Priority.DEBUG)

        retry_attempt += 1

        self.data_source.savePage(page)
        self.logger.log("[Scraper #{0}] An error has occured while parsing this page: {1}".format(self.ID, page), priority=Priority.DEBUG)

        # After 3 reattempts, recreate the web drivers to make sure they aren't glitching out
        if retry_attempt > 3:
          retry_attempt = 0
          new_page = self.data_source.getPage()
          self.data_source.savePage(page)
          page = new_page
          self.recreateDrivers()

    self.logger.log("[Scraper #{0}] ERROR: No pages found... ".format(self.ID), priority=Priority.CRITICAL)
    try:
      self.exit_handler()
    except:
      self.logger.log("[Scraper #{0}] An error has occured while closing the driver".format(self.ID), priority=Priority.CRITICAL)

  def recreateDrivers(self):
    self.logger.log("[Scraper #{0}] Recreating web drivers from scratch...".format(self.ID), priority=Priority.CRITICAL)
    if self.driver is not None:
      self.driver.close()
      self.driver.quit()
      self.driver = None

    # In the case that the web drivers closed on themselves, recreate them
    if self.driver is None:
      self.logger.log("[Scraper #{0}] Creating primary driver...".format(self.ID), priority=Priority.CRITICAL)
      self.driver = webdriver.Firefox(firefox_options=self.options)




  '''
  Simply retrieves the titles of the papers that cite the designated paper
  '''
  def getReferencesForPaper(self, webpage):
    references = set()
    self.logger.log("\n[Scraper #{0}] Loading webpage in REFERENCE_DRIVER: {1}".format(self.ID, webpage), priority=Priority.HIGH)

    self.driver.get(webpage)
    #self.logger.log("\n[Scraper #{0}] CURRENT WEBPAGE: {1}".format(self.ID, self.driver.current_url), priority=Priority.HIGH)

    # Wait for web page to load  
    #@#######
    self.loadWebPage(self.driver, webpage=webpage)
    #self.logger.log("\n[Scraper #{0}] CURRENT WEBPAGE 2: {1}".format(self.ID, self.driver.current_url), priority=Priority.HIGH)
    
    # Loop until no more reference pages
    more_pages = True
    while more_pages:
      if Globals.end_threads:
        return None


      more_pages = False
      
      # Retrieve info
      #self.logger.log("\n[Scraper #{0}] CURRENT WEBPAGE 3: {1}".format(self.ID, self.driver.current_url), priority=Priority.HIGH)
      self.driver.refresh()
      time.sleep(2)
      #self.logger.log("\n[Scraper #{0}] CURRENT WEBPAGE 4: {1}".format(self.ID, self.driver.current_url), priority=Priority.HIGH)
      html = self.driver.page_source

      titles = self.retrieveTitles(html)
      self.logger.log("\n[Scraper #{0}] TITLES: {1}".format(self.ID, titles), priority=Priority.HIGH)

      references = references.union(titles)

      # Save current page to be fully looked at later
      future_link = self.driver.current_url

      if not self.data_source.alreadyVisitedPage(future_link):
        self.data_source.savePage(future_link)

      more_pages = self.pressNext(self.driver)
      if not more_pages:
        self.logger.log("[Scraper #{0}] Found end of references. Total Count: ".format(self.ID) + str(len(references)), priority=Priority.HIGH)

    self.logger.log("[Scraper #{0}] Found end of references: {1}".format(self.ID, references), priority=Priority.HIGH)
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
        self.logger.log("[Scraper #{0}] NEXT PAGE".format(self.ID), priority=Priority.DEBUG)
        self.loadWebPage(web_driver) 

        return True
        
    # No 'Next' button present
    except: 
      self.logger.log("No next button found", priority=Priority.DEBUG)

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
        _ = WebDriverWait(web_driver, 3).until(
            #EC.presence_of_element_located((By.CSS_SELECTOR, '.content-main section.paper-tile'))
            #EC.presence_of_element_located((By.CSS_SELECTOR, 'div.result-stats:nth-child(2)'))
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.result-stats'))
        )
        attempt_count = -1
        self.logger.log("[Scraper #{0}] Dynamic loading completed".format(self.ID), priority=Priority.LOW)
      except:
        self.logger.log(("[Scraper #{0}] Failed to load page for attempt #".format(self.ID)) + str(attempt_count) + "/" + str(max_attempts) + "...", priority=Priority.DEBUG)
        attempt_count += 1

        web_driver.refresh()
        time.sleep(2)
        continue
        

  '''
    Retrieves all of the information for each paper on the page
  '''
  def retrieveInfoFromPage(self, webpage):
    self.logger.log("\n[Scraper #{0}] Loading webpage in PRIMARY_DRIVER: ".format(self.ID) + webpage + "\n", priority=Priority.HIGH)

    self.loadWebPage(self.driver, webpage)

    # Initialize Beautiful Soup for this page 
    html = str(self.driver.page_source)
    soup = BeautifulSoup(html, 'html.parser')
    papers = soup.select('paper-tile')

    # keep track of the page being scraped
    current_page = self.driver.current_url

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
      self.logger.log("[Scraper #{0}] Title: ".format(self.ID) + title_str, priority=Priority.HIGH)

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

      self.logger.log("Authors: " + " ".join(authors))
      self.logger.log("Associations: " + " ".join(associations))

      journal = paper.select(".paper-venue li a")
      journal_str = recursiveGetStringGivenList(journal)
      self.logger.log("Journal: " + journal_str)

      #date = paper.select(".paper-date")
      #date_str = recursiveGetStringGivenList(date)
      date = paper.select(".paper-year span")
      date_str = 'Jan 1 0000'
      if len(date) > 0:
        date_str = date[0]['title']
        self.logger.log("Date Published: " + date_str)
      
      # Abstract
      abstract = paper.select(".paper-abstract span")
      abstract_str = recursiveGetStringGivenList(abstract)
      self.logger.log("Abstract: " + abstract_str)

      citationCount = paper.select(".paper-actions a.c-count span")
      
      citation_count_str = self.getCitationCount(recursiveGetStringGivenList(citationCount))
      self.logger.log("Citation Count: " + citation_count_str)

      citations = paper.select(".paper-actions a.c-count")
      self.logger.log('')

      # Generate and save the new article
      newArticle = Article(title=title_str, abstract=abstract_str, authors=authors, journal=journal_str, date=date_str, citationCount=citation_count_str)
      if len(citations) > 0:
        link = 'https://academic.microsoft.com/' + citations[0]['href']
        newArticle.citedBy = list(self.getReferencesForPaper(link))
        num_cited_by = len(newArticle.citedBy)
        newArticle.citedByCount = num_cited_by
        self.logger.log("Found " + str(num_cited_by) + "/" + citation_count_str + " papers")
      newArticle.save()

      # Add this article to the web_scraped_articles set
      self.data_source.saveScrapedArticle(title_str)

      self.logger.log("\n\n-----------------------------------\n\n")

    # Save the visited page
    self.data_source.saveVisitedPage(current_page)

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
      self.logger.log("Title: " + title_str)
      titles.add(title_str)

    return titles
