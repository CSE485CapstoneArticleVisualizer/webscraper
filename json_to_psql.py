
# Open the JSON file
import json
import psycopg2

conn = psycopg2.connect("host=localhost dbname=stephen user=stephen password=stephen")
cur = conn.cursor()

with open('./Data/2019-01-28/2019-03-01--Demystifying the impact of CEO transformational leadership on firm performance Interactive roles of exploratory innovation and environmental uncertainty.json') as json_data:
#with open('./Data/2019-01-28/2017-09-01--YouTube as a Source of Information on Neurosurgery.json') as json_data:    
    
    # data here is a list of dicts
    data = [json.load(json_data)]
    

    # create a table with one column of type JSON
    cur.execute("CREATE TABLE SMA2 (data json);")

    #fields = ['abstract', 'authors', 'citationCount', 'citedBy', 'citedByCount', 'cites', 'citesCount', 'date', 'journal', 'referenceCount', 'title'];
    fields = ['title'];

    for item in data:
        my_data = {field: item[field] for field in fields}
        print("FINAL DATA\n", my_data)
        cur.execute("INSERT INTO SMA2 VALUES (%s)", (json.dumps(my_data),))


    # commit changes
    conn.commit()
    # Close the connection
    conn.close()
    print("Success!")

    # -------------------------------------