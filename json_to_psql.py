
# Open the JSON file
import json
import psycopg2

# Saves journal in the database if it doens't exist
# Returns journal id
def save_journal(journal_name):
    cur.execute("select id from journals as j where j.name = %s;", (journal_name, ))
    journal = cur.fetchone()

    # Create journal if it doesn't exist
    if journal is None:
        cur.execute("INSERT INTO journals (name) VALUES (%s)", (journal_name,))
        conn.commit()
        print("Saved journal {}".format(journal_name))

        cur.execute("select id from journals as j where j.name = %s;", (journal_name, ))
        journal_id = cur.fetchone()[0]
    else:
        # Journal exists. Retrive journal id
        journal_id = journal[0]

    return journal_id
    

# Saves each author in the authors list 
def save_authors(authors, article_id):
    for author_name in authors:
        cur.execute("INSERT INTO article_authors (article_id, author_name) VALUES (%s, %s)", (article_id, author_name))
        conn.commit()

# Saves each citation in the cited_by list 
def save_cited_by(cited_by, article_id):
    pass

# Saves each citation in the cites list 
def save_cites(cites, article_id):
    pass

# Saves an article
def save_article(json_obj):
    pass


if __name__ == "__main__":
    conn = psycopg2.connect("host=localhost dbname=alex")
    cur = conn.cursor()

    # print(save_journal('Space Journal 3'))
    save_authors(['Space Author 1', 'Space Author 2', 'Space Author 3'], 0)
    conn.commit(), 
    conn.close()
