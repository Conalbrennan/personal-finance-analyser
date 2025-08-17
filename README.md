# Personal Finance Analyser

A small end-to-end data project that imports bank statement CSVs into PostgreSQL, models them with SQL, and shows interactive insights in a Streamlit dashboard.

Skills demonstrated:  
- Python ETL (pandas + psycopg)  
- Relational database design & SQL analytics  
- Data visualisation (Altair)  
- Secure config via `.env`

---

## Features
- Load and categorise transactions using simple text rules
- Prevent duplicates with a unique constraint
- Views for:
  - Monthly totals (income, spend, net)
  - Spend by category (stacked bar chart)
  - Recurring payments
- Interactive date range selector

---

## Quick start
1. Install requirements:  
   pip install -r requirements.txt

2. Create schema & views:  
   psql -U pfa_user -h 127.0.0.1 -p 5432 -d pfa_db -f sql/create_tables.sql  
   psql -U pfa_user -h 127.0.0.1 -p 5432 -d pfa_db -f sql/seed_rules.sql  
   psql -U pfa_user -h 127.0.0.1 -p 5432 -d pfa_db -f sql/create_views.sql

3. Load sample data & apply rules:  
   python etl/import_transactions.py data/samples/sample_transactions.csv  
   python etl/apply_rules.py

4. Run dashboard:  
   streamlit run app.py

---

## Tech stack
PostgreSQL, Python, pandas, psycopg, Altair, Streamlit
