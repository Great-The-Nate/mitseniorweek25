WITH stats AS (
    select student_kerb, count(*) as num_events 
    from lottery_wagers 
    where accepted 
    group by student_kerb 
    order by num_events asc
) 
SELECT num_events, count(*) as frequency 
from stats 
group by num_events 
order by num_events desc;

