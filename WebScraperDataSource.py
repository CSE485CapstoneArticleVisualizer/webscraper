import json
import threading
from collections import deque
import os 

class WebScraperDataSource():
  
  # ------------------------------ Data 
  # The articles that have been web scraped. Don't need to look at them again!
  web_scraped_articles = set()
  lock_web_scraped_articles = threading.RLock()

  # Add to visited_pages after creating the json files for each paper on the page
  visited_pages = set() 
  lock_visited_pages = threading.RLock()

  # After finishing the current page remove the current page off the list and add the next page to the list
  # When getting the citedBy papers, add each page to the visited_pages set
  to_be_visited_pages = set()
  lock_to_be_visited_pages = threading.RLock()

  '''
  saveToDiskIndex is the max number of pages in the to_be_visited_pages set before saving the contents to disk 
  retain is the number of to_be_visited_pages to keep in memory (save the rest to disk)
  '''
  def __init__(self, saveToDiskIndex = 750, retain = 250):
    self.saveToDiskIndex = saveToDiskIndex
    self.retain = retain 

    data = None
    try:
      with open('./visited_pages.json') as f:
        data = json.load(f)
        # pprint(data)
        self.visited_pages = set(data)

      self.retrieveToBeVisitedFromDisk(retain)
        
      with open('./web_scraped_articles.json') as f:
        data = json.load(f)
        # pprint(data)
        self.web_scraped_articles = set(data)

    except FileNotFoundError:
      print("Non-Fatal Error: Could not find visited_pages.json OR to_be_visited_pages.json OR web_scraped_articles.json in local directory.")
    except:
      print("ERROR: An unknown error has occured while reading visited_pages.json OR to_be_visited_pages.json OR web_scraped_articles.json")

    self.to_be_visited_pages.add("https://academic.microsoft.com/#/search?iq=And(Ty%3D'0'%2CRId%3D2165228770)&q=papers%20citing%20Social%20media%20and%20health%20care%20professionals%3A%20benefits%2C%20risks%2C%20and%20best%20practices.&filters=&from=0&sort=0")
    self.to_be_visited_pages.add("https://academic.microsoft.com/#/search?iq=%40social%20media%40&q=social%20media&filters=&from=0&sort=0")

  def save_all_data(self):
    try:
      print('Saving visited_pages...')
      # Save visited_pages
      target = './visited_pages.json'

      with open(target, 'w') as outfile:
        json.dump(list(self.visited_pages), outfile, sort_keys=True, indent=4, separators=(',', ': '))

      print('Saving to_be_visited_pages...')

      # Save to_be_visited_pages
      target = './to_be_visited_pages.txt'
      with open(target, 'a') as outfile:
        #json.dump(list(to_be_visited_pages), outfile, sort_keys=True, indent=4, separators=(',', ': '))
        for page in self.to_be_visited_pages:
          outfile.write("%s\n" % page)

      print('Saving web_scraped_articles...')

      # Save to_be_visited_pages
      target = './web_scraped_articles.json'
      with open(target, 'w') as outfile:
        json.dump(list(self.web_scraped_articles), outfile, sort_keys=True, indent=4, separators=(',', ': '))
      
    except:
      print("FATAL ERROR OCCURED: Failed to save files.")
      return False
    
    # Success!
    return True

  #------------------------------------------ GETTERS and SETTERS


  def getPage(self):
    self.lock_to_be_visited_pages.acquire()
    page = None
    #print("Before pop: " + str(len(self.to_be_visited_pages)))
    if len(self.to_be_visited_pages) > 0:
      page = self.to_be_visited_pages.pop()
    else:
      if len(self.retrieveToBeVisitedFromDisk(self.retain)) > 0:
        page = self.to_be_visited_pages.pop()
        
    #print("After pop: " + str(len(self.to_be_visited_pages)))

    self.lock_to_be_visited_pages.release()
    return page
  
  def savePage(self, page):
    self.lock_to_be_visited_pages.acquire()
    self.to_be_visited_pages.add(page)

    if len(self.to_be_visited_pages) >= self.saveToDiskIndex:
      self.saveToBeVisitedToDisk(self.retain)

    self.lock_to_be_visited_pages.release()

  def saveVisitedPage(self, page):
    self.lock_visited_pages.acquire()
    self.visited_pages.add(page)
    self.lock_visited_pages.release()
  
  def alreadyVisitedPage(self, page):
    self.lock_visited_pages.acquire()
    already_visited = (page in self.visited_pages)
    self.lock_visited_pages.release()
    return already_visited

  def saveScrapedArticle(self, article):
    self.lock_web_scraped_articles.acquire()
    self.web_scraped_articles.add(article)
    self.lock_web_scraped_articles.release()
  
  def alreadyScrapedArticle(self, article):
    self.lock_web_scraped_articles.acquire()
    already_scraped = (article in self.web_scraped_articles)
    self.lock_web_scraped_articles.release()
    return already_scraped

  #------------------------------------------ END GETTERS and SETTERS


  def saveToBeVisitedToDisk(self, retain=100):
    print("\n\nSAVING %d to_be_visited_pages TO DISK\n\n" % retain)

    self.lock_to_be_visited_pages.acquire()
    retain_set = set()
    print("Before write to disk: " + str(len(self.to_be_visited_pages)))

    if len(self.to_be_visited_pages) <= retain:
      self.lock_to_be_visited_pages.release()
      return
    else:
      for _ in range(retain):
        retain_set.add(self.to_be_visited_pages.pop())
        

    # Save to_be_visited_pages
    target = './to_be_visited_pages.txt'
    with open(target, 'a') as outfile:
      #json.dump(list(to_be_visited_pages), outfile, sort_keys=True, indent=4, separators=(',', ': '))
      for page in self.to_be_visited_pages:
        outfile.write("%s\n" % page)
          
    # Retain X pages
    self.to_be_visited_pages = retain_set
    print("After write to disk: " + str(len(self.to_be_visited_pages)))

    self.lock_to_be_visited_pages.release()

  def retrieveToBeVisitedFromDisk(self, X=100):
    print("\n\nRETRIEVING %d to_be_visited_pages FROM DISK\n\n" % X)
    self.lock_to_be_visited_pages.acquire()
    print("Before read from disk: " + str(len(self.to_be_visited_pages)))

    # Retreive the last X lines
    lastX = set()
    with open('./to_be_visited_pages.txt') as fin:
      lastX = set(deque(fin, X))
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
    print("After read from disk: " + str(len(self.to_be_visited_pages)))

    self.lock_to_be_visited_pages.release()

    return lastX
