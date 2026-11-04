-- OPTIONAL: execute as a MySQL administrator. Modify the password BEFORE use.
-- If you already have an appropriate user, skip this script.
-- Do not grant these privileges on other databases.
-- The example user intentionally has NO CREATE/DROP/ALTER privileges.
CREATE USER IF NOT EXISTS 'chapter9_app'@'localhost'
    IDENTIFIED BY 'REPLACE_WITH_A_STRONG_LOCAL_PASSWORD';
GRANT SELECT, INSERT, UPDATE, DELETE ON MyUniversityDB.*
    TO 'chapter9_app'@'localhost';
-- For remote hosts, your MySQL user host pattern may need adjustment.
