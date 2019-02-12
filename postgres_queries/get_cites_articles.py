# TODO: Get the articles that primary article cites.

import psycopg2

def getCitesArticles(articleID) :
    cur.execute("""SELECT S.* 
                   FROM sma S, 
                   (SELECT C.* FROM cites C WHERE C.article_id = %s) C 
                   WHERE S.id = C.cites_article_id""", (articleID, ))
    print(cur.fetchall())

if __name__ == "__main__":
    conn = psycopg2.connect("host=localhost port=5434 dbname=stephen user=stephen password=stephen")
    cur = conn.cursor()

    getCitesArticles(9)