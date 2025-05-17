import psycopg2
import random

EVENT_CAPACITY_QUERY = """
SELECT id, name, round_two_capacity FROM events WHERE biddable;
"""

EVENT_WAGERS_QUERY = """
WITH latest_submissions AS (
    SELECT student_kerb, MAX(timestamp) 
    AS max_ts 
    FROM lottery_wagers 
    WHERE points > 0 AND round=2
    GROUP BY student_kerb
) 
SELECT wagers.id, wagers.student_kerb, wagers.points 
FROM lottery_wagers 
AS wagers 
JOIN latest_submissions as latest 
ON wagers.student_kerb = latest.student_kerb AND wagers.timestamp = latest.max_ts AND wagers.round = 2
WHERE event_id = %d
ORDER BY points DESC;
"""

CREATE_STUDENT_IF_NOT_EXISTS_QUERY = """
INSERT INTO students (kerb, remaining_points) 
SELECT %s, 1000 WHERE NOT EXISTS (SELECT 1 FROM students WHERE kerb = %s);
"""

ADD_NEPOS_QUERY = """
INSERT INTO lottery_wagers (event_id, student_kerb, points, timestamp, round, accepted) 
VALUES (%d, '%s', 0, LOCALTIMESTAMP, 2, TRUE);
"""

MARK_ACCEPTED_QUERY = """
UPDATE lottery_wagers SET accepted = TRUE WHERE id=%d;
"""

nepos = {
    3: [
    ],  # Level99

    4: [
        "bebanks3", 
        "ggirard", "ronsh", "megangs", "kmisqui",
        "jolenez"
    ],  # Red Sox

    5: [
        "bebanks3",
        "gblosen", "escandon",
        "kyna_sibling",
        "ncam", "huanyic1"
    ],  # Top Golf

    9: [
    ],  # Cafe Runaway

    10: [
    ],  # Taza Chocolate Lab Tours

    11: [
        "ajhdz",
        "escandon"
    ],  # Skyzone

    12: [
        "bebanks3",
        "timberc",
        "svasquez"
    ],  # Cheeky Monkey

    13: [
        "bebanks3",
        "Jolenez",
        "ncam", "huanyic1"
    ],  # F1 Arcade

    14: [
        "mvemuri"
    ],  # Skydiving Day 1 (5/21)

    15: [
        "bsheres"
    ],  # Skydiving Day 2 (5/22)

    16: [
    ],  # Skydiving Day 3 (5/23)

    17: [
        "ajhdz"
    ],  # Skydiving Day 4 (5/24)
}

conn = psycopg2.connect(
    host="seniorweek25.xvm.mit.edu",
    database="seniorweek25",
    user="seniorweek25",
    password="XXX"
)

def get_capacities():
    cur = conn.cursor()
    cur.execute(EVENT_CAPACITY_QUERY)
    res = cur.fetchall()
    cur.close()

    res = {r[0]: (r[1], r[2]) for r in res}
    return res


def get_wagers(event_id):
    cur = conn.cursor()
    cur.execute(EVENT_WAGERS_QUERY % event_id)
    res = cur.fetchall()
    cur.close()
    return res

def store_accepted_wagers(accepted_wagers):
    cur = conn.cursor()
    for wager in accepted_wagers:
        wager_id, kerb, points = wager
        cur.execute(MARK_ACCEPTED_QUERY % wager_id)
    conn.commit()
    cur.close()

def store_nepos(nepos):
    cur = conn.cursor()
    for event_id in nepos:
        for kerb in nepos[event_id]:
            cur.execute(CREATE_STUDENT_IF_NOT_EXISTS_QUERY, (kerb, kerb))
            cur.execute(ADD_NEPOS_QUERY % (event_id, kerb))
    conn.commit()
    cur.close()


capacities = get_capacities()
store_nepos(nepos)
for event_id in capacities:
    event_name = capacities[event_id][0]

    capacity = capacities[event_id][1]
    cutoff_capacity = capacity - len(nepos[event_id])
    print("event_id", event_id, "event_name", event_name, "capacity", capacity, "cutoff_capacity", cutoff_capacity)
    
    wagers = get_wagers(event_id) # [(wager_id, kerb, points), ...]
    for wager in wagers:
        wager_id, wager_kerb, wager_points = wager
        if wager_kerb in nepos[event_id]:
            wagers.remove(wager)
    cutoff_points = wagers[cutoff_capacity-1][2] if len(wagers) >= cutoff_capacity else 1
    print("cutoff_points", cutoff_points)

    # Store those accepted and those who are at the cutoff boundary
    accepted = []
    accepted.extend((0, i, 0) for i in nepos[event_id])
    boundary = []
    for i in range(len(wagers)):
        if wagers[i][2] > cutoff_points:
            accepted.append(wagers[i])
        if wagers[i][2] == cutoff_points:
            boundary.append(wagers[i])

    # If theres a tie for the cutoff, pick people randomly
    print("accepted", len(accepted), "boundary", len(boundary))
    if len(accepted) + len(boundary) > capacity:
        delta = capacity - len(accepted)
        random.shuffle(boundary)
        accepted.extend(boundary[:delta])
    else:
        accepted.extend(boundary)
    print("final accepted", len(accepted))
    # print("\n".join([str(i) for i in accepted]))


    with open("round_two/wagers_%s.txt" % event_name.replace(" ", "_"), 'w') as f:
        f.write("\n".join([str(i) for i in wagers]))
        f.write("\n\nNepos: %s" % str(nepos[event_id]))
        f.write("\n\ncapacity: %d" % capacity)
        f.write("\ncutoff_capacity: %d" % cutoff_capacity)
        f.write("\ncutoff_points: %d" % cutoff_points)
        f.write("\nnum accepted: %d" % len(accepted))
    with open("round_two/accepted_%s.txt" % event_name.replace(" ", "_"), 'w') as f:
        f.write("\n".join([str(i[1])+"@mit.edu" for i in accepted]))

    store_accepted_wagers(accepted)

conn.close()
