-- Q11: Among the top 10 contractors (by budget), which have the highest count of
-- contracts past completion_date but progress < 100% (delay flags)?

WITH top_contractor_stats AS (
    SELECT  contractor, 
            SUM(budget) AS total_budget,
            COUNT(*) AS project_count,
            COUNT(*) FILTER (WHERE completion_date < CURRENT_DATE AND progress < 100) AS delayed_count
    FROM dpwh_transparency_data
    GROUP BY contractor
    ORDER BY SUM(budget) DESC
    LIMIT 10
)
SELECT *
FROM top_contractor_stats
ORDER BY delayed_count DESC;


-- Q12: Across all contractors, which have the highest percentage of contracts
-- flagged as delayed (past completion_date, progress < 100%) TODO: check status first?
SELECT  contractor,
        COUNT(*) FILTER (WHERE completion_date < CURRENT_DATE AND progress < 100) AS delayed_count,
        COUNT(*) AS total_contracts,
        ROUND( 100.0 * COUNT(*) FILTER (WHERE completion_date < CURRENT_DATE AND progress < 100)/ COUNT(*), 2) AS delayed_percentage
FROM dpwh_transparency_data
GROUP BY contractor
HAVING COUNT(*) > 100
ORDER BY delayed_percentage DESC
LIMIT 10;




-- Q13: Which contracts are marked status = 'completed' but have progress < 100%
-- (data-integrity / reporting red flag)?
SELECT  contractor,
        COUNT(*) FILTER (WHERE status = 'completed' AND progress < 100) AS wrong_status_count,
        COUNT(*) AS total_contracts
FROM dpwh_transparency_data
GROUP BY contractor
HAVING COUNT(*) > 100
ORDER BY wrong_status_count DESC
LIMIT 10;

-- Q14: Which contractors have the most contracts where amount_paid exceeds budget
-- (potential overpayment)?


-- Q15: What's the average overdue duration (today - completion_date) for still
-- incomplete contracts, grouped by contractor, for the top 10 by budget?