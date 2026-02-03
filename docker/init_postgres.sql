-- Script d'initialisation PostgreSQL
-- Crée une base de données séparée pour MLflow

-- Base de données principale (créée automatiquement via POSTGRES_DB)
-- letsgo_db

-- Base de données pour MLflow tracking
CREATE DATABASE mlflow_db;
GRANT ALL PRIVILEGES ON DATABASE mlflow_db TO letsgo_user;
