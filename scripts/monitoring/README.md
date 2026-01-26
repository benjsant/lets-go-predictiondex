# 📊 Scripts de Monitoring

Scripts pour valider et tester la stack de monitoring (Prometheus + Grafana + API metrics).

---

## 📝 Scripts disponibles

### `validate_monitoring.py`

**Description** : Validation complète de la stack de monitoring  
**Usage** : Script de validation end-to-end pour la certification E3/C11

**Ce qu'il fait** :
1. ✅ Génère 100 prédictions de test
2. ✅ Collecte métriques Prometheus
3. ✅ Vérifie l'état des services (API, Prometheus, Grafana)
4. ✅ Force la détection de drift
5. ✅ Analyse les résultats
6. ✅ Génère rapports JSON + HTML

**Prérequis** :
- Stack Docker lancée : `docker compose up`
- API disponible sur http://localhost:8080
- Prometheus sur http://localhost:9091
- Grafana sur http://localhost:3001

**Commande** :
```bash
# Depuis la racine du projet
python scripts/monitoring/validate_monitoring.py

# Ou avec chemin relatif
cd scripts/monitoring
python validate_monitoring.py
```

**Output** :
- 📄 `reports/monitoring/validation_report.json` - Rapport détaillé (métriques, scores)
- 🌐 `reports/monitoring/validation_report.html` - Rapport visuel (graphiques, alertes)

**Visualisation** :
```bash
# Ouvrir le rapport HTML
firefox reports/monitoring/validation_report.html

# Ou
xdg-open reports/monitoring/validation_report.html
```

---

## 📊 Exemple de rapport

### Métriques validées
- ✅ Taux de succès des prédictions (100%)
- ✅ Latence API (P95, P99)
- ✅ Taux de collecte Prometheus
- ✅ Détection de drift (Evidently)
- ✅ CPU/RAM système (Node Exporter)

### Score de validation
- **90-100%** : ✅ Excellent
- **70-89%** : 🟡 Bon (améliorations possibles)
- **50-69%** : 🟠 Moyen (vérifications nécessaires)
- **<50%** : ❌ Problèmes critiques

---

## 🔧 Développement

### Ajouter un nouveau test
```python
# Dans validate_monitoring.py
class MonitoringValidator:
    def test_custom_metric(self):
        """Ajouter un test personnalisé"""
        # Votre code ici
        pass
```

### Personnaliser les seuils
```python
# Configuration des seuils d'alerte
THRESHOLDS = {
    "success_rate_min": 95.0,
    "latency_p95_max_ms": 500,
    "prometheus_scrape_errors_max": 5
}
```

---

## 📚 Références

- **Documentation monitoring** : [docs/monitoring/MONITORING_README.md](../../docs/monitoring/MONITORING_README.md)
- **Docker orchestration** : [DOCKER_ORCHESTRATION.md](../../DOCKER_ORCHESTRATION.md)
- **Certification E3** : [docs/certification/E3_COMPETENCES_STATUS.md](../../docs/certification/E3_COMPETENCES_STATUS.md)

---

**Créé le** : 26 janvier 2026  
**Maintenu par** : PredictionDex Team
