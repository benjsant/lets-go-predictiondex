-- 2️⃣ Capacités par Pokémon
SELECT
    ps.name_fr AS pokemon_name,
    m.name AS move_name,
    pm.level,
    lm.name AS learn_method
FROM pokemon_move pm
JOIN pokemon p ON p.id = pm.pokemon_id
JOIN pokemon_species ps ON ps.id = p.species_id
JOIN move m ON m.id = pm.move_id
JOIN learn_method lm ON lm.id = pm.learn_method_id
ORDER BY ps.name_fr, pm.level;
