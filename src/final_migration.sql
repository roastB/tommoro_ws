-- ===========================================
-- 🚀 Perfect Data Migration Script (Final Version)
-- ===========================================

-- 1. 기초 데이터 세팅 (로봇 및 Tasks)
INSERT INTO robots (robot_id, model_name, status) VALUES
    (1, 'RB-Y1', 'active'),
    (2, 'AI-Worker', 'active')
ON CONFLICT DO NOTHING;

INSERT INTO tasks (project_id, task_name)
SELECT project_id, project_name || ' Default Task' FROM projects
WHERE NOT EXISTS (SELECT 1 FROM tasks WHERE tasks.project_id = projects.project_id);

-- 2. Logs Data (Subtasks & Subtask_logs) 삽입

-- Data Row 1: Amore sunscreen soyoung (2026-02-13)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Amore sunscreen soyoung' LIMIT 1),
    '2026-02-13',
    '조성현',
    'Epi(0) * Avg(50s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    0,
    0.0
);

-- Data Row 2: Habilis beta deodorant (2026-02-12)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis beta deodorant' LIMIT 1),
    '2026-02-12',
    '조성현',
    'Epi(126) * Avg(70s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    8820,
    0.0
);

-- Data Row 3: Habilis beta deodorant (2026-02-11)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis beta deodorant' LIMIT 1),
    '2026-02-11',
    '조성현',
    'Epi(56) * Avg(70s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    3920,
    0.0
);

-- Data Row 4: Habilis beta deodorant (2026-02-10)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis beta deodorant' LIMIT 1),
    '2026-02-10',
    '조성현',
    'Epi(10) * Avg(70s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    700,
    0.0
);

-- Data Row 5: Amore sunscreen soyoung (2026-02-06)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Amore sunscreen soyoung' LIMIT 1),
    '2026-02-06',
    '조성현',
    'Epi(25) * Avg(50s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    1250,
    0.0
);

-- Data Row 6: Habilis beta deodorant (2026-02-05)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis beta deodorant' LIMIT 1),
    '2026-02-05',
    '조성현',
    'Epi(33) * Avg(70s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    2310,
    0.0
);

-- Data Row 7: Amore sunscreen soyoung (2026-02-05)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Amore sunscreen soyoung' LIMIT 1),
    '2026-02-05',
    '조성현',
    'Epi(12) * Avg(50s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    600,
    0.0
);

-- Data Row 8: Habilis beta deodorant (2026-02-04)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis beta deodorant' LIMIT 1),
    '2026-02-04',
    '조성현',
    'Epi(147) * Avg(70s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    10290,
    1.0
);

-- Data Row 9: Amore v8 (3-1) (2026-01-27)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Amore v8 (3-1)' LIMIT 1),
    '2026-01-27',
    '조성현',
    'Epi(130) * Avg(55s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    7150,
    1.0
);

-- Data Row 10: Amore v8 (3-1) (2026-01-26)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Amore v8 (3-1)' LIMIT 1),
    '2026-01-26',
    '조성현',
    'Epi(38) * Avg(55s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    2090,
    1.0
);

-- Data Row 11: Amore v8 (3-1) (2026-01-23)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Amore v8 (3-1)' LIMIT 1),
    '2026-01-23',
    '조성현',
    'Epi(41) * Avg(55s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    2255,
    1.0
);

-- Data Row 12: Amore v8 (3-1) (2026-01-22)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Amore v8 (3-1)' LIMIT 1),
    '2026-01-22',
    '조성현',
    'Epi(43) * Avg(55s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    2365,
    1.0
);

-- Data Row 13: Amore v8 (3-1) (2026-01-21)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Amore v8 (3-1)' LIMIT 1),
    '2026-01-21',
    '조성현',
    'Epi(20) * Avg(55s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    1100,
    1.0
);

-- Data Row 14: Amore v7 (4-1) (2026-01-21)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Amore v7 (4-1)' LIMIT 1),
    '2026-01-21',
    '조성현',
    'Epi(79) * Avg(55s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    4345,
    1.0
);

-- Data Row 15: Amore v7 (4-1) (2026-01-20)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Amore v7 (4-1)' LIMIT 1),
    '2026-01-20',
    '조성현',
    'Epi(170) * Avg(55s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    9350,
    1.0
);

-- Data Row 16: Amore v6 (5-1) (2026-01-19)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Amore v6 (5-1)' LIMIT 1),
    '2026-01-19',
    '조성현',
    'Epi(200) * Avg(55s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    11000,
    1.0
);

-- Data Row 17: Habilis beta v4 (2026-01-16)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis beta v4' LIMIT 1),
    '2026-01-16',
    '조성현',
    'Epi(35) * Avg(100s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    3500,
    1.0
);

-- Data Row 18: Habilis beta v4 (2026-01-16)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis beta v4' LIMIT 1),
    '2026-01-16',
    '조성현',
    'Epi(81) * Avg(100s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    8100,
    1.0
);

-- Data Row 19: Habilis beta Play (Picking_Daiso-Left, Daiso-Right) (2026-01-15)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis beta Play (Picking_Daiso-Left, Daiso-Right)' LIMIT 1),
    '2026-01-15',
    '조성현',
    'Epi(80) * Avg(180s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    14400,
    1.0
);

-- Data Row 20: Habilis beta v4 (2026-01-14)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis beta v4' LIMIT 1),
    '2026-01-14',
    '조성현',
    'Epi(133) * Avg(100s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    13300,
    1.0
);

-- Data Row 21: Habilis beta v4 (2026-01-13)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis beta v4' LIMIT 1),
    '2026-01-13',
    '조성현',
    'Epi(120) * Avg(100s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    12000,
    1.0
);

-- Data Row 22: Habilis beta Play (Picking_Amore) (2026-01-12)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis beta Play (Picking_Amore)' LIMIT 1),
    '2026-01-12',
    '조성현',
    'Epi(13) * Avg(180s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    2340,
    0.0
);

-- Data Row 23: Habilis beta Play (Picking_Amore) (2026-01-12)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis beta Play (Picking_Amore)' LIMIT 1),
    '2026-01-12',
    '조성현',
    'Epi(9) * Avg(180s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    1620,
    0.0
);

-- Data Row 24: Habilis beta Play (Picking_jam+tube) (2026-01-09)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis beta Play (Picking_jam+tube)' LIMIT 1),
    '2026-01-09',
    '조성현',
    'Epi(4) * Avg(180s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    720,
    0.0
);

-- Data Row 25: Amore v2-1 (2026-01-09)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Amore v2-1' LIMIT 1),
    '2026-01-09',
    '조성현',
    'Epi(134) * Avg(56s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    7504,
    0.0
);

-- Data Row 26: Amore v5 (2026-01-08)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Amore v5' LIMIT 1),
    '2026-01-08',
    '조성현',
    'Epi(236) * Avg(50s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    11800,
    0.0
);

-- Data Row 27: Amore v5 (2026-01-07)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Amore v5' LIMIT 1),
    '2026-01-07',
    '조성현',
    'Epi(51) * Avg(50s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    2550,
    0.0
);

-- Data Row 28: Amore v4 (2026-01-07)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Amore v4' LIMIT 1),
    '2026-01-07',
    '조성현',
    'Epi(210) * Avg(60s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    12600,
    0.0
);

-- Data Row 29: Habilis beta Play (Picking_jam+tube) (2026-01-06)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis beta Play (Picking_jam+tube)' LIMIT 1),
    '2026-01-06',
    '조성현',
    'Epi(37) * Avg(180s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    6660,
    0.0
);

-- Data Row 30: Amore v3 (2026-01-06)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Amore v3' LIMIT 1),
    '2026-01-06',
    '조성현',
    'Epi(55) * Avg(60s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    3300,
    1.0
);

-- Data Row 31: Amore v3 (2026-01-05)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Amore v3' LIMIT 1),
    '2026-01-05',
    '조성현',
    'Epi(125) * Avg(60s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    7500,
    1.0
);

-- Data Row 32: Amore v2 (2026-01-02)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Amore v2' LIMIT 1),
    '2026-01-02',
    '조성현',
    'Epi(79) * Avg(60s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    4740,
    1.0
);

-- Data Row 33: Amore v2 (2025-12-31)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Amore v2' LIMIT 1),
    '2025-12-31',
    '조성현',
    'Epi(125) * Avg(60s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    7500,
    1.0
);

-- Data Row 34: Amore v2 (2025-12-30)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Amore v2' LIMIT 1),
    '2025-12-30',
    '조성현',
    'Epi(100) * Avg(60s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    6000,
    1.0
);

-- Data Row 35: CES2026 v7 (Backup) (2025-12-29)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'CES2026 v7 (Backup)' LIMIT 1),
    '2025-12-29',
    '한준모',
    'Epi(100) * Avg(60s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    6000,
    1.0
);

-- Data Row 36: CES2026 v4,5,6 (2025-12-26)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'CES2026 v4,5,6' LIMIT 1),
    '2025-12-26',
    '한준모',
    'Epi(50) * Avg(35s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    1750,
    1.0
);

-- Data Row 37: Amore v1 (2025-12-24)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Amore v1' LIMIT 1),
    '2025-12-24',
    '한준모',
    'Epi(7) * Avg(60s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    420,
    1.0
);

-- Data Row 38: CES2026 v4,5,6 (2025-12-24)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'CES2026 v4,5,6' LIMIT 1),
    '2025-12-24',
    '한준모',
    'Epi(33) * Avg(35s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    1155,
    1.0
);

-- Data Row 39: CES2026 v4,5,6 (2025-12-23)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'CES2026 v4,5,6' LIMIT 1),
    '2025-12-23',
    '한준모',
    'Epi(37) * Avg(35s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    1295,
    1.0
);

-- Data Row 40: Amore v1 (2025-12-23)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Amore v1' LIMIT 1),
    '2025-12-23',
    '한준모',
    'Epi(75) * Avg(60s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    4500,
    1.0
);

-- Data Row 41: Amore v1 (2025-12-22)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Amore v1' LIMIT 1),
    '2025-12-22',
    '한준모',
    'Epi(101) * Avg(60s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    6060,
    1.0
);

-- Data Row 42: Amore v1 (2025-12-19)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Amore v1' LIMIT 1),
    '2025-12-19',
    '한준모',
    'Epi(16) * Avg(60s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    960,
    1.0
);

-- Data Row 43: Habilis Beta v2 (2025-12-19)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis Beta v2' LIMIT 1),
    '2025-12-19',
    '한준모',
    'Epi(281) * Avg(60s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    16860,
    1.0
);

-- Data Row 44: Habilis Beta v2 (2025-12-18)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis Beta v2' LIMIT 1),
    '2025-12-18',
    '한준모',
    'Epi(259) * Avg(60s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    15540,
    1.0
);

-- Data Row 45: Habilis Beta v2 (2025-12-17)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis Beta v2' LIMIT 1),
    '2025-12-17',
    '한준모',
    'Epi(186) * Avg(60s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    11160,
    1.0
);

-- Data Row 46: Habilis Beta v2 (2025-12-16)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis Beta v2' LIMIT 1),
    '2025-12-16',
    '한준모',
    'Epi(210) * Avg(60s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    12600,
    1.0
);

-- Data Row 47: Habilis Beta v2 (2025-12-16)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis Beta v2' LIMIT 1),
    '2025-12-16',
    '한준모',
    'Epi(16) * Avg(60s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    960,
    1.0
);

-- Data Row 48: Habilis Beta v2 (2025-12-16)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis Beta v2' LIMIT 1),
    '2025-12-16',
    '한준모',
    'Epi(0) * Avg(60s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    0,
    1.0
);

-- Data Row 49: Habilis Beta v2 (2025-12-15)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis Beta v2' LIMIT 1),
    '2025-12-15',
    '한준모',
    'Epi(112) * Avg(60s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    6720,
    1.0
);

-- Data Row 50: Habilis Beta v2 (2025-12-15)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis Beta v2' LIMIT 1),
    '2025-12-15',
    '한준모',
    'Epi(209) * Avg(60s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    12540,
    1.0
);

-- Data Row 51: Habilis Beta v2 (2025-12-12)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis Beta v2' LIMIT 1),
    '2025-12-12',
    '한준모',
    'Epi(53) * Avg(60s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    3180,
    1.0
);

-- Data Row 52: Habilis Beta v2 (2025-12-12)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis Beta v2' LIMIT 1),
    '2025-12-12',
    '한준모',
    'Epi(172) * Avg(60s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    10320,
    1.0
);

-- Data Row 53: Habilis Beta v2 (2025-12-11)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis Beta v2' LIMIT 1),
    '2025-12-11',
    '한준모',
    'Epi(34) * Avg(60s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    2040,
    1.0
);

-- Data Row 54: Habilis Beta v2 (2025-12-11)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis Beta v2' LIMIT 1),
    '2025-12-11',
    '한준모',
    'Epi(67) * Avg(60s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    4020,
    1.0
);

-- Data Row 55: Habilis Beta v2 (2025-12-10)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis Beta v2' LIMIT 1),
    '2025-12-10',
    '한준모',
    'Epi(72) * Avg(60s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    4320,
    1.0
);

-- Data Row 56: Habilis Beta v2 (2025-12-09)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis Beta v2' LIMIT 1),
    '2025-12-09',
    '한준모',
    'Epi(166) * Avg(60s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    9960,
    1.0
);

-- Data Row 57: Habilis Beta v2 (2025-12-08)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis Beta v2' LIMIT 1),
    '2025-12-08',
    '한준모',
    'Epi(95) * Avg(60s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    5700,
    1.0
);

-- Data Row 58: CES2026 v2 (2025-12-05)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'CES2026 v2' LIMIT 1),
    '2025-12-05',
    '한준모',
    'Epi(0) * Avg(60s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    0,
    1.0
);

-- Data Row 59: Habilis Beta v2 (2025-12-05)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis Beta v2' LIMIT 1),
    '2025-12-05',
    '한준모',
    'Epi(0) * Avg(60s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    0,
    1.0
);

-- Data Row 60: CES2026 v2 (2025-12-04)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'CES2026 v2' LIMIT 1),
    '2025-12-04',
    '한준모',
    'Epi(29) * Avg(60s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    1740,
    1.0
);

-- Data Row 61: Habilis Beta v2 (2025-12-04)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis Beta v2' LIMIT 1),
    '2025-12-04',
    '한준모',
    'Epi(96) * Avg(60s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    5760,
    1.0
);

-- Data Row 62: Habilis Beta v2 (2025-12-03)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis Beta v2' LIMIT 1),
    '2025-12-03',
    '한준모',
    'Epi(1) * Avg(60s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    60,
    1.0
);

-- Data Row 63: Habilis Beta v2 (2025-12-02)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis Beta v2' LIMIT 1),
    '2025-12-02',
    '한준모',
    'Epi(18) * Avg(60s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    1080,
    1.0
);

-- Data Row 64: Habilis Beta v2 (2025-12-01)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis Beta v2' LIMIT 1),
    '2025-12-01',
    '한준모',
    'Epi(30) * Avg(60s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    1800,
    1.0
);

-- Data Row 65: Habilis Beta v2 (2025-11-28)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis Beta v2' LIMIT 1),
    '2025-11-28',
    '한준모',
    'Epi(135) * Avg(60s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    8100,
    1.0
);

-- Data Row 66: Habilis Beta v2 (2025-11-27)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis Beta v2' LIMIT 1),
    '2025-11-27',
    '한준모',
    'Epi(121) * Avg(60s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    7260,
    1.0
);

-- Data Row 67: CES2026 v1 (2025-11-26)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'CES2026 v1' LIMIT 1),
    '2025-11-26',
    '한준모',
    'Epi(1) * Avg(65s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    65,
    1.0
);

-- Data Row 68: CES2026 v1 (2025-11-25)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'CES2026 v1' LIMIT 1),
    '2025-11-25',
    '한준모',
    'Epi(300) * Avg(65s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    19500,
    1.0
);

-- Data Row 69: CES2026 v1 (2025-11-24)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'CES2026 v1' LIMIT 1),
    '2025-11-24',
    '한준모',
    'Epi(217) * Avg(65s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    14105,
    1.0
);

-- Data Row 70: CES2026 v1 (2025-11-21)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'CES2026 v1' LIMIT 1),
    '2025-11-21',
    '한준모',
    'Epi(201) * Avg(65s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    13065,
    1.0
);

-- Data Row 71: CES2026 v1 (2025-11-20)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'CES2026 v1' LIMIT 1),
    '2025-11-20',
    '한준모',
    'Epi(1) * Avg(65s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    65,
    1.0
);

-- Data Row 72: Habilis Beta v1 (2025-11-19)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis Beta v1' LIMIT 1),
    '2025-11-19',
    '한준모',
    'Epi(1) * Avg(90s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    90,
    1.0
);

-- Data Row 73: Habilis Beta v1 (2025-11-18)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis Beta v1' LIMIT 1),
    '2025-11-18',
    '한준모',
    'Epi(1) * Avg(90s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    90,
    1.0
);

-- Data Row 74: Habilis Beta v1 (2025-11-17)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis Beta v1' LIMIT 1),
    '2025-11-17',
    '한준모',
    'Epi(1) * Avg(90s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    90,
    1.0
);

-- Data Row 75: Habilis Beta v1 (2025-11-14)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis Beta v1' LIMIT 1),
    '2025-11-14',
    '한준모',
    'Epi(0) * Avg(90s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    0,
    1.0
);

-- Data Row 76: Habilis Beta v1 (2025-11-13)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis Beta v1' LIMIT 1),
    '2025-11-13',
    '한준모',
    'Epi(3) * Avg(90s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    270,
    1.0
);

-- Data Row 77: Habilis Beta v1 (2025-11-12)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis Beta v1' LIMIT 1),
    '2025-11-12',
    '한준모',
    'Epi(0) * Avg(90s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    0,
    1.0
);

-- Data Row 78: Habilis Beta v1 (2025-11-11)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'Habilis Beta v1' LIMIT 1),
    '2025-11-11',
    '한준모',
    'Epi(0) * Avg(90s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    0,
    1.0
);

-- Data Row 79: BI_aloha_data (2025-01-01)
INSERT INTO subtasks (task_id, subtask_date, collector_main, instruction)
VALUES (
    (SELECT t.task_id FROM tasks t JOIN projects p ON t.project_id = p.project_id WHERE p.project_name = 'BI_aloha_data' LIMIT 1),
    '2025-01-01',
    '박진우',
    'Epi(2335) * Avg(30s)'
);

INSERT INTO subtask_logs (subtask_id, robot_id, duration, quality_score)
VALUES (
    currval('subtasks_subtask_id_seq'),
    1,
    70050,
    1.0
);

