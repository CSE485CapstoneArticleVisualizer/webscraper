import settings
import os 
from enum import Enum
import datetime

class Priority(Enum):
  DEBUG = 1
  LOW = 2
  NORMAL = 3
  HIGH = 4
  CRITICAL = 5
  ARTICLE_DETAILS = 6

class WebScraperLogger():
  logging_enabled = True

  def __init__(self):
    self.DEBUG_ENABLED = (os.getenv("DEBUG_ENABLED") == "on")
    self.LOW_ENABLED = (os.getenv("LOW_ENABLED") == "on")
    self.NORMAL_ENABLED = (os.getenv("NORMAL_ENABLED") == "on")
    self.HIGH_ENABLED = (os.getenv("HIGH_ENABLED") == "on")  
    self.CRITICAL_ENABLED = (os.getenv("CRITICAL_ENABLED") == "on")
    self.ARTICLE_DETAILS_ENABLED = (os.getenv("ARTICLE_DETAILS_ENABLED") == "on")
    
    print("------------------------------------------------------------------")
    print("Logger initialized")
    print("DEBUG ENABLED: {0}".format(self.DEBUG_ENABLED))
    print("LOW_ENABLED: {0}".format(self.LOW_ENABLED))
    print("NORMAL_ENABLED: {0}".format(self.NORMAL_ENABLED))
    print("HIGH_ENABLED: {0}".format(self.HIGH_ENABLED))
    print("CRITICAL_ENABLED: {0}".format(self.CRITICAL_ENABLED))
    print("ARTICLE_DETAILS_ENABLED: {0}".format(self.ARTICLE_DETAILS_ENABLED))
    print("------------------------------------------------------------------")
  def log(self, filename, message, priority=Priority.NORMAL):
    # Save to_be_visited_pages
    save_to_file = False
    if save_to_file and priority.value > Priority.NORMAL.value and priority.value != Priority.ARTICLE_DETAILS.value:
      target = './{}'.format(filename)
      with open(target, 'a') as outfile:
        outfile.write("%s %s\n" % (datetime.datetime.now().strftime("[%I:%M%p on %B %d, %Y]"), message))
        
    if self.logging_enabled:
      if self.DEBUG_ENABLED and priority.value == Priority.DEBUG.value:
        print(message)
      elif self.LOW_ENABLED and priority.value == Priority.LOW.value:
        print(message)
      elif self.NORMAL_ENABLED and priority.value == Priority.NORMAL.value:
        print(message)
      elif self.HIGH_ENABLED and priority.value == Priority.HIGH.value:
        print(message)
      elif self.CRITICAL_ENABLED and priority.value == Priority.CRITICAL.value:
        print(message)
      elif self.ARTICLE_DETAILS_ENABLED and priority.value == Priority.ARTICLE_DETAILS.value:
        print(message)
      