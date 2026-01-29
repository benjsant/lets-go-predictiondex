# pgAdmin 4 - Interface de gestion PostgreSQL

## Accès à l'interface

Une fois les conteneurs Docker lancés, pgAdmin est accessible via :

**URL**: http://localhost:5050

### Identifiants de connexion

- **Email**: `admin@predictiondex.com`
- **Mot de passe**: `admin`

## Connexion au serveur PostgreSQL

Le serveur PostgreSQL **PredictionDex** est pré-configuré automatiquement.

### Pour vous connecter :

1. Ouvrez http://localhost:5050 dans votre navigateur
2. Connectez-vous avec les identifiants ci-dessus
3. Dans le panneau de gauche, cliquez sur **Servers** → **PredictionDex PostgreSQL**
4. Entrez le mot de passe de la base de données : `letsgo_password`
5. Cochez "Save password" pour ne pas avoir à le retaper

## Explorer la base de données

Une fois connecté, vous pouvez :

### 📊 Visualiser les données

- **Databases** → **letsgo_db** → **Schemas** → **public** → **Tables**
- Clic droit sur une table → **View/Edit Data** → **All Rows**

### 🔍 Exécuter des requêtes SQL

- Clic droit sur **letsgo_db** → **Query Tool**
- Écrivez vos requêtes SQL et exécutez-les avec F5 ou le bouton ▶️

Exemples de requêtes :

```sql
-- Voir tous les Pokémon
SELECT * FROM pokemon LIMIT 10;

-- Compter les capacités par type
SELECT type, COUNT(*) as nombre_capacites
FROM capacite
GROUP BY type
ORDER BY nombre_capacites DESC;

-- Voir les affinités de type
SELECT * FROM type_affinity WHERE multiplicateur > 2.0;

-- Statistiques des combats simulés
SELECT COUNT(*) as total_combats FROM battle_simulation;
```

### 📈 Analyser les schémas

- **Schemas** → **public** → **Tables**
- Clic droit sur une table → **Properties** pour voir la structure
- Onglet **Columns** : voir les colonnes et types
- Onglet **Constraints** : voir les clés primaires et étrangères

## Tables disponibles

| Table | Description |
|-------|-------------|
| `pokemon` | 187 Pokémon de Let's Go Pikachu/Eevee |
| `capacite` | 225 capacités/attaques disponibles |
| `type_affinity` | 323 affinités de types (multiplicateurs de dégâts) |
| `battle_simulation` | 898,612 combats simulés pour ML |
| `pokemon_capacity` | Association Pokémon ↔ Capacités |
| `alembic_version` | Gestion des migrations de schéma |

## Fonctionnalités avancées

### Sauvegarde de la base de données

1. Clic droit sur **letsgo_db** → **Backup...**
2. Choisir le format (Plain, Custom, Tar)
3. Cliquer sur **Backup**

### Import de données

1. Clic droit sur une table → **Import/Export...**
2. Sélectionner un fichier CSV
3. Configurer les colonnes et le format
4. Cliquer sur **OK**

### Surveillance des performances

- **Dashboard** : Vue d'ensemble de l'activité de la base
- **Server Activity** : Sessions actives et requêtes en cours
- **Statistics** : Statistiques détaillées par table

## Dépannage

### pgAdmin ne démarre pas

```bash
docker logs letsgo_pgadmin
docker restart letsgo_pgadmin
```

### Impossible de se connecter au serveur PostgreSQL

Vérifier que le conteneur `db` est bien démarré :

```bash
docker ps | grep letsgo_postgres
docker logs letsgo_postgres
```

### Réinitialiser pgAdmin

```bash
docker-compose down
docker volume rm lets-go-predictiondex_pgadmin_data
docker-compose up -d pgadmin
```

## Configuration

### Fichiers de configuration

- `servers.json` : Configuration pré-enregistrée du serveur PostgreSQL
- Volume Docker `pgadmin_data` : Persistance des préférences et connexions

### Modifier la configuration

Éditez [docker-compose.yml](../../docker-compose.yml) section `pgadmin` :

```yaml
environment:
  PGADMIN_DEFAULT_EMAIL: votre-email@example.com
  PGADMIN_DEFAULT_PASSWORD: votre-mot-de-passe
```

Puis redémarrez :

```bash
docker-compose down pgadmin
docker-compose up -d pgadmin
```

## Ressources

- [Documentation officielle pgAdmin 4](https://www.pgadmin.org/docs/pgadmin4/latest/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/15/)
