# webscraper

<h2>Requirements</h2>
python3
pip3
geckodriver
firefox

<h2>Packages</h2>
bs4
selenium
psutil


<h2>Usage</h2>
Naviagate to the folder <code>cd ...</code><br>
Set the environment: <code>source ./env/Scripts/activate</code><br>
Run the program <code>python3 WebScrapeMicrosoftAcademic.py</code><br>

<h2>WARNING</h2>
Closing the program may leave dangling references to the geckodriver. In order to prevent a memory leak, make sure to teminate them.<br>
Run this on Windows to close all Firefox instances:<br>
<code>Taskkill /IM firefox.exe /F</code>