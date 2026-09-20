-- Q1 Top 10 contractors in dpwh_transparency_data by total budget(solo projects).
SELECT  contractor, 
        TO_CHAR(SUM(budget), 'FM999,999,999,999,999,990.00') AS total_budget,
        COUNT(*) AS project_count
FROM dpwh_transparency_data
GROUP BY contractor
ORDER BY SUM(budget) DESC
LIMIT 10;

-- Q2 Top 10 contractors in flood_control by total contract cost(solo projects) TODO: contract_cost to budget.
SELECT  contractor, 
        TO_CHAR(SUM(contract_cost), 'FM999,999,999,999,999,990.00') AS total_budget,
        COUNT(*) AS project_count
FROM flood_control
GROUP BY contractor
ORDER BY SUM(contract_cost) DESC
LIMIT 10;

-- Q3 Top 10 categories by number of projects (component_category).
SELECT  component_category_table.component_category, 
        TO_CHAR(SUM(budget), 'FM999,999,999,999,999,990.00') AS total_budget,
        COUNT(dpwh_transparency_data.contract_id) AS project_count
FROM dpwh_transparency_data
INNER JOIN component_category_table ON dpwh_transparency_data.contract_id = component_category_table.contract_id
GROUP BY component_category_table.component_category
ORDER BY project_count DESC
LIMIT 10;

-- Q4 Top 10 categories by total budget.
SELECT  component_category_table.component_category, 
        TO_CHAR(SUM(budget), 'FM999,999,999,999,999,990.00') AS total_budget,
        COUNT(dpwh_transparency_data.contract_id) AS project_count
FROM dpwh_transparency_data
INNER JOIN component_category_table ON dpwh_transparency_data.contract_id = component_category_table.contract_id
GROUP BY component_category_table.component_category
ORDER BY SUM(budget) DESC
LIMIT 10;

-- Q5 Top 10 organizations (philgeps) by total contract_amount awarded.
SELECT organization_name,
        TO_CHAR(SUM(contract_amount), 'FM999,999,999,999,999,990.00') AS total_contract_amount,
        COUNT(*) AS project_count
FROM philgeps
GROUP BY organization_name
ORDER BY SUM(contract_amount) DESC
LIMIT 10;

-- Q6 Top 10 awardees (philgeps) by total contract_amount received.
SELECT awardee_name,
        TO_CHAR(SUM(contract_amount), 'FM999,999,999,999,999,990.00') AS total_contract_amount,
        COUNT(*) AS project_count
FROM philgeps
GROUP BY awardee_name
ORDER BY SUM(contract_amount) DESC
LIMIT 10;

-- Q7 Top 10 regions by total DPWH budget TODO change to just rank.
SELECT region, 
        TO_CHAR(SUM(budget), 'FM999,999,999,999,999,990.00') AS total_budget,
        COUNT(*) AS project_count
FROM dpwh_transparency_data
GROUP BY region
ORDER BY SUM(budget) DESC
LIMIT 10;

-- Q8 Top 10 provinces by number of flood control projects.
SELECT province, 
        TO_CHAR(SUM(contract_cost), 'FM999,999,999,999,999,990.00') AS total_budget,
        COUNT(*) AS project_count
FROM flood_control
GROUP BY province
ORDER BY project_count DESC
LIMIT 10;

-- Q9 (revised): Top 10 source_of_funds by total budget in dpwh_transparency_data
SELECT source_of_funds,
        TO_CHAR(SUM(budget), 'FM999,999,999,999,999,990.00') AS total_budget,
COUNT(*) AS project_count
FROM dpwh_transparency_data
GROUP BY source_of_funds
ORDER BY SUM(budget) DESC
LIMIT 10;

-- Q10 Top 10 business_categories in PhilGEPS by total contract_amount.
SELECT business_category,
        TO_CHAR(SUM(contract_amount), 'FM999,999,999,999,999,990.00') AS total_contract_amount,
        COUNT(*) AS project_count
FROM philgeps
GROUP BY business_category
ORDER BY SUM(contract_amount) DESC
LIMIT 10;