-- ======================================================
-- Capacités : extraction des attaques
-- ======================================================

-- 1️⃣ Liste des capacités
SELECT
    m.id,
    m.name,
    t.name AS type,
    m.category,
    m.power,
    m.accuracy
FROM move m
JOIN type t ON t.id = m.type_id
ORDER BY m.name;
