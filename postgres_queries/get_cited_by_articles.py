# TODO: Get the articles that the 
# primary article is cited by.

import psycopg2

def getCitedByArticles(articleID) :
    cur.execute("SELECT S.* FROM sma S, (SELECT C.* FROM cited_by C WHERE C.article_id = %s) C WHERE S.id = C.cited_by_id", (articleID, ))
    print(cur.fetchall())

if __name__ == "__main__":
    conn = psycopg2.connect("host=localhost port=5434 dbname=stephen user=stephen password=stephen")
    cur = conn.cursor()

    getCitedByArticles(1)