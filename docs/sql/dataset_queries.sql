-- ======================================================
-- Dataset final agrégé
-- ======================================================

SELECT
    ps.pokedex_number,
    ps.name_fr,
    t1.name AS primary_type,
    t2.name AS secondary_type,
    s.hp,
    s.attack,
    s.defense,
    s.sp_attack,
    s.sp_defense,
    s.speed
FROM pokemon p
JOIN pokemon_species ps ON ps.id = p.species_id
JOIN pokemon_stat s ON s.pokemon_id = p.id
LEFT JOIN pokemon_type pt1 ON pt1.pokemon_id = p.id AND pt1.slot = 1
LEFT JOIN pokemon_type pt2 ON pt2.pokemon_id = p.id AND pt2.slot = 2
LEFT JOIN type t1 ON t1.id = pt1.type_id
LEFT JOIN type t2 ON t2.id = pt2.type_id;
