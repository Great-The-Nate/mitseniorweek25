'''
Copy bids from XVM to athena. Athena AFS can be considered reliable storage.
'''
import psycopg2

conn = psycopg2.connect(
    host="seniorweek25.xvm.mit.edu",
    database="seniorweek25",
    user="seniorweek25",
    password="XXX"
)
cur = conn.cursor()

cur.execute("SELECT * FROM lottery_wagers;")
res = cur.fetchall()
with open('wagers_backup.txt', 'w') as f:
    for row in res:
        f.write(str(row) + '\n')

cur.execute("SELECT * FROM lottery_attendance;")
res = cur.fetchall()
with open('attendance_backup.txt', 'w') as f:
    for row in res:
        f.write(str(row) + '\n')

cur.close()
conn.close()
