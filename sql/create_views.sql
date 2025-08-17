-- 1) Monthly totals: income, spend, net
CREATE OR REPLACE VIEW v_monthly_totals AS
SELECT
  date_trunc('month', txn_date)::date AS month,
  SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS income,
  SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END) AS spend,
  SUM(amount) AS net
FROM transactions
GROUP BY 1
ORDER BY 1;

-- 2) Spend by category per month
-- Only shows rows where a category exists.
CREATE OR REPLACE VIEW v_spend_by_category_month AS
SELECT
  date_trunc('month', t.txn_date)::date AS month,
  c.name AS category,
  SUM(t.amount) AS total
FROM transactions t
JOIN categories c ON c.category_id = t.category_id
GROUP BY 1, 2
HAVING SUM(t.amount) <> 0
ORDER BY 1, 2;

-- 3) Recurring candidates
-- Looks for descriptions that occur in >= 3 different months. Splits income vs expense to avoid mixing salary with outgoings.
CREATE OR REPLACE VIEW v_recurring_candidates AS
WITH tagged AS (
  SELECT
    LEFT(TRIM(description), 40) AS merchant,  -- short label
    CASE WHEN amount > 0 THEN 'income' ELSE 'expense' END AS kind,
    date_trunc('month', txn_date)::date AS month,
    COUNT(*) AS n_txn,
    ROUND(AVG(amount), 2) AS avg_amount
  FROM transactions
  GROUP BY 1, 2, 3
),
by_merchant AS (
  SELECT
    merchant, kind,
    COUNT(DISTINCT month) AS months_seen,
    ROUND(AVG(avg_amount), 2) AS avg_amount
  FROM tagged
  GROUP BY 1, 2
)
SELECT merchant, kind, months_seen, avg_amount
FROM by_merchant
WHERE months_seen >= 2
ORDER BY kind, merchant;
