DROP TABLE IF EXISTS remnants_materials;
REASSIGN OWNED BY robot TO postgres;
DROP OWNED BY robot;
DROP ROLE IF EXISTS robot;
CREATE TABLE remnants_materials (
    article TEXT PRIMARY KEY,
    remainder INTEGER NOT NULL DEFAULT 0,
    minimum_threshold INTEGER NOT NULL DEFAULT 0,
    max_capacity INTEGER NOT NULL DEFAULT 100 
);

INSERT INTO remnants_materials (article, remainder, minimum_threshold, max_capacity)
VALUES
    ('BLT000101', 45, 20, 100),
    ('BLT000102', 12, 15, 100),
    ('BLT000103', 0, 25, 100),
    ('NUT000201', 88, 30, 100),
    ('NUT000202', 5, 10, 100),
    ('WAS000301', 200, 50, 300), 
    ('WAS000302', 77, 20, 300),
    ('SCR000401', 33, 15, 100),
    ('SCR000402', 2, 5, 100),
    ('PIN000501', 150, 40, 200),
    ('PIN000502', 0, 10, 200),
    ('STU000601', 67, 25, 150),
    ('STU000602', 9, 12, 150),
    ('RIV000701', 40, 18, 100),
    ('RIV000702', 1, 3, 100),
    ('KEY000801', 25, 8, 50),
    ('KEY000802', 0, 5, 50),
    ('WEL000901', 120, 35, 200),
    ('WEL000902', 18, 20, 200),
    ('SPR001001', 55, 15, 100);
CREATE USER robot WITH PASSWORD 'iamrobot';
GRANT ALL PRIVILEGES ON DATABASE krep_db TO robot;
GRANT ALL PRIVILEGES ON TABLE remnants_materials TO robot;
GRANT USAGE ON SCHEMA public TO robot;