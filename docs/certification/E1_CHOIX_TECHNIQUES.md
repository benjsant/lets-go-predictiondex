# E1 - Justification des Choix Techniques
## Document de Défense pour le Jury

**Projet**: Pokémon Let's Go - PredictionDex
**Bloc de Compétences**: E1 - Développer une Solution de Collecte et de Traitement de Données
**Date**: 2026-01-20

---

## Table des Matières

1. [Choix des Technologies](#choix-des-technologies)
2. [Choix Architecturaux](#choix-architecturaux)
3. [Choix de Modélisation](#choix-de-modélisation)
4. [Gestion des Limites](#gestion-des-limites)

---

## Choix des Technologies

### PostgreSQL (vs SQLite, MongoDB)

**Choix retenu**: PostgreSQL 15

**Alternatives considérées**:
- SQLite: Trop simple pour relations complexes
- MongoDB: Document-oriented inadapté au modèle relationnel

**Justification**:
- ✅ **ACID**: Garantie d'intégrité transactionnelle
- ✅ **Relations complexes**: Foreign keys, cascade delete
- ✅ **Performance**: Indexes B-tree, LATERAL joins
- ✅ **Standard industriel**: Compatible production future
- ✅ **Types avancés**: DECIMAL pour précision (multiplicateurs)
- ✅ **Scalabilité**: Jusqu'à plusieurs millions de lignes (ML dataset)

**Défendable en jury**:
> "PostgreSQL a été choisi pour sa robustesse relationnelle et sa conformité aux standards industriels, permettant de garantir l'intégrité des données et d'anticiper une évolution vers un environnement de production."

---

### SQLAlchemy ORM (vs SQL brut, Django ORM)

**Choix retenu**: SQLAlchemy 2.0

**Alternatives considérées**:
- SQL brut: Trop verbeux, erreurs à l'exécution
- Django ORM: Trop couplé au framework Django

**Justification**:
- ✅ **Type safety**: Détection d'erreurs au développement
- ✅ **Réutilisabilité**: Modèles utilisables par API et ML
- ✅ **Lazy loading**: Optimisation des requêtes (joinedload)
- ✅ **Migration facilitée**: Alembic compatible
- ✅ **Abstraction DB**: Portable vers MySQL/MariaDB si besoin

**Défendable en jury**:
> "SQLAlchemy offre une abstraction objet tout en gardant la puissance de SQL. Cela permet de manipuler les données de façon pythonique tout en optimisant les performances via les options de chargement."

---

### FastAPI (vs Flask, Django REST)

**Choix retenu**: FastAPI 0.100+

**Alternatives considérées**:
- Flask: Pas de validation automatique
- Django REST: Trop monolithique pour micro-service

**Justification**:
- ✅ **Performance**: Asynchrone (ASGI), 2-3x plus rapide que Flask
- ✅ **Validation automatique**: Pydantic intégré
- ✅ **Documentation auto**: Swagger UI / ReDoc généré
- ✅ **Type hints**: Cohérence avec SQLAlchemy
- ✅ **Standards modernes**: OpenAPI 3.0, JSON Schema

**Défendable en jury**:
> "FastAPI combine performance, validation automatique et documentation interactive. C'est devenu le standard de facto pour les APIs Python modernes, notamment dans les projets ML (voir mlflow, ray-serve)."

---

### Scrapy (vs BeautifulSoup + requests)

**Choix retenu**: Scrapy 2.11

**Alternatives considérées**:
- BeautifulSoup: Trop basique pour scraping structuré
- Selenium: Overkill pour site statique

**Justification**:
- ✅ **Pipeline structuré**: Items, middlewares, pipelines
- ✅ **Asynchrone natif**: Twisted, concurrence élevée
- ✅ **Retry automatique**: Robustesse face aux erreurs réseau
- ✅ **Rate limiting**: Respect du serveur cible
- ✅ **Logs structurés**: Traçabilité complète

**Défendable en jury**:
> "Scrapy est un framework dédié au scraping professionnel. Il offre une structure robuste avec gestion automatique des erreurs, retry, et rate limiting, essentiel pour un ETL pérenne."

---

### Parquet (vs CSV, JSON)

**Choix retenu**: Apache Parquet

**Alternatives considérées**:
- CSV: Pas de types, encodage problématique
- JSON: Verbeux, pas optimisé pour analytics

**Justification**:
- ✅ **Columnar**: Compression 3-5x vs CSV
- ✅ **Types préservés**: INT64, FLOAT64, STRING
- ✅ **Performance ML**: Lecture 10x plus rapide (pandas)
- ✅ **Standard Big Data**: Compatible Spark, Dask, Arrow
- ✅ **Schema inclus**: Autodocumenté

**Défendable en jury**:
> "Parquet est le format standard pour le Machine Learning et le Big Data. Il offre compression, typage fort et performances optimales pour pandas et scikit-learn, tout en étant compatible avec les écosystèmes modernes (Spark, Dask)."

---

## Choix Architecturaux

### Pipeline ETL Orchestré (vs Script monolithique)

**Choix retenu**: Pipeline modulaire avec check de complétion

**Architecture**:
```python
def main():
    if check_etl_already_done():
        return
    run_etl_csv()
    run_etl_pokeapi()
    run_scrapy()
    run_post_process()
```

**Justification**:
- ✅ **Idempotence**: Réexécutable sans duplication
- ✅ **Modularité**: Chaque phase testable indépendamment
- ✅ **Traçabilité**: Logs par phase
- ✅ **Reprise sur erreur**: Possibilité de skip phases
- ✅ **Vérification DB**: Plus robuste qu'un fichier `.etl_done`

**Défendable en jury**:
> "Le pipeline ETL suit le principe d'idempotence: il peut être relancé sans effet de bord. La vérification se fait via la base de données elle-même (`SELECT COUNT(*) FROM pokemon`), éliminant les risques liés aux fichiers de flag."

---

### Séparation CSV / init_db

**Choix retenu**:
- CSV: Données métier variables (Pokémon, capacités)
- init_db: Vocabulaire contrôlé fixe (form, learn_method, move_category)

**Justification**:
- ✅ **Maintenabilité**: Vocabulaire en code = DRY
- ✅ **Cohérence**: Garantie par enum/constantes
- ✅ **Moins de fichiers**: Évite CSV triviaux (3-5 lignes)
- ✅ **Type safety**: Validation au démarrage

**Alternative rejetée**:
- Tout en CSV: Multiplication de fichiers, risque d'incohérence
- Tout en init_db: Perd la traçabilité des données sources

**Défendable en jury**:
> "Cette séparation respecte le principe de responsabilité unique: les données métier (188 Pokémon) viennent de sources externes (CSV), tandis que le vocabulaire contrôlé (3 catégories de capacités) est géré en code pour garantir cohérence et typage."

---

### Docker Compose (vs Kubernetes, Nomad)

**Choix retenu**: Docker Compose v2

**Alternatives considérées**:
- Kubernetes: Overkill pour développement local
- Bare metal: Pas reproductible

**Justification**:
- ✅ **Reproductibilité**: `docker compose up` = environnement complet
- ✅ **Isolation**: Chaque service dans son container
- ✅ **Dépendances**: `depends_on` avec healthchecks
- ✅ **Hot reload**: Volumes montés pour développement
- ✅ **Standard**: Compatible CI/CD (GitHub Actions)

**Défendable en jury**:
> "Docker Compose garantit la reproductibilité totale de l'environnement. Un simple `docker compose up` crée l'infrastructure complète (DB, API, interface), permettant à n'importe quel développeur de démarrer le projet en quelques minutes."

---

## Choix de Modélisation

### Normalisation 3NF (vs Dénormalisation)

**Choix retenu**: Forme normale 3NF

**Justification**:
- ✅ **Évite la redondance**: `pokemon.species_id` → `pokemon_species.name_fr`
- ✅ **Intégrité**: Foreign keys garantissent cohérence
- ✅ **Maintenabilité**: Modifier un nom = 1 UPDATE
- ✅ **Performance**: Index B-tree sur FK

**Alternative rejetée**:
- Dénormalisation: Duplication de `name_fr` dans table `pokemon`
- Raison: Pas de gain de perf pour ce volume (188 lignes)

**Défendable en jury**:
> "Le modèle suit la 3ème forme normale pour garantir l'intégrité des données. Avec un volume de 188 Pokémon, le coût des jointures est négligeable (quelques millisecondes), tandis que la cohérence est garantie par design."

---

### Table pokemon_move (vs Array JSON)

**Choix retenu**: Table de jonction relationnelle

**Alternative rejetée**:
```python
# MAUVAIS
class Pokemon:
    moves = Column(JSONB)  # {"moves": [{"id": 1, "level": 5}]}
```

**Justification**:
- ✅ **Requêtes SQL**: Recherche de Pokémon par capacité
- ✅ **Intégrité**: CASCADE DELETE automatique
- ✅ **Normalisation**: Évite duplication de move.name
- ✅ **Indexation**: Index sur (pokemon_id, move_id)

**Défendable en jury**:
> "La table de jonction `pokemon_move` suit le modèle relationnel canonique. Stocker les capacités en JSON aurait empêché les jointures SQL et violé la normalisation. PostgreSQL gère très efficacement ce type de relation many-to-many."

---

### DECIMAL pour multiplicateurs (vs FLOAT)

**Choix retenu**: `DECIMAL(3, 2)`

**Alternative rejetée**: `FLOAT`

**Justification**:
- ✅ **Précision exacte**: 2.0 × 2.0 = 4.0 (pas 3.9999...)
- ✅ **Calculs métier**: ML nécessite précision
- ✅ **Stockage**: 6 bytes (acceptable pour 324 lignes)
- ✅ **Standard financier**: Même logique que prix

**Défendable en jury**:
> "Les multiplicateurs de type (0.25, 0.5, 1.0, 2.0, 4.0) sont des valeurs métier exactes. DECIMAL évite les erreurs d'arrondi qui pourraient s'accumuler dans les calculs de dégâts ou les features ML (type_multiplier)."

---

## Gestion des Limites

### Limite 1: Capacités Niveau "Départ"

**Problème identifié**:
- Poképédia regroupe parfois: "Charge + Cage-Éclair" dans une cellule
- Parsing actuel: Récupère uniquement la première capacité

**Impact**:
- Perte de ~5-10 capacités pour certains Pokémon
- Non bloquant pour MVP (majorité des capacités sont OK)

**Statut**:
> ✅ **Documenté et assumé**

**Défense en jury**:
> "Cette limite est identifiée et documentée. Elle représente moins de 2% des données. Pour un MVP éducatif, l'impact est négligeable. Une amélioration future consisterait à parser finement les cellules multi-valeurs ou à utiliser une source alternative."

---

### Limite 2: Méga-Évolutions Partielles

**Problème identifié**:
- Seules les méga-évolutions de Let's Go sont incluses (Dracaufeu X/Y, Mewtwo X/Y)
- Pas de Méga-Lucario, Méga-Rayquaza (pas dans ce jeu)

**Impact**:
- Dataset incomplet pour générations ultérieures
- Conforme au périmètre fonctionnel

**Statut**:
> ✅ **Conforme au scope**

**Défense en jury**:
> "Le périmètre est volontairement limité à Pokémon Let's Go Pikachu/Eevee (151 Pokémon + mégas disponibles). Cette limite est cohérente avec l'objectif métier (application pour ce jeu spécifique). Une extension future pourrait intégrer Sword/Shield ou Scarlet/Violet."

---

### Limite 3: Dépendance Réseau PokéAPI

**Problème identifié**:
- ETL nécessite connexion internet active
- Rate limiting: 1 req/s (prend ~3 min pour 188 Pokémon)

**Mitigation**:
- Cache local possible (non implémenté en MVP)
- Fallback CSV possible pour données critiques

**Impact**:
- Acceptable en développement Docker
- À adresser en production (mirror interne)

**Défense en jury**:
> "La dépendance à PokéAPI est acceptable en environnement de développement. Le rate limiting (1 req/s) est respecté pour éviter de surcharger le serveur. En production, une approche de cache local ou de mirror interne serait implémentée."

---

## Améliorations Futures (Post-MVP)

### Technique

1. **Migration Alembic**
   - Actuellement: `Base.metadata.create_all()`
   - Futur: Versioning schéma avec historique de migrations
   - Bénéfice: Rollback, audit, collaboration

2. **Cache Redis**
   - Actuellement: Requêtes SQL à chaque appel API
   - Futur: Cache L1 (Redis) pour `/pokemon/` (données statiques)
   - Bénéfice: Latence divisée par 10, charge DB réduite

3. **GraphQL**
   - Actuellement: REST avec sur-fetching possible
   - Futur: API GraphQL pour requêtes complexes client-defined
   - Bénéfice: Flexibilité frontend, 1 requête vs N

### Fonctionnel

4. **Webhooks**
   - Déclenchement automatique sur ajout Pokémon
   - Notification Slack/Discord des changements
   - Régénération dataset ML automatique

5. **Internationalisation Complète**
   - Actuellement: FR/EN/JP pour noms
   - Futur: IT, ES, DE pour descriptions
   - API: Accept-Language header

---

## Tableau Récapitulatif

| Choix | Alternative | Raison | Défendable |
|-------|-------------|--------|------------|
| PostgreSQL | SQLite | Relations complexes, ACID | ✅ Production-ready |
| SQLAlchemy | SQL brut | Type safety, réutilisabilité | ✅ Standard Python |
| FastAPI | Flask | Performance, validation auto | ✅ Standard ML/API |
| Scrapy | BeautifulSoup | Robustesse, async | ✅ Scraping pro |
| Parquet | CSV | Compression, types, perf ML | ✅ Standard Big Data |
| Docker Compose | K8s | Simplicité, reproductibilité | ✅ Dev local optimal |
| Normalisation 3NF | Dénormalisation | Intégrité, cohérence | ✅ Best practice SGBD |
| Table pokemon_move | JSON Array | Requêtabilité, intégrité | ✅ Relationnel canonique |
| DECIMAL | FLOAT | Précision exacte | ✅ Calculs métier |
| init_db | CSV | Vocabulaire contrôlé | ✅ DRY, type safety |

---

## Conclusion

### Points Forts à Mettre en Avant

1. ✅ **Architecture moderne**: FastAPI + SQLAlchemy + Docker = Stack 2026
2. ✅ **Reproductibilité totale**: `docker compose up` = projet fonctionnel
3. ✅ **Standards industriels**: PostgreSQL, Parquet, OpenAPI, REST
4. ✅ **Qualité de code**: Type hints, validation Pydantic, ORM
5. ✅ **Limites assumées**: Documentation claire des trade-offs

### Phrase Clé pour le Jury

> "Ce projet démontre une maîtrise des technologies de données modernes (PostgreSQL, FastAPI, Parquet) et des bonnes pratiques d'ingénierie logicielle (Docker, ORM, validation). Les choix techniques sont cohérents avec un environnement de production tout en restant pragmatiques pour un MVP éducatif."

---

**Document préparé le**: 2026-01-20
**Prêt pour soutenance**: ✅ Oui
