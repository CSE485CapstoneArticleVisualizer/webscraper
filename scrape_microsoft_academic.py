import requests
from bs4 import BeautifulSoup, NavigableString
from utility import recursiveGetString, recursiveGetStringGivenList
import re


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#driver = webdriver.Firefox()
driver = webdriver.Chrome()
driver.get("https://academic.microsoft.com/#/search?iq=%40social%20media%40&q=social%20media&filters=&from=0&sort=0")

try:
  elem = WebDriverWait(driver, 30).until(
      EC.presence_of_element_located((By.XPATH, '//*[@id="isrcWrapper"]/div[4]/article[1]/div[3]/section[2]/div/paper-tile[1]/article/section[1]/h2/a/span[2]'))
  )
finally:
  #driver.quit()
  print("Dynamic Loading Completed")
  #print(driver.page_source)

# def x():
#   title_elems = driver.find_elements_by_xpath("//paper-tile")
#   print("papers = " + str(len(title_elems)))
#   for elem in title_elems:
#   title = elem.text
#   print(title)

import pickle

# # write python dict to a file
# mydict = {'a': 1, 'b': 2, 'c': 3}
# output = open('myfile.pkl', 'wb')
# pickle.dump(mydict, output)
# output.close()

# # read python dict back from the file
# pkl_file = open('myfile.pkl', 'rb')
# mydict2 = pickle.load(pkl_file)
# pkl_file.close()

# print mydict
# print mydict2

# Regex constants
author_pattern = r"([\w\s]+),?\s*"
author_regex = re.compile(author_pattern)
journal_pattern = r"[^-]*-\s(.*)"
journal_regex = re.compile(journal_pattern)
year_pattern = r"[^\d]*((?:20|19)\d\d)[^\d]*"
year_regex = re.compile(year_pattern)
citation_count_pattern = r"[^\d]*(\d+,?\d*)[^\d]*"
citation_count_regex = re.compile(citation_count_pattern)

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

# Initialize Beautiful Soup
soup = BeautifulSoup(driver.page_source, 'html.parser')

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

################### Per-paper web scraping
papers = soup.select('paper-tile')
for paper in papers:
  # Title
  title = paper.select(".paper-title span[data-bind]")
  print("Title: " + recursiveGetStringGivenList(title))

  # Author/Journal/Year
  authors_list = paper.select(".paper-authors")
  authors = []
  associations = []
  for author in authors_list:
    #author_list, journal = getAuthorsAndJournal(authors)
    x = author.select("a.button-link")
    authors.append(recursiveGetString(x[0]))
    associations.append(recursiveGetString(x[1]))

  print("Authors: " + " ".join(authors))
  print("Assocaitions: " + " ".join(associations))

  journal = paper.select(".paper-venue li a")
  print("Journal: " + recursiveGetStringGivenList(journal))

  date = paper.select(".paper-date")
  print("Date Published: " + recursiveGetStringGivenList(date))
  
  # Abstract
  abstract = paper.select(".paper-abstract span")
  print("Abstract: " + recursiveGetStringGivenList(abstract))

  citations = paper.select(".paper-actions a.c-count span")
  print("Citation Count: ", getCitationCount(recursiveGetStringGivenList(citations)))

  # citations_link = citation_anchor['href'] # Index 2 is the cited by child
  # print("Cited by: ", citations_link)
  print("\n\n-----------------------------------\n\n")


# Scrape authors from microsoft academic?
# paper_page = requests.get('https://scholar.google.com/scholar?hl=en&as_sdt=0%2C3&q=social+media&btnG=&oq=social')

####################
     

'''
def getTitles():
  for title in titles:
    final_string = recursiveGetString(title)
    print(final_string)

#getTitles()
#getAuthorsAndJournal()
''' 

# !!!!!!!!!! Things to keep track of
# Link currently visiting
# List of links to visit (such as the 'next' page) 