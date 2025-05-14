UPDATE events
SET
  round_one_cutoff = CASE name
    WHEN 'Cafe Runaway'             THEN 100
    WHEN 'Cheeky Monkey'            THEN 200
    WHEN 'F1 Arcade'                THEN 300
    WHEN 'Level99'                  THEN 500
    WHEN 'Red Sox Game'             THEN 1
    WHEN 'Skydiving Day 1'          THEN 100
    WHEN 'Skydiving Day 2'          THEN 600
    WHEN 'Skydiving Day 3'          THEN 1
    WHEN 'Skydiving Day 4'          THEN 100
    WHEN 'Skyzone'                  THEN 196
    WHEN 'Taza Chocolate Lab Tours' THEN 175
    WHEN 'Top Golf'                 THEN 150
    ELSE round_one_cutoff
  END,
  round_two_capacity = CASE name
    WHEN 'Cafe Runaway'             THEN capacity - 124
    WHEN 'Cheeky Monkey'            THEN capacity - 230
    WHEN 'F1 Arcade'                THEN capacity - 162
    WHEN 'Level99'                  THEN capacity - 171
    WHEN 'Red Sox Game'             THEN capacity - 187
    WHEN 'Skydiving Day 1'          THEN capacity - 100
    WHEN 'Skydiving Day 2'          THEN capacity - 100
    WHEN 'Skydiving Day 3'          THEN capacity - 12
    WHEN 'Skydiving Day 4'          THEN capacity - 100
    WHEN 'Skyzone'                  THEN capacity - 187
    WHEN 'Taza Chocolate Lab Tours' THEN capacity - 82
    WHEN 'Top Golf'                 THEN capacity - 226
    ELSE round_two_capacity
  END
WHERE name IN (
  'Cafe Runaway','Cheeky Monkey','F1 Arcade','Level99',
  'Red Sox Game','Skydiving Day 1','Skydiving Day 2',
  'Skydiving Day 3','Skydiving Day 4',
  'Skyzone','Taza Chocolate Lab Tours','Top Golf'
);