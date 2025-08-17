-- 1) accounts: one row per bank/credit account you import
CREATE TABLE IF NOT EXISTS accounts (
    account_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,             
    institution TEXT NOT NULL,      
    currency CHAR(3) DEFAULT 'GBP', 
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE (name, institution)
);

-- 2) categories: fixed set of spending/income types
CREATE TABLE IF NOT EXISTS categories (
    category_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    kind TEXT CHECK (kind IN ('income', 'expense')) NOT NULL,
    UNIQUE (name)
);

-- 3) rules: patterns to auto-label transactions
CREATE TABLE IF NOT EXISTS rules (
    rule_id SERIAL PRIMARY KEY,
    pattern TEXT NOT NULL,
    category_id INT REFERENCES categories(category_id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE (pattern)
);

-- 4) transactions: each line from statements
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id SERIAL PRIMARY KEY,
    account_id INT REFERENCES accounts(account_id) ON DELETE CASCADE,
    txn_date DATE NOT NULL,
    description TEXT NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    balance NUMERIC(12, 2),
    category_id INT REFERENCES categories(category_id),
    import_id UUID DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Prevent duplicate transactions
ALTER TABLE transactions
    ADD CONSTRAINT ux_txn_dupe_guard
    UNIQUE (account_id, txn_date, amount, description);


INSERT INTO categories (name, kind)
VALUES
    ('Salary', 'income'),
    ('Rent', 'expense'),
    ('Groceries', 'expense'),
    ('Transport', 'expense'),
    ('Utilities', 'expense'),
    ('Subscriptions', 'expense')
ON CONFLICT DO NOTHING;
