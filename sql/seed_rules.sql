-- Map common merchants/keywords to categories by name
INSERT INTO rules (pattern, category_id)
SELECT 'TESCO', c.category_id FROM categories c WHERE c.name = 'Groceries'
ON CONFLICT (pattern) DO NOTHING;

INSERT INTO rules (pattern, category_id)
SELECT 'SAINSBURY', c.category_id FROM categories c WHERE c.name = 'Groceries'
ON CONFLICT (pattern) DO NOTHING;

INSERT INTO rules (pattern, category_id)
SELECT 'AMAZON', c.category_id FROM categories c WHERE c.name = 'Subscriptions'
ON CONFLICT (pattern) DO NOTHING;

INSERT INTO rules (pattern, category_id)
SELECT 'NETFLIX', c.category_id FROM categories c WHERE c.name = 'Subscriptions'
ON CONFLICT (pattern) DO NOTHING;

INSERT INTO rules (pattern, category_id)
SELECT 'SPOTIFY', c.category_id FROM categories c WHERE c.name = 'Subscriptions'
ON CONFLICT (pattern) DO NOTHING;

INSERT INTO rules (pattern, category_id)
SELECT 'UBER', c.category_id FROM categories c WHERE c.name = 'Transport'
ON CONFLICT (pattern) DO NOTHING;

INSERT INTO rules (pattern, category_id)
SELECT 'TRANSPORT FOR LONDON', c.category_id FROM categories c WHERE c.name = 'Transport'
ON CONFLICT (pattern) DO NOTHING;

INSERT INTO rules (pattern, category_id)
SELECT 'SALARY', c.category_id FROM categories c WHERE c.name = 'Salary'
ON CONFLICT (pattern) DO NOTHING;
