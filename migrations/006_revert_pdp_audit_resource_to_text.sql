ALTER TABLE pdp_audit
ALTER COLUMN resource TYPE TEXT
USING resource[1];