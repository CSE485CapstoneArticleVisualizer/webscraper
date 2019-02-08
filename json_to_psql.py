
# Open the JSON file
import json
import psycopg2
import datetime
import os

def delete_all_rows():
    cur.execute("DELETE FROM cites;")
    cur.execute("DELETE FROM cited_by;")
    cur.execute("DELETE FROM article_authors;")
    cur.execute("DELETE FROM sma;")
    cur.execute("DELETE FROM journals;")

    conn.commit()
    print("Deleted all rows.")

# Saves journal in the database if it doens't exist
# Returns journal id
def save_journal(journal_name):
    cur.execute("SELECT id FROM journals AS j WHERE j.name = %s;", (journal_name, ))
    journal = cur.fetchone()

    # Create journal if it doesn't exist
    if journal is None:
        cur.execute("INSERT INTO journals (name) VALUES (%s) RETURNING id;", (journal_name,))

        journal_id = cur.fetchone()[0]
        conn.commit()
        print("Saved journal: {}".format(journal_name))

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
    for cited_by_id in cited_by:
        cur.execute("INSERT INTO cited_by (article_id, cited_by_id) VALUES (%s, %s)", (article_id, cited_by_id))
    conn.commit()

# Saves each citation in the cites list 
def save_cites(cites, article_id):
    for cites_article_id in cites:
        cur.execute("INSERT INTO cites (article_id, cites_article_id) VALUES (%s, %s)", (article_id, cites_article_id))
    conn.commit()

# Converts a list of article titles to article ids
def convert_articles_to_ids(article_titles):
    article_ids = []

    for title in article_titles:
        cur.execute("SELECT id FROM sma AS sma where sma.title = %s;", (title, ))
        article = cur.fetchone()

        if article is None:
            # Create an article with all fields empty (except for title and date_added)
            cur.execute("INSERT INTO sma (title, date_added) VALUES (%s, %s) RETURNING id;",
                        (title, datetime.datetime.now()))

            article = cur.fetchone()
            article_ids.append(article[0])
            conn.commit()
        else:
            article_ids.append(article[0])

    return article_ids

# Saves an article
def save_article(json_article):
    cur.execute("SELECT id, journal_id FROM sma AS sma where sma.title = %s;", (json_article['title'], ))
    article = cur.fetchone()
    
    # Create article if it doesn't exist
    if article is None:
        journal_id = save_journal(json_article['journal'])
        cur.execute("INSERT INTO sma (expected_cited_by_count, expected_cites_count, abstract, publish_date, date_added, title, journal_id) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
                    (json_article['citationCount'], json_article['referenceCount'], json_article['abstract'], json_article['date'], datetime.datetime.now(), json_article['title'], journal_id))
        
        article = cur.fetchone()
        article_id = article[0]
        conn.commit()

        # Unique pairs in citedBy, cites, and authors table. (Hint: GroupBy?)
        # Solution: Not groupBy. Used Primary Key on both columns.
        save_cited_by(convert_articles_to_ids(json_article['citedBy']), article_id)
        save_authors(json_article['authors'], article_id)
        save_cites(convert_articles_to_ids(json_article['cites']), article_id)
        print("Created new article: ", article_id)

    else:

        # Run update if necessary (expected cited by, expected cites, abstract, publish date, date added, etc.)
        # It becomes 'necessary' if the journal field is missing
        article_id = article[0]
        journal_id = article[1]
        if journal_id is None: # Run the update
            journal_id = save_journal(json_article['journal'])
            cur.execute("UPDATE sma SET expected_cited_by_count=%s, expected_cites_count=%s, abstract=%s, publish_date=%s, date_added=%s, journal_id=%s WHERE id = %s;", 
                        (json_article['citationCount'], json_article['referenceCount'], json_article['abstract'], json_article['date'], datetime.datetime.now(), journal_id, article_id))
            conn.commit()

            # Unique pairs in citedBy, cites, and authors table. (Hint: GroupBy?)
            # Solution: Not groupBy. Used Primary Key on both columns.
            save_cited_by(convert_articles_to_ids(json_article['citedBy']), article_id)
            save_authors(json_article['authors'], article_id)
            save_cites(convert_articles_to_ids(json_article['cites']), article_id)
            print("Updated article: ", article_id)

    # ------------------------------------------------------------------------------
    # journal_id = save_journal(json_article['journal'])
    # cur.execute("INSERT INTO sma (expected_cited_by_count, expected_cites_count, abstract, publish_date, date_added, title, journal_id) VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO UPDATE SET expected_cited_by_count = 666 RETURNING id;", 
    #         (json_article['citationCount'], json_article['referenceCount'], json_article['abstract'], json_article['date'], datetime.datetime.now(), json_article['title'], journal_id))
    
    # article = cur.fetchone()
    # article_id = article[0]
    # ------------------------------------------------------------------------------

    return article_id
    
def save_article_file(filename):
    with open(filename) as data:
        json_article = json.load(data)

        if json_article['citationCount'] == 'N/A':
            json_article['citationCount'] = 0

        json_article['citationCount'] = str(json_article['citationCount']).replace(',', '')
        json_article['referenceCount'] = str(json_article['referenceCount']).replace(',', '')


        print("Loaded json:", json_article['title'])
        save_article(json_article)
    
    print("Saved file")
        
def get_data_files():
    import glob
    return glob.glob("./Data/*/*")

def move_data_file(date_folder, filename):
    if not os.path.exists("./Data_Archived/"+date_folder):
        os.makedirs("./Data_Archived/"+date_folder)

    os.rename("./Data/{}/{}".format(date_folder, filename), "./Data_Archived/{}/{}".format(date_folder,filename))

def get_folders(path):
    folders = []
    while 1:
        path, folder = os.path.split(path)

        if folder != "":
            folders.append(folder)
        else:
            if path != "":
                folders.append(path)

            break

    folders.reverse()
    return folders

if __name__ == "__main__":
    conn = psycopg2.connect("host=localhost dbname=alex")
    cur = conn.cursor()
    # delete_all_rows()

    # print(save_journal('Space Journal 3'))
    # save_authors(['Space Author 1', 'Space Author 2', 'Space Author 3'], 0)
    
    average_time = 0
    start_time = datetime.datetime.now()
    for file in get_data_files():
        time1 = datetime.datetime.now()

        save_article_file(file)
    
        time2 = datetime.datetime.now() # waited a few minutes before pressing enter
        elapsedTime = time2 - time1
        print("Time it took: ", elapsedTime.total_seconds())
        average_time = average_time * 0.99 + elapsedTime.total_seconds() * (1-0.99) 
        print("Running average time: ", average_time)
        folders = get_folders(file)

        move_data_file(folders[2], folders[3])

    finish_time = datetime.datetime.now()
    elapsedTime = finish_time - start_time
    min_sec = divmod(elapsedTime.total_seconds(), 60)
    print(min_sec)
    print("Total run time: {} min {} sec".format(min_sec[0], min_sec[1]))

    conn.commit() 
    conn.close()


