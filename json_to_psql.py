
# Open the JSON file
import json
import psycopg2

connection = psycopg2.connect("host=localhost dbname=stephen user=stephen password=stephen")
cursor = connection.cursor()

with open('./Data/2019-01-28/2017-09-01--YouTube as a Source of Information on Neurosurgery.json') as json_data:
    data = json.load(json_data)
    print(data)
    # Populate column fields
    fields = ['abstract', 'authors', 'citationCount', 'citedBy', 'citedByCount', 'cites', 'citesCount', 'date', 'journal', 'referenceCount', 'title'];

    # Store JSON in databse
    # for item in data:
    #     my_data = [item[field] for field in fields]
    #     for i, v in enumerate(my_data):
    #         if isinstance(v, dict):
    #             my_data[i] = json.dumps(v)
    #     insert_query = "INSERT INTO articles VALUES " 
    #     cursor.execute(insert_query, tuple(my_data))

    my_data = [data[field] for field in fields]
    for i, v in enumerate(my_data):
        if isinstance(v, dict):
            my_data[i] = json.dumps(v)

    cursor.execute("INSERT INTO articles VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", tuple(my_data))