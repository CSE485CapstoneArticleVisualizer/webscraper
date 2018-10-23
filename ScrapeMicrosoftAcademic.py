import signal
import sys
import time
import datetime
import atexit
from WebScraperDataSource import WebScraperDataSource
from WebScraper import WebScraper
from threading import Thread
from multiprocessing import Process
from WebScraperLogger import WebScraperLogger
import Globals

# Regex constants
# author_pattern = r"([\w\s]+),?\s*"
# author_regex = re.compile(author_pattern)
# journal_pattern = r"[^-]*-\s(.*)"
# journal_regex = re.compile(journal_pattern)
# year_pattern = r"[^\d]*((?:20|19)\d\d)[^\d]*"
# year_regex = re.compile(year_pattern)


def exit_handler():
  print('Application shutting down...')

  global data_source
  data_source.save_all_data()
  
  timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
  print(timestamp)
  print("Program exit.")

def create_scraper(ID):
  global data_source
  global logger
  time.sleep(3)
  WebScraper(data_source, logger, ID)

def signal_handler(sig, frame):
  Globals.end_threads = True
  print('You pressed Ctrl+C!')
  sys.exit(0)


def main():
  global data_source
  data_source = WebScraperDataSource()
  global logger
  logger = WebScraperLogger()

  global num_threads
  for n in range(num_threads):
    Thread(target = create_scraper, args = (n+1, )).start()
    print("Created thread #" + str(n+1))
  

def save_every_x_minutes(minutes):
  global data_source
  while True:
    
    time.sleep(minutes*60)
    if not data_source.save_all_data():
      return

    if (Globals.end_threads):
      return

if __name__ == '__main__':
  atexit.register(exit_handler)
  signal.signal(signal.SIGINT, signal_handler)

  global num_threads
  num_threads = 7
  #save_thread = Thread(target = save_every_x_minutes, args = (5, ))
  #save_thread.start()
  
  main()
  print("End Main")
