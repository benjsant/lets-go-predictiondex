BEGIN;

-- =========================
-- TABLE : pokemon
-- =========================
CREATE TABLE IF NOT EXISTS pokemon (
    pokemon_id SERIAL PRIMARY KEY,
    num_pokedex INTEGER NOT NULL,
    nom_fr VARCHAR(75) NOT NULL,
    nom_en VARCHAR(75),
    is_alola BOOLEAN NOT NULL DEFAULT false,
    is_mega BOOLEAN NOT NULL DEFAULT false,
    height_m DECIMAL(5,2) NOT NULL CHECK (height_m > 0),
    weight_kg DECIMAL(5,2) NOT NULL CHECK (weight_kg > 0),
    sprite_url TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- TABLE : pokemon_stat
-- =========================
CREATE TABLE IF NOT EXISTS pokemon_stat (
    pokemon_id INTEGER PRIMARY KEY,
    hp INTEGER NOT NULL CHECK (hp >= 1),
    attack INTEGER NOT NULL CHECK (attack >= 1),
    defense INTEGER NOT NULL CHECK (defense >= 1),
    sp_attack INTEGER NOT NULL CHECK (sp_attack >= 1),
    sp_defense INTEGER NOT NULL CHECK (sp_defense >= 1),
    speed INTEGER NOT NULL CHECK (speed >= 1),
    CONSTRAINT fk_pokemon_stat
        FOREIGN KEY (pokemon_id)
        REFERENCES pokemon (pokemon_id)
        ON DELETE CASCADE
);

-- =========================
-- TABLE : type
-- =========================
CREATE TABLE IF NOT EXISTS type (
    type_id SERIAL PRIMARY KEY,
    name_fr VARCHAR(50) NOT NULL UNIQUE,
    name_en VARCHAR(50)
);

-- =========================
-- TABLE : move
-- =========================
CREATE TABLE IF NOT EXISTS move (
    move_id SERIAL PRIMARY KEY,
    name_fr VARCHAR(100) NOT NULL,
    name_en VARCHAR(100),
    power INTEGER CHECK (power >= 1),
    accuracy INTEGER CHECK (accuracy BETWEEN 1 AND 100),
    description TEXT,
    category VARCHAR(20) NOT NULL,
    type_id INTEGER NOT NULL,
    CONSTRAINT fk_move_type
        FOREIGN KEY (type_id)
        REFERENCES type (type_id)
);

-- =========================
-- TABLE : learn_method
-- =========================
CREATE TABLE IF NOT EXISTS learn_method (
    method_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

-- =========================
-- TABLE : pokemon_move
-- =========================
CREATE TABLE IF NOT EXISTS pokemon_move (
    pokemon_id INTEGER NOT NULL,
    move_id INTEGER NOT NULL,
    learn_method_id INTEGER NOT NULL,
    learn_level INTEGER CHECK (learn_level >= 1),
    PRIMARY KEY (pokemon_id, move_id, learn_method_id),
    CONSTRAINT fk_pm_pokemon
        FOREIGN KEY (pokemon_id)
        REFERENCES pokemon (pokemon_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_pm_move
        FOREIGN KEY (move_id)
        REFERENCES move (move_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_pm_method
        FOREIGN KEY (learn_method_id)
        REFERENCES learn_method (method_id)
);

-- =========================
-- TABLE : pokemon_type
-- =========================
CREATE TABLE IF NOT EXISTS pokemon_type (
    pokemon_id INTEGER NOT NULL,
    type_id INTEGER NOT NULL,
    slot INTEGER NOT NULL CHECK (slot IN (1, 2)),
    PRIMARY KEY (pokemon_id, slot),
    CONSTRAINT uq_pokemon_type UNIQUE (pokemon_id, type_id),
    CONSTRAINT fk_pt_pokemon
        FOREIGN KEY (pokemon_id)
        REFERENCES pokemon (pokemon_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_pt_type
        FOREIGN KEY (type_id)
        REFERENCES type (type_id)
);

-- =========================
-- TABLE : type_effectiveness
-- =========================
CREATE TABLE IF NOT EXISTS type_effectiveness (
    attacking_type_id INTEGER NOT NULL,
    defending_type_id INTEGER NOT NULL,
    multiplier DECIMAL(3,2) NOT NULL
        CHECK (multiplier IN (0, 0.25, 0.5, 1, 2, 4)),
    PRIMARY KEY (attacking_type_id, defending_type_id),
    CONSTRAINT fk_te_attack
        FOREIGN KEY (attacking_type_id)
        REFERENCES type (type_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_te_defense
        FOREIGN KEY (defending_type_id)
        REFERENCES type (type_id)
        ON DELETE CASCADE
);

COMMIT;
