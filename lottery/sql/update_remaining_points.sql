UPDATE students AS s
SET remaining_points = s.remaining_points - agg.spent_points
FROM (
  SELECT w.student_kerb, SUM(LEAST(w.points, e.round_one_cutoff)) AS spent_points
  FROM lottery_wagers as w 
  JOIN events as e ON w.event_id = e.id
  where w.accepted AND w.round = 1
  GROUP BY student_kerb
) AS agg
WHERE agg.student_kerb = s.kerb;
