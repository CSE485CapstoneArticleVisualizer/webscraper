# TODO: Get the articles whose title matches a certain string

import psycopg2

def getArticlesThatMatchString(string) :
    cur.execute("SELECT S.* FROM sma S WHERE S.title = %s", (string, ))
    print(cur.fetchall())

if __name__ == "__main__":
    conn = psycopg2.connect("host=localhost port=5434 dbname=stephen user=stephen password=stephen")
    cur = conn.cursor()

    getArticlesThatMatchString("Linkages and Spillovers")