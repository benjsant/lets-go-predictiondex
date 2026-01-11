# Pokémon Let’s Go – PredictionDex

## 📌 Présentation du projet

**PredictionDex** est un projet complet de data engineering et d’API backend autour de *Pokémon Let’s Go Pikachu & Évoli*.

L’objectif est de construire **une base de données fiable et exploitable**, enrichie à partir de plusieurs sources (CSV, PokéAPI, Poképédia), puis d’exposer ces données via **une API REST moderne**.

Le projet couvre l’ensemble d’un pipeline **ETL → stockage → exposition API**, avec une architecture pensée pour être claire, testable et évolutive.

---

## 🎯 Objectifs pédagogiques

* Mettre en place un **pipeline ETL complet**
* Concevoir un **schéma relationnel cohérent**
* Implémenter une **API REST avec FastAPI**
* Séparer clairement **modèles, schémas, services et routes**
* Préparer un projet conforme aux exigences **E1 / E3**

---

## 🧱 Architecture générale

```
ETL
 ├── CSV (données statiques)
 ├── PokéAPI (stats, taille, poids, sprites)
 ├── Poképédia (scraping des capacités LGPE)
 └── Scripts Python orchestrés (run_all_in_one.py)

Base de données (PostgreSQL)
 └── Modèles SQLAlchemy normalisés

API REST (FastAPI)
 ├── Routes
 ├── Services
 ├── Schémas Pydantic
 └── Accès DB sécurisé
```

---

## 🗂️ Arborescence du projet (simplifiée)

```
app/
├── api/
│   ├── main.py
│   ├── routes/
│   └── services/
├── db/
│   ├── guards/
│   ├── base.py
│   └── session.py
├── models/
├── schemas/
├── scripts/
│   ├── init_db.py
│   ├── load_all_csv.py
│   ├── load_pokeapi.py
│   └── inherit_mega_moves.py
├── pokepedia_scraper/
└── run_all_in_one.py
```

---

## 🔄 Pipeline ETL

### 1️⃣ Initialisation de la base

* Création des tables
* Insertion des tables de référence (types, learn methods, etc.)

### 2️⃣ Chargement CSV

* Pokémon (espèces et formes)
* Capacités
* Relations Pokémon ↔ capacités

### 3️⃣ Enrichissement PokéAPI

* Statistiques
* Taille / poids
* Sprites

### 4️⃣ Scraping Poképédia

* Capacités spécifiques Let’s Go
* Méthodes d’apprentissage

### 5️⃣ Post-traitement

* Héritage des capacités Méga

L’ensemble est orchestré via :

```bash
python run_all_in_one.py
```

---

## 🌐 API REST

### Endpoints principaux

#### Pokémon

* `GET /pokemon/` → liste des Pokémon
* `GET /pokemon/{id}` → détail d’un Pokémon

#### Capacités

* `GET /moves/` → liste des capacités
* `GET /moves/{id}` → détail d’une capacité

#### Types

* `GET /types/`

---

## 🧩 Modèles & Schémas

* **SQLAlchemy** : gestion de la persistance
* **Pydantic** : validation et sérialisation des réponses API
* Séparation stricte entre **modèles DB** et **schémas API**

---

## 🐳 Lancement avec Docker

```bash
docker-compose up --build
```

Accès à l’API :

* [http://localhost:8000](http://localhost:8000)
* Swagger : [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Tests (à venir)

Des tests unitaires seront ajoutés pour :

* les guards DB
* les services API
* les scripts ETL critiques

---

## 🚀 Améliorations possibles

* Passage partiel en asynchrone
* Pagination des endpoints
* Monitoring (Prometheus / Grafana)
* Modèles de prédiction de combats

---

## 👤 Auteur

Benjamin — Projet pédagogique Pokémon Let’s Go
