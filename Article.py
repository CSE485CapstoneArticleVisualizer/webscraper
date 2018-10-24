import json
import os
import datetime

class Article(object):
  
  def __init__(self, title="Temp Title", abstract="Temporary Abstract", authors=[], journal="N/A", date="N/A", citationCount="-1"):
    self.title = title
    self.abstract = abstract
    self.authors = authors
    self.journal = journal
    self.date = date
    self.citationCount = citationCount
    self.citedBy = []
    self.citedByCount = 0
    
  # def addCitedBy(self, paper):
  #   self.citedBy.add(paper)
  
  def save(self):
    #Create new directory if necessary
    directory = './Data/'
    if not os.path.exists(directory):
      os.makedirs(directory)

    directory = directory + datetime.datetime.today().strftime('%Y-%m-%d')
    if not os.path.exists(directory):
      os.makedirs(directory)
      
    filename = self.date + '--' + self.title
    whitelist = set('abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ-0123456789')
    filtered_filename = ''.join(filter(whitelist.__contains__, filename))
    target =  directory + '/' + filtered_filename + '.json'

    with open(target, 'w') as outfile:
      json.dump(self.__dict__, outfile, sort_keys=True, indent=4, separators=(',', ': '))

      print("Saved " + self.title + " to " + target)
