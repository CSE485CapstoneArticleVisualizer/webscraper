# TODO: Compare journals stored in database with those stored in csv file provided by Az
# TODO: Reveal what journals exist in database that don't exist in csv file
# TODO: Reveal what journals exist in the csv file that don't exist in the database

# SELECT * FROM journals

# import python csv module to read csv's. 
# Read csv and retrieve all journals from
# Check:
# -which journals are in both csv and database
# -Which are just in csv
# -Which are just in database

# Ask Stephen what he wants to do with the journals just in database and just in csv
# Idea for csv only journals: Go to Microsoft Academic and scrape articles for each csv journal

import csv
import psycopg2

def getCSVJournals():
    journalArray = []
    with open('categories.csv', encoding='utf8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='|')

        for row in csv_reader:
            if len(row) == 4:
                journalArray.append(row[3])
            print(row)
    return journalArray


def getDatabaseJournals():
    cur.execute("""SELECT J.name 
                    FROM journals J""", ())
    return cur.fetchall()

if __name__ == "__main__":
    conn = psycopg2.connect("host=localhost port=5434 dbname=stephen user=stephen password=stephen")
    cur = conn.cursor()

    databaseJournals = getDatabaseJournals()
    csvJournals = getCSVJournals()

    print(databaseJournals)
    print(csvJournals)