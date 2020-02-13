CREATE USER django WITH ENCRYPTED PASSWORD 'qwerty';
GRANT CONNECT ON DATABASE surf TO django;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO django;
ALTER DEFAULT PRIVILEGES FOR USER django IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO django;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO django;
