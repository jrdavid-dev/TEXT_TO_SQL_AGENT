-- Q11: Among the top 10 contractors (by budget), which have the highest count of
-- contracts past completion_date but progress < 100% (delay flags) NOthing is delayed?

WITH top_contractor_stats AS (
    SELECT  contractor, 
            SUM(budget) AS total_budget,
            COUNT(*) AS project_count,
            COUNT(*) FILTER (WHERE completion_date < CURRENT_DATE AND progress < 100 AND status != 'terminated' AND status != 'completed') AS delayed_count
    FROM dpwh_transparency_data
    GROUP BY contractor
    ORDER BY SUM(budget) DESC
    LIMIT 10
)
SELECT *
FROM top_contractor_stats
ORDER BY delayed_count DESC, project_count DESC;


-- Q12: Across all contractors, which have the highest percentage of contracts
-- flagged as delayed (past completion_date, progress < 100%) NONe

WITH contractor_with_delays AS (
        SELECT  contractor,
                COUNT(*) AS delayed_contracts
        FROM dpwh_transparency_data
        WHERE completion_date < CURRENT_DATE AND progress < 100 AND status != 'terminated' AND status != 'completed'
        GROUP BY contractor
)

SELECT  contractor_with_delays.contractor,
        ROUND( 100 * contractor_with_delays.delayed_contracts / COUNT(*), 2) AS delayed_percentage, 
        COUNT(*) AS total_contracts
FROM dpwh_transparency_data
INNER JOIN contractor_with_delays ON dpwh_transparency_data.contractor = contractor_with_delays.contractor
GROUP BY contractor_with_delays.contractor, contractor_with_delays.delayed_contracts;



-- Q13: Which contracts are marked status = 'completed' but have progress < 100%
-- (data-integrity / reporting red flag)?


-- Q14: Which contractors have the most contracts where amount_paid exceeds budget
-- (potential overpayment) NONE?
SELECT  contractor, 
        COUNT(*) AS overpaid_contracts,
        SUM(amount_paid - budget) AS total_overpayment
FROM dpwh_transparency_data
WHERE amount_paid > budget
GROUP BY contractor
ORDER BY COUNT(*) DESC
LIMIT 10;


-- Q15: What's the average overdue duration (today - completion_date) for still
-- incomplete contracts, grouped by contractor, for the top 10 by budget NONE?
WITH top_10_contractor AS (
    SELECT  contractor
    FROM dpwh_transparency_data
    GROUP BY contractor
    ORDER BY SUM(budget) DESC
    LIMIT 10
)
SELECT  top_10_contractor.*, 
        ROUND(AVG(CURRENT_DATE - completion_date), 0) AS avg_days_overdue,
        COUNT(*) AS number_of_contract_delays
FROM dpwh_transparency_data
INNER JOIN top_10_contractor ON dpwh_transparency_data.contractor = top_10_contractor.contractor
WHERE completion_date < CURRENT_DATE AND progress < 100 AND status != 'terminated' AND status != 'completed'
GROUP BY top_10_contractor.contractor
ORDER BY avg_days_overdue DESC


-- Q11: What percentage of all contracts fall into each status category
-- (portfolio snapshot)?

SELECT  status,
        COUNT(*) AS contract_count,
        ROUND( 100 * COUNT(*) / SUM(COUNT(*)) OVER() ,2) AS pct_of_total
FROM dpwh_transparency_data
GROUP BY status
ORDER BY pct_of_total DESC;


-- Q12: Which categories have the highest share of ongoing contracts
-- (excluding completed/terminated) with progress under 50%?
SELECT category,
       COUNT(*) FILTER (WHERE progress < 50) AS low_progress_count,
       COUNT(*) AS total_ongoing,
       ROUND(100.0 * COUNT(*) FILTER (WHERE progress < 50) / NULLIF(COUNT(*), 0), 2) AS pct_low_progress
FROM dpwh_transparency_data
WHERE status NOT IN ('completed', 'terminated')
GROUP BY category
ORDER BY pct_low_progress DESC;

-- Q13: Which contracts are marked status = 'completed' but have progress < 100%
-- (data-integrity / reporting red flag)?
SELECT  contract_id, 
        description, 
        category, 
        contractor, 
        progress, 
        status, 
        start_date, 
        completion_date, 
        budget, 
        amount_paid
FROM dpwh_transparency_data
WHERE status = 'completed' AND progress < 100;

-- Q14: What percentage of all contracts are joint ventures (contractor field
-- contains multiple names)?

SELECT
    ROUND(100.0 * COUNT(*) FILTER (WHERE contractor LIKE '%/%') / NULLIF(COUNT(*), 0), 2) AS pct_joint_ventures,
    COUNT(*) FILTER (WHERE contractor LIKE '%/%') AS jv_count,
    COUNT(*) AS total_contracts
FROM dpwh_transparency_data;

-- Q15: Which individual contractors appear most often in joint-venture
-- combinations, and what's their total JV-associated budget?

SELECT TRIM(contractor_split) AS contractor,
       COUNT(*) AS jv_appearance_count,
       SUM(budget) AS jv_total_budget
FROM dpwh_transparency_data,
     LATERAL unnest(string_to_array(contractor, '/')) AS contractor_split
WHERE contractor LIKE '%/%'
GROUP BY TRIM(contractor_split)
ORDER BY jv_appearance_count DESC
LIMIT 10;


-- Q16: Which source_of_funds account for the highest total budget?
SELECT  source_of_funds,
        SUM(budget) AS total_budget,
        COUNT(*) AS project_count
FROM dpwh_transparency_data
GROUP BY source_of_funds
ORDER BY total_budget DESC
LIMIT 10;

-- Q17: Which source_of_funds have the highest average budget per project
-- (largest-scale individual funding, regardless of volume) add project count having?
SELECT source_of_funds,
       ROUND(AVG(budget), 2) AS avg_budget,
       COUNT(*) AS project_count
FROM dpwh_transparency_data
GROUP BY source_of_funds
ORDER BY avg_budget DESC
LIMIT 10;

-- Q18: How has total contract budget trended over time, by start year?
SELECT EXTRACT(YEAR FROM start_date) AS start_year,
       SUM(budget) AS total_budget,
       COUNT(*) AS project_count
FROM dpwh_transparency_data
WHERE start_date IS NOT NULL
GROUP BY EXTRACT(YEAR FROM start_date)
ORDER BY start_year;

-- Q19: What percentage of total national DPWH budget is held by the
-- top 10 contractors (by budget)?

WITH top_10_contractor AS (
        SELECT  contractor,
                SUM(budget) AS total_budget
        FROM dpwh_transparency_data
        GROUP BY contractor
        ORDER BY total_budget DESC
        LIMIT 10
) 


SELECT  SUM(budget) FILTER(WHERE top_10_contractor.contractor = dpwh_transparency_data.contractor) AS top_10_budget,
        SUM(budget) AS total_budget,
        ROUND( 100 * SUM(budget) FILTER(WHERE top_10_contractor.contractor = dpwh_transparency_data.contractor) / SUM(budget) ,2) AS pct_of_top_10
FROM dpwh_transparency_data, top_10_contractor



-- Q20: Which region/category combination has the highest concentration of
-- stalled contracts (progress < 50%, excluding completed/terminated)?

FROM dpwh_transparency_data



-- Q20: Which region/category combination has the highest concentration of
-- low-progress contracts (progress < 50%, excluding completed/terminated)?
SELECT region, category,
       COUNT(*) FILTER (WHERE progress < 50) AS low_progress_count,
       COUNT(*) AS total_count,
       ROUND(100.0 * COUNT(*) FILTER (WHERE progress < 50) / NULLIF(COUNT(*), 0), 2) AS pct_low_progress
FROM dpwh_transparency_data
WHERE status NOT IN ('completed', 'terminated')
GROUP BY region, category
HAVING COUNT(*) >= 5
ORDER BY pct_low_progress DESC
LIMIT 10;