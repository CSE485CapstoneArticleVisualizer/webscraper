import settings
import json
import threading
from collections import deque
import os 
import time

class WebScraperDataSource():
  
  '''
  DATA_SOURCE_MAX_PAGE_COUNT_IN_MEM is the max number of pages in the to_be_visited_pages set before saving the contents to disk 
  DATA_SOURCE_RETRIEVE_PAGE_COUNT is the number of to_be_visited_pages to keep in memory (save the rest to disk)
  '''

  def log(self, X):
    if self.DATA_SOURCE_LOGGING_ENABLED:
      print(X)

  def __init__(self):

    self.DATA_SOURCE_MAX_PAGE_COUNT_IN_MEM = int(os.getenv("DATA_SOURCE_MAX_PAGE_COUNT_IN_MEM"))
    self.DATA_SOURCE_RETRIEVE_PAGE_COUNT = int(os.getenv("DATA_SOURCE_RETRIEVE_PAGE_COUNT"))
    self.DATA_SOURCE_LOGGING_ENABLED = (os.getenv("DATA_SOURCE_LOGGING_ENABLED") == "on")

    # ------------------------------ Data 
    # The articles that have been web scraped. Don't need to look at them again!
    self.web_scraped_articles = set()
    self.lock_web_scraped_articles = threading.RLock()

    # Add to visited_pages after creating the json files for each paper on the page
    self.visited_pages = set() 
    self.lock_visited_pages = threading.RLock()

    # After finishing the current page remove the current page off the list and add the next page to the list
    # When getting the citedBy papers, add each page to the visited_pages set
    self.to_be_visited_pages = set()
    self.lock_to_be_visited_pages = threading.RLock()
    # ------------------------------ END Data 

    # Create to_be_visited_pages if it does not exist
    if not os.path.exists('./to_be_visited_pages.txt'):
      target = './to_be_visited_pages.txt'
      with open(target, 'w') as outfile:
        outfile.write("")

    data = None
    try:
      with open('./visited_pages.json') as f:
        data = json.load(f)
        # pprint(data)
        self.visited_pages = set(data)

      self.retrieveToBeVisitedFromDisk(DATA_SOURCE_RETRIEVE_PAGE_COUNT)
        
      with open('./web_scraped_articles.json') as f:
        data = json.load(f)
        # pprint(data)
        self.web_scraped_articles = set(data)

    except FileNotFoundError:
      self.log("Non-Fatal Error: Could not find visited_pages.json OR to_be_visited_pages.json OR web_scraped_articles.json in local directory.")
    except:
      self.log("ERROR: An unknown error has occured while reading visited_pages.json OR to_be_visited_pages.json OR web_scraped_articles.json")

    self.to_be_visited_pages.add("https://academic.microsoft.com/#/search?iq=And(Ty%3D'0'%2CRId%3D2165228770)&q=papers%20citing%20Social%20media%20and%20health%20care%20professionals%3A%20benefits%2C%20risks%2C%20and%20best%20practices.&filters=&from=0&sort=0")
    self.to_be_visited_pages.add("https://academic.microsoft.com/#/search?iq=%40social%20media%40&q=social%20media&filters=&from=0&sort=0")

  def save_all_data(self):
    try:
      self.log()
      self.log('Saving visited_pages: ' + str(len(self.visited_pages)))
      # Save visited_pages
      target = './visited_pages.json'

      with open(target, 'w') as outfile:
        json.dump(list(self.visited_pages), outfile, sort_keys=True, indent=4, separators=(',', ': '))

      self.log('Saving to_be_visited_pages: ' + str(len(self.to_be_visited_pages)))

      # Save to_be_visited_pages
      target = './to_be_visited_pages.txt'
      with open(target, 'a') as outfile:
        #json.dump(list(to_be_visited_pages), outfile, sort_keys=True, indent=4, separators=(',', ': '))
        for page in self.to_be_visited_pages:
          outfile.write("%s\n" % page.rstrip())

      
      self.log('Saving web_scraped_articles: ' + str(len(self.web_scraped_articles)))
      self.log()
      # Save to_be_visited_pages
      target = './web_scraped_articles.json'
      with open(target, 'w') as outfile:
        json.dump(list(self.web_scraped_articles), outfile, sort_keys=True, indent=4, separators=(',', ': '))
      
    except:
      self.log("FATAL ERROR OCCURED: Failed to save files.")
      return False
    
    # Success!
    return True

  #------------------------------------------ GETTERS and SETTERS


  def getPage(self):
    self.lock_to_be_visited_pages.acquire()
    page = None
    #print("Before pop: " + str(len(self.to_be_visited_pages)))
    if len(self.to_be_visited_pages) > 0:
      page = self.to_be_visited_pages.pop().rstrip()
    else:
      if len(self.retrieveToBeVisitedFromDisk(self.DATA_SOURCE_RETRIEVE_PAGE_COUNT)) > 0:
        page = self.to_be_visited_pages.pop().rstrip()
        
    #print("After pop: " + str(len(self.to_be_visited_pages)))

    self.lock_to_be_visited_pages.release()
    return page
  
  def savePage(self, page):
    self.lock_to_be_visited_pages.acquire()
    self.to_be_visited_pages.add(page)

    if len(self.to_be_visited_pages) >= self.DATA_SOURCE_MAX_PAGE_COUNT_IN_MEM:
      self.saveToBeVisitedToDisk(self.DATA_SOURCE_RETRIEVE_PAGE_COUNT)
    self.log("\n[DATA SOURCE] Saved future page " + str(len(self.to_be_visited_pages)) + "\n")
    self.lock_to_be_visited_pages.release()

  def saveVisitedPage(self, page):
    self.lock_visited_pages.acquire()
    self.visited_pages.add(page)
    self.lock_visited_pages.release()
  
  def alreadyVisitedPage(self, page):
    self.lock_visited_pages.acquire()
    already_visited = False
    if page in self.visited_pages:
      already_visited = True
    self.lock_visited_pages.release()
    return already_visited

  def saveScrapedArticle(self, article):
    self.log("\n[DATA SOURCE] Webscraped an article!\n")
    self.lock_web_scraped_articles.acquire()
    self.web_scraped_articles.add(article)
    self.lock_web_scraped_articles.release()
  
  def alreadyScrapedArticle(self, article):
    self.lock_web_scraped_articles.acquire()

    already_scraped = False
    if article in self.web_scraped_articles:
      already_scraped = True
      self.log("\n[DATA SOURCE] Non-Fatal Error: Already scraped article {0}\n".format(article))

    self.lock_web_scraped_articles.release()
    return already_scraped

  #------------------------------------------ END GETTERS and SETTERS


  def saveToBeVisitedToDisk(self, DATA_SOURCE_RETRIEVE_PAGE_COUNT=100):
    self.log("\n\n[DATA SOURCE] SAVING %d to_be_visited_pages TO DISK\n\n" % DATA_SOURCE_RETRIEVE_PAGE_COUNT)

    self.lock_to_be_visited_pages.acquire()
    DATA_SOURCE_RETRIEVE_PAGE_COUNT_set = set()
    self.log("Before write to disk: " + str(len(self.to_be_visited_pages)))

    if len(self.to_be_visited_pages) <= DATA_SOURCE_RETRIEVE_PAGE_COUNT:
      self.lock_to_be_visited_pages.release()
      return
    else:
      for _ in range(DATA_SOURCE_RETRIEVE_PAGE_COUNT):
        DATA_SOURCE_RETRIEVE_PAGE_COUNT_set.add(self.to_be_visited_pages.pop())
        

    # Save to_be_visited_pages
    try:
      target = './to_be_visited_pages.txt'
      with open(target, 'a') as outfile:
        #json.dump(list(to_be_visited_pages), outfile, sort_keys=True, indent=4, separators=(',', ': '))
        for page in self.to_be_visited_pages:
          outfile.write("%s\n" % page.rstrip())
            
      # Retain X pages
      self.to_be_visited_pages = DATA_SOURCE_RETRIEVE_PAGE_COUNT_set
      self.log("After write to disk: " + str(len(self.to_be_visited_pages)))
    except Exception as e:
      self.log("EXCEPTION HAS OCCURED WHILE OPENING FILE ./to_be_visited_pages.txt\n{}".format(e))
      
    self.lock_to_be_visited_pages.release()

  def retrieveToBeVisitedFromDisk(self, X=100):
    self.log("\n\n[DATA SOURCE] RETRIEVING %d to_be_visited_pages FROM DISK" % X)
    self.lock_to_be_visited_pages.acquire()
    self.log("Size before read from disk: " + str(len(self.to_be_visited_pages)))

    try:
      # Retreive the last X lines
      lastX = set()
      with open('./to_be_visited_pages.txt') as fin:
        temp = deque(fin, X)
        lastX = set(temp)
        self.log("Retrieved " + str(len(temp)) + " lines")
        self.to_be_visited_pages = self.to_be_visited_pages.union(lastX)

      # Delete the last X lines
      file = open('./to_be_visited_pages.txt', "r+", encoding = "utf-8")

      for _ in range(X):
        # Move the pointer (similar to a cursor in a text editor) to the end of the file. 
        file.seek(0, os.SEEK_END)

        # This code means the following code skips the very last character in the file - 
        # i.e. in the case the last line is null we delete the last line 
        # and the penultimate one
        pos = file.tell() - 1

        # Read each character in the file one at a time from the penultimate 
        # character going backwards, searching for a newline character
        # If we find a new line, exit the search
        while pos > 0 and file.read(1) != "\n":
          pos -= 1
          file.seek(pos, os.SEEK_SET)

        # So long as we're not at the start of the file, delete all the characters ahead of this position
        if pos >= 0:
          file.seek(pos, os.SEEK_SET)
          file.truncate()
        else:
          break

      file.close()
      self.log("Size after read from disk: " + str(len(self.to_be_visited_pages)) + "\n\n")
    except Exception as e:
      self.log("EXCEPTION HAS OCCURED WHILE OPENING FILE ./to_be_visited_pages.txt\n{}".format(e))

    self.lock_to_be_visited_pages.release()

    return lastX
