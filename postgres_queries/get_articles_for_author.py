# TODO: Get the articles that match a given author name

import psycopg2

def getArticlesForAuthor(author) :
    cur.execute("""SELECT S.* 
                   FROM sma S, article_authors A 
                   WHERE S.id = A.article_id 
                   AND A.author_name = %s""", (author, ))
    print(cur.fetchall())

if __name__ == "__main__":
    conn = psycopg2.connect("host=localhost port=5434 dbname=stephen user=stephen password=stephen")
    cur = conn.cursor()

    getArticlesForAuthor("Carlos Penilla")