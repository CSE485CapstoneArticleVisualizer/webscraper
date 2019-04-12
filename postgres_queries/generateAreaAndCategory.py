import csv
import psycopg2
import datetime


def getCSVJournals():
    journals = {}

    with open('RankingsListWithDividedNumber.csv', encoding='utf8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        skipLines = 2
        for row in csv_reader:
            if skipLines > 0:
                skipLines -= 1
                continue

            name = row[1]
            # print("Name:", name)
            divided_rank = row[11]
            # print("Divided rank:", divided_rank)
            subject_category = row[16].lower().strip()
            # print("Subject Category:", subject_category)

            if name not in journals:  # New journal
                journals[name] = {
                    "divided_rank": divided_rank,
                    "subject_category": subject_category
                }

            # Update subject category of journal
            if divided_rank < journals[name]['divided_rank']:
                journals[name]['divided_rank'] = divided_rank
                journals[name]['subject_category'] = subject_category

    return journals


def getCategoryToAreaDict():
    subject_cat_to_subject_area = {}

    with open('Scopus_Categories_Subcategories_paired_charactersremoved2.csv', encoding='utf8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        for row in csv_reader:
            subject_area = row[0].lower().strip()
            subject_category = row[1].lower().strip()
            subject_cat_to_subject_area[subject_category] = subject_area
            print(row[0], row[1])
    return subject_cat_to_subject_area


def getDatabaseJournals():
    cur.execute("""SELECT J.name 
                    FROM journals J""", ())
    return [row[0] for row in cur.fetchall()]


if __name__ == "__main__":
    conn = psycopg2.connect(
        "host=localhost port=5434 dbname=stephen user=stephen password=stephen")
    cur = conn.cursor()

    csvJournals = getCSVJournals()
    print("Retrieved Journals from CSV file")

    subject_cat_to_subject_area = getCategoryToAreaDict()
    print("Created reverse lookup table for subject category to subject area")

    # Get subject area for top subject category
    matched = []
    unmatched = []
    for key, val in csvJournals.items():
        if val['subject_category'] == 'archaeology':
            val['subject_category'] = 'archeology'
        elif val['subject_category'] == 'palaeontology':
            val['subject_category'] = 'paleontology'
        elif val['subject_category'] == 'health(social science)':
            val['subject_category'] = 'health (social science)'
        elif val['subject_category'] == 'obstetrics and gynaecology':
            val['subject_category'] = 'obstetrics and gynecology'
        elif val['subject_category'] == 'modelling and simulation':
            val['subject_category'] = 'modeling and simulation'
        elif val['subject_category'] == 'advanced and specialised nursing':
            val['subject_category'] = 'advanced and specialized nursing'
        elif val['subject_category'] == 'biochemistry, medical':
            val['subject_category'] = 'biochemistry (medical)'
        elif val['subject_category'] == 'phychiatric mental health':
            val['subject_category'] = 'psychiatric mental health'
        elif val['subject_category'] == 'ecological modelling':
            val['subject_category'] = 'ecological modeling'
        elif val['subject_category'] == 'oncology(nursing)':
            val['subject_category'] = 'oncology (nursing)'
        elif val['subject_category'] == 'genetics(clinical)':
            val['subject_category'] = 'genetics (clinical)'
        elif val['subject_category'] == 'ageing':
            val['subject_category'] = 'aging'
        elif val['subject_category'] == 'medical–surgical':
            val['subject_category'] = 'medical and surgical nursing'
        elif val['subject_category'] == 'clinical neurology':
            val['subject_category'] = 'neurology (clinical)'
        elif val['subject_category'] == 'critical care':
            val['subject_category'] = 'critical care nursing'
        # Misnamed in RankingslistWithDividedNumber.csv
        elif val['subject_category'] == 'emergency':
            val['subject_category'] = 'emergency nursing'
        elif val['subject_category'] == 'veterinary (miscalleneous)':
            val['subject_category'] = 'veterinary (miscellaneous)'

        if val['subject_category'] not in subject_cat_to_subject_area:
            print("Missing Subject Area for Subject Category:",
                  val['subject_category'], '...\t Journal: ', key)
            unmatched.append(key)
            csvJournals[key]['subject_area'] = "Unknown"
        else:
            matched.append(key)
            csvJournals[key]['subject_area'] = subject_cat_to_subject_area[val['subject_category']]

    print("Updated journals to include subject area using subject category")

    print("Matched Count:", len(matched))
    print("Unmatched Count:", len(unmatched))
    print("First 5 Unmatched:", unmatched[:5])

    # Update database
    running_time_avg = 0
    count_remaining = len(csvJournals)
    for journal_name, journal_attr in csvJournals.items():
        count_remaining -= 1
        start_time = datetime.datetime.now()

        cur.execute("""UPDATE journals J
                    SET subject_area = %s, subject_category = %s
                    WHERE J.name LIKE %s""", (journal_attr['subject_area'], journal_attr['subject_category'], journal_name))
        cur.execute("""INSERT INTO journals (name, subject_area, subject_category)
                        SELECT %s, %s, %s
                        WHERE NOT EXISTS (SELECT 1 FROM journals WHERE name LIKE %s)""",
                    (journal_name, journal_attr['subject_area'], journal_attr['subject_category'], journal_name))
        conn.commit()
        end_time = datetime.datetime.now()
        time_diff = end_time - start_time
        running_time_avg = running_time_avg * 0.997 + time_diff.total_seconds() * 0.003
        print(
            "[{:.3f} sec] - [{:.3f} sec avg.] - [Time Remaining: {:.3f} sec] Updated Journal: {}".format(time_diff.total_seconds(), running_time_avg, running_time_avg*count_remaining, journal_name))
