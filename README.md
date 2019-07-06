# webscraper
## Requirements
python3
pip3
geckodriver
firefox

## Packages
bs4
selenium
psutil


## Usage
Navigate to the folder:
```
cd ...
```
Set the environment:
```
source ./env/Scripts/activate
```
Run the program:
```
python3 ScrapeMicrosoftAcademic.py
```

## Editing the .env
You can edit various aspects of the *.env* file to change how the program works. For instance you can set the number of threads or webscrapers to 10 if you want to webscrape faster:
```
NUM_THREADS = 5
```

You can also choose what kind of messages the program will log to the screen (more details in Logging section):
``` 
DEBUG_ENABLED = "off"
LOW_ENABLED = "off"
NORMAL_ENABLED = "on"
HIGH_ENABLED = "on"
CRITICAL_ENABLED = "on"
ARTICLE_DETAILS_ENABLED = "off" # Print out details about the social media article after it has been web-scraped.
```

In-case you are running out of memory, you can set ```DATA_SOURCE_MAX_PAGE_COUNT_IN_MEM``` to a smaller number. This is the max number of URLs that the program will store in memory before writing the pages to memory. The program will write all but ```DATA_SOURCE_RETRIEVE_PAGE_COUNT``` pages out to disk. You can enable ```DATA_SOURCE_LOGGING_ENABLED``` by setting it to **"on"** if you wish to see data logging.

Here is an example:
```
DATA_SOURCE_MAX_PAGE_COUNT_IN_MEM = 750
DATA_SOURCE_RETRIEVE_PAGE_COUNT = 250
DATA_SOURCE_LOGGING_ENABLED = "off"
```


## LOGGING
Below is are the messages that will be printed out if **LOW**, **NORMAL**, **HIGH**, or **CRITICAL** logs are enabled.

### DEBUG Priority List - (Normal to experience these issues.)
*  "[Scraper #{0}] Page Scraping Attempt FAILED: {1}/3.... {2}"
*  "[Scraper #{0}] An error has occured while parsing this page: {1}\n{2}"
*  "[Scraper #{0}] Failed to load page for attempt #{1}/{2}..."

### LOW Priority List - (Unsuprising messages that aren't very important and may be highly repetitive.)
*  "Started scraper #{0}"
*  "[Scraper #{0}] [Attempt {1}/{2}] Waiting for page to become available..."
*  "[Scraper #{0}] Found end of references: {1}"
*  "[Scraper #{0}] FOUND NEXT PAGE"
*  "[Scraper #{0}] No next button found:{1}"
*  "[Scraper #{0}] Dynamic loading completed"
*  "\n[Scraper #{0}] Loading webpage in PRIMARY_DRIVER: {1}\n"

### NORMAL Priority List - (Typical expected operations. Not as repetitive as other operations.)
*  "[Scraper #{0}] Successfully scraped page {1}"
*  "[Scraper #{0}] Recreating web drivers from scratch..."
*  "[Scraper #{0}] Creating primary driver..."
*  "\n[Scraper #{0}] Loading webpage in REFERENCE_DRIVER: {1}"
*  "[Scraper #{0}] Attempting to find next page..."
*  "[Scraper #{0}] Found end of references. Total Count: {1}"
*  "[Scraper #{0}] Retrieving information on paper with Title: {1}"

### HIGH Priority List - (Did not expect this to occur, but not vital to program.)
*  "[Scraper #{0}] ERROR: No pages found in the last 5 minutes! The thread will now be closing "

### CRITICAL Priority List - (These have large impact to program operation.)
*  "\n------------------------------------\nKeyboard Interrupt Detected"
*  "[Scraper #{0}] Exit Save Thread: {1}"
*  "Successfully closed scraper #{0}"
*  "[Scraper #{0}] An error has occured while closing the driver:\n{1}"
*  "[Scraper #{0}] An error has occured while reopening the primary driver:\n{1}"

## WARNING 
Closing the program may leave dangling references to the geckodriver. In order to prevent a memory leak, make sure to teminate them.
*This seams to only be an issue on Windows. Ubuntu handles this issue and closes and threads.*
Run this on Windows to close all Firefox instances:
```
Taskkill /IM firefox.exe /F
```

## ISSUES
It appears as though even if it says that 85 papers cited **The (R) Evolution of social media in software engineering**, Microsoft Academic only provides 53 of these papers.
https://academic.microsoft.com/#/detail/2141271901


