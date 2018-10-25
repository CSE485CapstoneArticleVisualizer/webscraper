import settings
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
import os
import psutil

# Regex constants
# author_pattern = r"([\w\s]+),?\s*"
# author_regex = re.compile(author_pattern)
# journal_pattern = r"[^-]*-\s(.*)"
# journal_regex = re.compile(journal_pattern)
# year_pattern = r"[^\d]*((?:20|19)\d\d)[^\d]*"
# year_regex = re.compile(year_pattern)
DEFAULT_NUM_THREADS = int(os.getenv("NUM_THREADS"))

def exit_handler():
  print('\n\nApplication shutting down...')

  global data_source
  data_source.save_all_data()
  
  timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
  print(timestamp)
  print("Program exit.")
  print("MAKE SURE TO KILL ALL FIREFOX INSTANCES FROM THE TERMINAL IF THE DRIVER FAILED TO BE KILLED. OTHERWISE THERE WILL BE A MEMORY LEAK.")

def create_scraper(ID):
  global data_source
  global logger
  time.sleep(3)
  WebScraper(data_source, logger, ID)

def signal_handler(sig, frame):
  print('You pressed Ctrl+C!')
  Globals.end_threads = True
  print('Globals.end_threads: {0}'.format(Globals.end_threads))
  print('\nPLEASE WAIT WHILE THE THREADS CLOSE...\n\n')

  global threads
  #for thread in threads:
    #print('Joining thread ' + str(thread))
    #if thread.isAlive():
      #thread.join()

  PROCNAME = "geckodriver" # or chromedriver or IEDriverServer
  for proc in psutil.process_iter():
      # check whether the process name matches
      if proc.name() == PROCNAME:
          proc.kill()

  sys.exit(0)




def main():

  
  
  global data_source
  data_source = WebScraperDataSource()
  global logger
  logger = WebScraperLogger()
  if len(sys.argv) > 2:
    arg = str(sys.argv[2]).lower()
    if arg == "false" or arg == "f":
      logger.logging_enabled = False
    else:
      logger.logging_enabled = True

  global num_threads
  if len(sys.argv) > 1:
    num_threads = int(sys.argv[1])
  else:
    num_threads = DEFAULT_NUM_THREADS

  global threads
  threads = []
  for n in range(num_threads):
    time.sleep(1)
    thread = Thread(target = create_scraper, args = (n+1, ))
    threads.append(thread)
    thread.start()
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

  #save_thread = Thread(target = save_every_x_minutes, args = (5, ))
  #save_thread.start()
  
  main()
  while True:
    time.sleep(1)
  print("End Main")
