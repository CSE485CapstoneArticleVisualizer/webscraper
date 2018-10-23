from enum import Enum
class Priority(Enum):
  DEBUG = 1
  LOW = 2
  NORMAL = 3
  HIGH = 4
  CRITICAL = 5


class WebScraperLogger():
  logging_enabled = True

  def __init__(self):
    print("Logger initialized")

  def log(self, X, priority=Priority.NORMAL):
    if self.logging_enabled:
      if priority.value != Priority.NORMAL.value:
        print(X)
      # if priority.value >= Priority.HIGH.value:
      #   print(X)