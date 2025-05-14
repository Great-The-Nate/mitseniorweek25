WITH latest_submissions AS (
    SELECT student_kerb, MAX(timestamp) 
    AS max_ts 
    FROM lottery_wagers 
    WHERE points > 0
    GROUP BY student_kerb
) 
select lottery.event_id, name, count(*) from lottery_wagers as lottery
join latest_submissions as latest on lottery.student_kerb = latest.student_kerb and lottery.timestamp = latest.max_ts
join events as e on lottery.event_id = e.id 
where biddable
group by event_id, name 
order by event_id;