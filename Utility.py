from bs4 import NavigableString

def recursiveGetString(tag):
    s = ""
    for c in tag.contents:
      if not isinstance(c, NavigableString):
        s += recursiveGetString(c)
      else:
        s += c

    return s

def recursiveGetStringGivenList(list):
    s = ""
    for c in list:
      if not isinstance(c, NavigableString):
        s += recursiveGetString(c)
      else:
        s += c

    return s
