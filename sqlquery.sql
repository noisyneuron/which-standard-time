SELECT 
visits.id as visit_id,
datetime(((visits.visit_time/1000000)-11644473600), "unixepoch", "localtime") as visit_local_time, COUNT(*) cnt,
visits.from_visit as from_visit_id,
visits.transition,
urls.typed_count,
urls.id as url_id,
urls.url as url_link,
urls.title as url_title,
urls.visit_count as url_visit_count,
segments.name as segment_name
FROM 
visits
LEFT JOIN urls on visits.url = urls.id
LEFT JOIN segments on visits.segment_id = segments.id
WHERE visit_local_time >= '2018-09-16'  AND visit_local_time < '2018-09-17'
GROUP BY strftime('%s', visit_local_time) / 60
