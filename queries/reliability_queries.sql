-- Q11: Among the top 10 contractors (by budget), which have the highest count of
-- contracts past completion_date but progress < 100% (delay flags)?


-- Q12: Across all contractors, which have the highest percentage of contracts
-- flagged as delayed (past completion_date, progress < 100%)?


-- Q13: Which contracts are marked status = 'completed' but have progress < 100%
-- (data-integrity / reporting red flag)?


-- Q14: Which contractors have the most contracts where amount_paid exceeds budget
-- (potential overpayment)?


-- Q15: What's the average overdue duration (today - completion_date) for still
-- incomplete contracts, grouped by contractor, for the top 10 by budget?