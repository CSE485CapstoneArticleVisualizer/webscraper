import requests
from bs4 import BeautifulSoup, NavigableString
from utility import recursiveGetString, recursiveGetStringGivenList
import re

# Regex constants
author_pattern = r"([\w\s]+),?\s*"
author_regex = re.compile(author_pattern)
journal_pattern = r"[^-]*-\s(.*)"
journal_regex = re.compile(journal_pattern)
year_pattern = r"[^\d]*((?:20|19)\d\d)[^\d]*"
year_regex = re.compile(year_pattern)
citation_count_pattern = r"[^\d]*(\d*)[^\d]*"
citation_count_regex = re.compile(citation_count_pattern)

# Parse HTML and save it to a HTML file on disk
def getAndSaveFile():
  page = requests.get('https://scholar.google.com/scholar?hl=en&as_sdt=0%2C3&q=social+media&btnG=&oq=social')
  contents = page.content

  Html_file= open("google.html","w")
  Html_file.write(str(contents))
  Html_file.close()

  return contents 

contents = getAndSaveFile()

# Read a HTML file from disk
def readHTML(filename):
  Html_file= open("google.html","r")
  content = Html_file.read()
  Html_file.close()

  return content

###contents = readHTML("google.html")

# Initialize Beautiful Soup
soup = BeautifulSoup(contents, 'html.parser')


titles = soup.select('.gs_rt a')
authorLists = soup.select('.gs_a')

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
papers = soup.select('.gs_ri')
for paper in papers:
  # Title
  title = paper.select(".gs_rt a")
  print(recursiveGetStringGivenList(title))

  # Author/Journal/Year
  authors = paper.select(".gs_a")
  author_list, journal = getAuthorsAndJournal(authors)
  print("Authors: " + " ".join(author_list))
  print("Journal: " + journal)
  print("Year Published: " + getYearFromJournal(journal))
  
  # Abstract
  abstract = paper.select(".gs_rs")
  print("Abstract: " + recursiveGetStringGivenList(abstract))

  bottom_row_links = paper.select(".gs_fl a")
  citation_anchor = bottom_row_links[2]
  print("Citation Count: ", getCitationCount(citation_anchor.contents[0]))

  citations_link = citation_anchor['href'] # Index 2 is the cited by child
  print("Cited by: ", citations_link)
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
