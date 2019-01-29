import requests
import psycopg2
import json

#conn = psycopg2.connect(database='NHL', user='postgres', password='postgres', host='localhost', port='5432')
conn = psycopg2.connect("host=localhost dbname=stephen user=stephen password=stephen")

req = requests.get('http://www.nhl.com/stats/rest/skaters?isAggregate=false&reportType=basic&isGame=false&reportName=skatersummary&sort=[{%22property%22:%22playerName%22,%22direction%22:%22ASC%22},{%22property%22:%22goals%22,%22direction%22:%22DESC%22},{%22property%22:%22assists%22,%22direction%22:%22DESC%22}]&cayenneExp=gameTypeId=2%20and%20seasonId%3E=20172018%20and%20seasonId%3C=20172018') 

# data here is a list of dicts
data = req.json()['data']

cur = conn.cursor()
# create a table with one column of type JSON
cur.execute("CREATE TABLE t_skaters (data json);")

fields = [
    'seasonId',
    'playerName',
    'playerFirstName',
    'playerLastName',
    'playerId',
    'playerHeight',
    'playerPositionCode',
    'playerShootsCatches',
    'playerBirthCity',
    'playerBirthCountry',
    'playerBirthStateProvince',
    'playerBirthDate',
    'playerDraftYear',
    'playerDraftRoundNo',
    'playerDraftOverallPickNo'
]

for item in data:
    my_data = {field: item[field] for field in fields}
    cur.execute("INSERT INTO t_skaters VALUES (%s)", (json.dumps(my_data),))


# commit changes
conn.commit()
# Close the connection
conn.close()