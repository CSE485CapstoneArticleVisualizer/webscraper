import requests
from bs4 import BeautifulSoup, NavigableString
from utility import recursiveGetString, recursiveGetStringGivenList
from article import Article
import re
import time
import datetime
import atexit
import json
from pprint import pprint
from threading import Thread
import sys

from selenium import webdriver
from selenium.webdriver.firefox.options import Options  
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#driver = webdriver.Firefox()
options = Options()
options.set_headless(headless=True)
#options.add_argument("--disable-gpu")
driver = webdriver.Firefox(firefox_options=options)
reference_driver = webdriver.Firefox(firefox_options=options)

# Regex constants
author_pattern = r"([\w\s]+),?\s*"
author_regex = re.compile(author_pattern)
journal_pattern = r"[^-]*-\s(.*)"
journal_regex = re.compile(journal_pattern)
year_pattern = r"[^\d]*((?:20|19)\d\d)[^\d]*"
year_regex = re.compile(year_pattern)
citation_count_pattern = r"[^\d]*(\d+,?\d*)[^\d]*"
citation_count_regex = re.compile(citation_count_pattern)

# ------------------------------ Data 
# The articles that have been web scraped. Don't need to look at them again!
web_scraped_articles = set()

# Add to visited_pages after creating the json files for each paper on the page
visited_pages = set() 

# After finishing the current page remove the current page off the list and add the next page to the list
# When getting the citedBy papers, add each page to the visited_pages set
to_be_visited_pages = set()

data = None
try:
  with open('./visited_pages.json') as f:
    data = json.load(f)
    # pprint(data)
    visited_pages = set(data)

  with open('./to_be_visited_pages.json') as f:
    data = json.load(f)
    # pprint(data)
    to_be_visited_pages = set(data)

  with open('./web_scraped_articles.json') as f:
    data = json.load(f)
    # pprint(data)
    web_scraped_articles = set(data)

except FileNotFoundError:
  print("Error: Could not find visited_pages.json OR to_be_visited_pages.json OR web_scraped_articles.json in local directory.")
except:
  print("ERROR: An unknown error has occured while reading visited_pages.json OR to_be_visited_pages.json OR web_scraped_articles.json")

to_be_visited_pages.add("https://academic.microsoft.com/#/search?iq=And(Ty%3D'0'%2CRId%3D2165228770)&q=papers%20citing%20Social%20media%20and%20health%20care%20professionals%3A%20benefits%2C%20risks%2C%20and%20best%20practices.&filters=&from=0&sort=0")
to_be_visited_pages.add("https://academic.microsoft.com/#/search?iq=%40social%20media%40&q=social%20media&filters=&from=0&sort=0")
# ------------------------------



# Parse HTML and save it to a HTML file on disk
def getAndSaveFile():
  page = requests.get('https://academic.microsoft.com/#/search?iq=%40social%20media%40&q=social%20media&filters=&from=0&sort=0')
  contents = page.content

  Html_file= open("mc_ac.html","w")
  Html_file.write(str(contents))
  Html_file.close()

  return contents 

#contents = getAndSaveFile()

# Read a HTML file from disk
def readHTML(filename):
  Html_file= open("mc_ac.html","r")
  contents = Html_file.read()
  Html_file.close()

  return contents

###contents = readHTML("google.html")



# Parse the author string into a list of authors and the journal the article belongs to
def convertAuthorStringToList(author_list_string):
  author_list = []
  journal = ""
  result = author_regex.match(author_list_string)
  
  if result: # This if statement ensures there is at least one match
    start, end = 0, 0
    # Match all authors
    while (result):
      # Add the matched author to the list of authors
      author_list.append(result.groups(0)[0].strip())
      start, end = result.span()
      result = author_regex.match(author_list_string, end)

    # The remaining string is the journal
    journal_result = journal_regex.match(author_list_string, end)
    if (journal_result):
      journal = journal_result.groups(0)[0]
      #print("GROUPS: ", journal_result.groups())
    else:
      print("ERROR: No values matched to JOURNAL regex")

  else:
    print("ERROR: No values matched to AUTHOR regex")

  return author_list, journal

# Converts a list of author tags into a string. Passes string to converAuthorStringToList() function and recieves a list of authors and the journal
def getAuthorsAndJournal(authorList):
  new_author_list_string = ""

  # Loop through each author in the author list
  if not isinstance(authorList, list):
    authorList = authorList.contents

  for index, author in enumerate(authorList):

    str = author
    if not isinstance(author, NavigableString):
      str = recursiveGetString(author)
    
    new_author_list_string += (str)
  
  #print(newAuthorList)
  result = convertAuthorStringToList(new_author_list_string)
  #print("Author/Journal: " , result)
  return result

def getYearFromJournal(journal):
  result = year_regex.match(journal)
    
  if result: # This if statement ensures there is at least one match
    return result.groups(0)[0].strip()

  return "N/A"

def getCitationCount(citation_string):
  result = citation_count_regex.match(citation_string)
    
  if result: # This if statement ensures there is at least one match
    return result.groups(0)[0].strip()

  return "N/A"


def retrieveTitles(html):
  # Initialize Beautiful Soup for this page 
  soup = BeautifulSoup(html, 'html.parser')

  titles = set()
  ################### Per-paper web scraping
  papers = soup.select('paper-tile')
  for paper in papers:
    # Title
    title = paper.select(".paper-title span[data-bind]")
    title_str = recursiveGetStringGivenList(title)
    print("Title: " + title_str)
    titles.add(title_str)

  return titles

'''
  Simply retrieves the titles of the papers that cite the designated paper
'''
def getReferencesForPaper(webpage):
  references = set()
  print("\nLoading webpage in REFERENCE_DRIVER: " + webpage + "\n")
  reference_driver.get(webpage)
  # Wait for web page to load  
  loadWebPage(reference_driver, None)

  # Loop until no more reference pages
  more_pages = True
  while more_pages:
    more_pages = False
    time.sleep(2)

    # Retrieve info
    references = references.union(retrieveTitles(reference_driver.page_source))

    # Save current page to be fully looked at later
    future_link = reference_driver.current_url
    if future_link not in visited_pages:
      to_be_visited_pages.add(future_link)

    more_pages = pressNext(reference_driver)
    if not more_pages:
      print("Found end of references. Total Count: " + str(len(references)))

  return references

def pressNext(web_driver):
  # Check if the 'Next' button exists
  try:
    nextButton = web_driver.find_element(By.CSS_SELECTOR, '.pagination > li > a[aria-label="Next"]')
    if nextButton is not None:
      #driver.execute_script("document.querySelectorAll('.pagination > li:nth-child(8) > a:nth-child(1)')[0].click()")
      web_driver.execute_script("document.querySelectorAll('.pagination > li > a[aria-label=\"Next\"]')[0].click()")
      print("NEXT PAGE")
      loadWebPage(web_driver) 

      return True
      
  # No 'Next' button present
  except: 
    print("No next button found")

  return False

def loadWebPage(web_driver=driver, webpage=None):
  if webpage is not None:
    web_driver.get(webpage)

  attempt_count = 1
  max_attempts = 2
  while attempt_count != -1 and attempt_count <= max_attempts:
    try:
      elem = WebDriverWait(web_driver, 5).until(
          EC.presence_of_element_located((By.CSS_SELECTOR, '.content-main paper-tile'))
      )
      attempt_count = -1
      print("Dynamic Loading Completed")
    except:
      print("Failed to load page for attempt #" + str(attempt_count) + "/" + str(max_attempts+1) + "...")
      attempt_count += 1

      web_driver.refresh()
      continue
      

'''
  Retrieves all of the information for each paper on the page
'''
def retrieveInfoFromPage(webpage):
  loadWebPage(driver, webpage)
  print("\nLoading webpage in PRIMARY_DRIVER: " + webpage + "\n")

  # Initialize Beautiful Soup for this page 
  soup = BeautifulSoup(driver.page_source, 'html.parser')

  ################### Per-paper web scraping
  papers = soup.select('paper-tile')
  for paper in papers:
    # Title
    title = paper.select(".paper-title span[data-bind]")
    title_str = recursiveGetStringGivenList(title)
    print("Title: " + title_str)

    # If we have already web scraped this paper, skip it
    if title_str in web_scraped_articles:
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

    print("Authors: " + " ".join(authors))
    print("Associations: " + " ".join(associations))

    journal = paper.select(".paper-venue li a")
    journal_str = recursiveGetStringGivenList(journal)
    print("Journal: " + journal_str)

    #date = paper.select(".paper-date")
    #date_str = recursiveGetStringGivenList(date)
    date = paper.select(".paper-year span")
    date_str = 'Jan 1 0000'
    if len(date) > 0:
      date_str = date[0]['title']
      print("Date Published: " + date_str)
    
    # Abstract
    abstract = paper.select(".paper-abstract span")
    abstract_str = recursiveGetStringGivenList(abstract)
    print("Abstract: " + abstract_str)

    citationCount = paper.select(".paper-actions a.c-count span")
    
    citation_count_str = getCitationCount(recursiveGetStringGivenList(citationCount))
    print("Citation Count: " + citation_count_str)

    citations = paper.select(".paper-actions a.c-count")
    print('')

    # Generate and save the new article
    newArticle = Article(title=title_str, abstract=abstract_str, authors=authors, journal=journal_str, date=date_str, citationCount=citation_count_str)
    if len(citations) > 0:
      link = 'https://academic.microsoft.com/' + citations[0]['href']
      newArticle.citedBy = list(getReferencesForPaper(link))
      num_cited_by = len(newArticle.citedBy)
      newArticle.citedByCount = num_cited_by
      print("Found " + str(num_cited_by) + "/" + citation_count_str + " papers")
    newArticle.save()

    # Add this article to the web_scraped_articles set
    web_scraped_articles.add(title_str)
    print("\n\n-----------------------------------\n\n")

  # After web scraping all the articles on this page... Save next page to be looked at later
  pressNext(driver)
  future_link = driver.current_url
  if future_link not in visited_pages:
    to_be_visited_pages.add(future_link)
  #print("ADDED FUTURE LINK: " + future_link)
  driver.back()


def save_all_data():
  try:
    print('Saving visited_pages...')
    # Save visited_pages
    target = './visited_pages.json'

    with open(target, 'w') as outfile:
      json.dump(list(visited_pages), outfile, sort_keys=True, indent=4, separators=(',', ': '))

    print('Saving to_be_visited_pages...')

    # Save to_be_visited_pages
    target = './to_be_visited_pages.json'
    with open(target, 'w') as outfile:
      json.dump(list(to_be_visited_pages), outfile, sort_keys=True, indent=4, separators=(',', ': '))
    

    print('Saving web_scraped_articles...')

    # Save to_be_visited_pages
    target = './web_scraped_articles.json'
    with open(target, 'w') as outfile:
      json.dump(list(web_scraped_articles), outfile, sort_keys=True, indent=4, separators=(',', ': '))
    
  except:
    print("FATAL ERROR OCCURED: Failed to save files.")
    return False
  
  # Success!
  return True

def exit_handler():
  print('Application shutting down')

  save_all_data()
  
  timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
  print(timestamp)
  print("Program exit.")

def main():
  retry_attempt = 0
  page = None
  while to_be_visited_pages:
    try:
      page = to_be_visited_pages.pop()
      time.sleep(2)
      retrieveInfoFromPage(page)
      retry_attempt = 0

    except KeyboardInterrupt:
      to_be_visited_pages.add(page)
      global end_save_thread
      end_save_thread = True
      
      print("\n------------------------------------\nKeyboard Interrupt Detected")
      print("Exit Save Thread: " + str(end_save_thread))
      break
    except:
      print("Attempt: " + str(retry_attempt) + "/3")

      retry_attempt += 1
      global driver
      global reference_driver

      to_be_visited_pages.add(page)
      print("An error has occured while parsing this page: " + page)

      # After 3 reattempts, recreate the web drivers to make sure they aren't glitching out
      if retry_attempt > 3:
        retry_attempt = 0
        print("Recreating web drivers from scratch...")
        if driver is not None:
          driver.close()
          driver = None
        if reference_driver is not None:
          reference_driver.close()
          reference_driver = None

      # In the case that the web drivers closed on themselves, recreate them
      if driver is None:
        print("Creating primary driver...")
        driver = webdriver.Chrome()
      if reference_driver is None:
        print("Creating reference driver...")
        reference_driver = webdriver.Chrome()

end_save_thread = False
def save_every_x_minutes(minutes):
  while True:
    
    time.sleep(minutes*60)
    if not save_all_data():
      return

    if (end_save_thread):
      return

if __name__ == '__main__':
  atexit.register(exit_handler)
  #save_thread = Thread(target = save_every_x_minutes, args = (5, ))
  #save_thread.start()
  
  main()
