import psycopg2
import random

ROUND_ONE_TICKETS_PERCENT = 0.75

EVENT_CAPACITY_QUERY = """
SELECT id, name, capacity FROM events WHERE biddable;
"""

EVENT_WAGERS_QUERY = """
WITH latest_submissions AS (
    SELECT student_kerb, MAX(timestamp) 
    AS max_ts 
    FROM lottery_wagers 
    WHERE points > 0
    GROUP BY student_kerb
) 
SELECT wagers.id, wagers.student_kerb, wagers.points 
FROM lottery_wagers 
AS wagers 
JOIN latest_submissions as latest 
ON wagers.student_kerb = latest.student_kerb AND wagers.timestamp = latest.max_ts 
WHERE event_id = %d
ORDER BY points DESC;
"""

CREATE_STUDENT_IF_NOT_EXISTS_QUERY = """
INSERT INTO students (kerb, remaining_points) 
SELECT %s, 1000 WHERE NOT EXISTS (SELECT 1 FROM students WHERE kerb = %s);
"""

ADD_NEPOS_QUERY = """
INSERT INTO lottery_wagers (event_id, student_kerb, points, timestamp, accepted) 
VALUES (%d, '%s', 0, LOCALTIMESTAMP, TRUE);
"""

MARK_ACCEPTED_QUERY = """
UPDATE lottery_wagers SET accepted = TRUE WHERE id=%d;
"""

nepos = {
    3: ["keena881", "angeles",
        "claire25", "sarahlu", "sallyz21", "malder", "tsm255",
        "kyna", "cnf", "anaemeje", "fdma2405", "stella24",
        "nmustafa", "katieac", "ninaj", "logtaham",
        "yycliang", "annamokk", "netb", "jkim25", "graceyan"
    ],  # Level99

    4: [
        "fdma2405", "gerardo",
        "kyna", "cnf", "anaemeje",
        "yycliang", "annamokk"
    ],  # Red Sox

    5: [
        "claire25", "gracep",
        "stella24", "cswan25", "rjloh",
        "fdma2405",
        "kyna", "cnf", "anaemeje",
        "katieac", "logtaham",
        "nmustafa",
        "jkim25", "graceyan", "mbivin",
        "yycliang", "aliak", "emmajung",
    ],  # Top Golf

    9: [
        "jkim25",
        "jolenez", "vivi1021", "kdutta1", "avad114",
        "ewang824", "graceyan", "jerrylu",
        "yycliang", "mnsodini",
        "nmustafa"
    ],  # Cafe Runaway

    10: [
        "claire25", "gyzhang",
        "kyna", "cnf", "anaemeje",
        "sallyz21", "malder", "eves",
        "katieac", "angeles",
        "jkim25", "graceyan",
        "yycliang", "netb", "aliak",
        "fdma2405"
    ],  # Taza Chocolate Lab Tours

    11: [
        "stella24", "pbowen", "ajhdz",
        "fdma2405", "katieac", "keena881",
        "yycliang", "netb",
        "sallyz21", "jmlaw"
    ],  # Skyzone

    12: [
        "sallyz21", "eves", "jmlaw",
        "kyna", "cnf", "anaemeje",
        "stella24", "cswan25",
        "fdma2405", "nmustafa", "ncam", "huanyic1",
        "katieac", "logtaham",
        "claire25",
        "yycliang", "emmajung",
        "jkim25",
        "hyewona"
    ],  # Cheeky Monkey

    13: [
        "claire25", "fdma2405",
        "stella24", "bokul123",
        "nmustafa",
        "yycliang", "sebnemg", "netb",
        "hyewona"
    ],  # F1 Arcade

    14: [
        "sallyz21", "jmlaw",
        "fdma2405", "gblosen"
    ],  # Skydiving Day 1 (5/21)

    15: ["rjloh"],  # Skydiving Day 2 (5/22)

    16: [],  # Skydiving Day 3 (5/23)

    17: [
        "mkdine", "gabimcd", "ninaj", "sebdj", "sasne", "sihernan", "ajhdz", "escandon", "juliush",
        "stella24", "sarahlu", "claire25",
        "nmustafa", "Katieac", "logtaham",
        "jkim25", "graceyan",
        "hyewona"
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

def store_accepted_wagers(event_id, accepted_wagers):
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
    round_one_capacity = capacity if event_id in range(14, 18) else int(capacity * ROUND_ONE_TICKETS_PERCENT)
    cutoff_capacity = round_one_capacity - len(nepos[event_id])
    print("event_id", event_id, "event_name", event_name, "capacity", capacity, "round_one_capacity", round_one_capacity, "cutoff_capacity", cutoff_capacity)
    
    wagers = get_wagers(event_id) # [(wager_id, kerb, points), ...]
    for wager in wagers:
        if wager[1] in nepos[event_id]:
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


    with open("round_one/wagers_%s.txt" % event_name.replace(" ", "_"), 'w') as f:
        f.write("\n".join([str(i) for i in wagers]))
        f.write("\n\nNepos: %s" % str(nepos[event_id]))
        f.write("\n\ncapacity: %d" % capacity)
        f.write("\nround_one_capacity: %d" % round_one_capacity)
        f.write("\ncutoff_capacity: %d" % cutoff_capacity)
        f.write("\ncutoff_points: %d" % cutoff_points)
        f.write("\nnum accepted: %d" % len(accepted))
    with open("round_one/accepted_%s.txt" % event_name.replace(" ", "_"), 'w') as f:
        f.write("\n".join([str(i[1])+"@mit.edu" for i in accepted]))

    store_accepted_wagers(event_id, accepted)

conn.close()
