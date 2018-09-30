import json

class Article:

  def __init__(self, title="Temp Title", abstract="Temporary Abstract", author="N/A"):
    self.title = title
    self.abstract = abstract
    self.author = author
    self.tricks = []    # creates a new empty list for each dog

  def add_trick(self, trick):
    self.tricks.append(trick)

  def toJSON(self, file):
    print("TODO: write to JSON file")

  def fromJSON(self, json):
    print("TODO")
