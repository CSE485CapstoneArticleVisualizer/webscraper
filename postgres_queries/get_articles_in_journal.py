# TODO: Get the articles that are stored in the database for a given journal

import psycopg2

def getArticlesForJournal(journal) :
    cur.execute("""SELECT S.* 
                   FROM sma S, journals J 
                   WHERE S.journal_id = J.id 
                   AND J.name = %s""", (journal, ))
    print(cur.fetchall())

if __name__ == "__main__":
    conn = psycopg2.connect("host=localhost port=5434 dbname=stephen user=stephen password=stephen")
    cur = conn.cursor()

    getArticlesForJournal("Research Policy")