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
    return journalArray


def getDatabaseJournals():
    cur.execute("""SELECT J.name 
                    FROM journals J""", ())
    return [row[0] for row in cur.fetchall()]


if __name__ == "__main__":
    conn = psycopg2.connect(
        "host=localhost port=5434 dbname=stephen user=stephen password=stephen")
    cur = conn.cursor()

    databaseJournals = getDatabaseJournals()
    print(databaseJournals[0])
    csvJournals = getCSVJournals()

    databaseJournals = set([journal.lower() for journal in databaseJournals])
    csvJournals = set([journal.lower() for journal in csvJournals])

    inDatabaseNotCSV = databaseJournals - csvJournals
    inCSVnotDatabase = csvJournals - databaseJournals

    print("Journals in Database: " + str(len(databaseJournals)))
    print("Journals in CSV: " + str(len(csvJournals)))
    print("-"*50)
    print("Journals in Database and not in CSV: " + str(len(inDatabaseNotCSV)))
    print("Journals in CSV and not in Database: " + str(len(inCSVnotDatabase)))
