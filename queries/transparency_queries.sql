-- Q16: What percentage of contracts marked status = 'completed' 
-- have progress < 100? too little 67/205109

WITH completed_contracts AS (
    SELECT COUNT(*) AS number_of_completed_contracts
    FROM dpwh_transparency_data
    WHERE status = 'completed' 
)

SELECT  COUNT(*) AS completed_contracts,
        COUNT(*) FILTER (WHERE progress < 100) AS suspicious_progress,
        ROUND(COUNT(*) FILTER (WHERE progress < 100) / COUNT(*)  ,2) AS suspicious_percentage
FROM dpwh_transparency_data
WHERE status = 'completed'


-- Q17: Which contractors have the highest number of contracts with
-- status = 'completed' but progress < 100 (status/progress contradiction)?

SELECT  contractor,
        COUNT(*) AS progress_status_contradiction
FROM dpwh_transparency_data
WHERE status = 'completed' AND progress < 100
GROUP BY contractor
ORDER BY progress_status_contradiction DESC
LIMIT 10;


-- Q18: How many DPWH contracts have report_count = 0 (never publicly
-- reported/monitored at all)?
SELECT COUNT(*) AS number_of_no_reports
FROM dpwh_transparency_data
WHERE report_count = 0;


-- Q19: Which contractors have the largest average overdue duration
-- (days past completion_date) for their still-incomplete contracts?
SELECT  contractor,
        COUNT(*) AS number_of_delayed_contracts
FROM dpwh_transparency_data
WHERE completion_date < CURRENT_DATE AND status != 'terminated' AND status != 'completed'
GROUP BY contractor
ORDER BY number_of_delayed_contracts DESC
LIMIT 10;


-- Q20: Of contracts still ongoing and past completion_date, what percentage
-- have progress = 0 (delayed with zero recorded work)?
WITH delayed_zero_work_contracts()
SELECT *
FROM dpwh_transparency_data
WHERE progress = 0 AND completion_date < CURRENT_DATE AND status = 'completed'


