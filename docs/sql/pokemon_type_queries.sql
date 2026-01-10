-- 3️⃣ Pokémon par type
SELECT
    ps.name_fr,
    t.name AS type_name,
    pt.slot
FROM pokemon p
JOIN pokemon_species ps ON ps.id = p.species_id
JOIN pokemon_type pt ON pt.pokemon_id = p.id
JOIN type t ON t.id = pt.type_id
ORDER BY ps.name_fr, pt.slot;
