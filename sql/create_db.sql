DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'pfa_user') THEN
    CREATE ROLE pfa_user
      WITH LOGIN PASSWORD 'SequelTheSecondII'  
      NOSUPERUSER NOCREATEDB NOCREATEROLE;
  END IF;
END
$$;

SELECT 'CREATE DATABASE pfa_db OWNER pfa_user'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'pfa_db')
\gexec

GRANT CONNECT ON DATABASE pfa_db TO pfa_user;
