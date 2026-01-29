# Accès au Monitoring - Guide Rapide

**Date** : 2026-01-29
**Status** : ✅ TOUT EST CONFIGURÉ

---

## ✅ État Actuel

### Métriques Disponibles

```
✅ model_predictions_total : 125 prédictions
✅ model_confidence_score : Histogram de confiance
✅ model_win_probability : Histogram de probabilités
✅ model_prediction_duration_seconds : Latences
```

### Services Actifs

```
✅ MLflow : http://localhost:5001 (6 runs dans demo_monitoring)
✅ Grafana : http://localhost:3001 (dashboards provisionnés)
✅ Prometheus : http://localhost:9091 (scraping API toutes les 10s)
✅ API : http://localhost:8080 (125 prédictions faites)
```

---

## 📊 GRAFANA - Comment Accéder aux Dashboards

### Étape 1 : Ouvrir Grafana

```bash
# Dans votre navigateur
http://localhost:3001
```

### Étape 2 : Login (si demandé)

**Le login devrait être automatique** (auth anonyme activée)

Si demandé :
```
Username: admin
Password: admin
```

### Étape 3 : Accéder aux Dashboards

1. **Cliquez sur le menu hamburger** (☰) en haut à gauche
2. **Sélectionnez "Dashboards"**
3. Vous devriez voir 2 dashboards :
   - 📊 **API Performance**
   - 🤖 **Model Performance**

### Étape 4 : Visualiser les Métriques

**Dashboard "Model Performance"** :
- Total predictions : 125
- Predictions rate : ~X req/s
- Confidence distribution
- Latency (p50, p95, p99)

**Dashboard "API Performance"** :
- HTTP requests
- Request duration
- Error rate
- CPU/Memory usage

---

## 🔧 Si les Dashboards Sont Vides

### Problème 1 : Datasource Non Configurée

**Vérification** :
1. Dans Grafana, aller dans : **Configuration → Data Sources**
2. Vérifier que **Prometheus** est présent
3. URL doit être : `http://prometheus:9090`
4. Cliquer sur **"Save & Test"** → Doit afficher "Data source is working"

**Si Prometheus absent** :
```bash
# Redémarrer Grafana pour forcer le provisioning
docker compose restart grafana
sleep 10
```

---

### Problème 2 : Dashboards Non Chargés

**Vérification** :
```bash
# Vérifier que les dashboards sont montés
docker compose exec grafana ls -la /var/lib/grafana/dashboards/
```

**Si vide** :
```bash
# Redémarrer Grafana
docker compose restart grafana
sleep 20

# Vérifier les logs
docker compose logs grafana | grep -i dashboard
```

---

### Problème 3 : Pas de Données sur les Graphiques

**Cause** : Time range trop restreint ou anciennes données

**Solution** :
1. En haut à droite de Grafana, cliquer sur le sélecteur de temps
2. Sélectionner **"Last 1 hour"** ou **"Last 6 hours"**
3. Cliquer sur le bouton **Refresh** (🔄)

---

## 🧪 MLflow - Comment Accéder aux Expériences

### Étape 1 : Ouvrir MLflow

```bash
http://localhost:5001
```

### Étape 2 : Naviguer dans l'UI

Vous devriez voir :
- ✅ **demo_monitoring** (expérience avec 6 runs)
- ✅ Éventuellement d'autres expériences si des modèles ont été entraînés

### Étape 3 : Explorer les Runs

1. Cliquer sur **demo_monitoring**
2. Voir les 6 runs avec leurs métriques :
   - accuracy : 0.9177 - 0.9734
   - precision : 0.88 - 0.98
   - recall : 0.87 - 0.98
   - f1_score : calculé
3. Voir les paramètres :
   - model_type : XGBoost
   - n_estimators : 100-300
   - max_depth : 5-10
   - learning_rate : 0.01-0.1

---

## 🔍 Prometheus - Queries de Test

Ouvrez **http://localhost:9091** et testez ces queries :

### 1. Total des Prédictions
```promql
model_predictions_total
```
**Résultat attendu** : 125

### 2. Rate de Prédictions (par seconde)
```promql
rate(model_predictions_total[1m])
```
**Résultat attendu** : ~0.1-0.5 req/s (selon activité récente)

### 3. Latence P95
```promql
histogram_quantile(0.95, rate(model_prediction_duration_seconds_bucket[5m]))
```
**Résultat attendu** : 0.2-0.5 secondes

### 4. Confiance Moyenne
```promql
rate(model_confidence_score_sum[5m]) / rate(model_confidence_score_count[5m])
```
**Résultat attendu** : 0.6-0.9

---

## 🚀 Générer Plus de Données

Si vous voulez plus de données pour les graphiques :

### Option 1 : Script populate_monitoring.py
```bash
# Génère 50 prédictions + popule MLflow
python3 scripts/populate_monitoring.py
```

### Option 2 : Test Monitoring Complet
```bash
# Génère 100 prédictions + validation complète
python3 tests/integration/test_monitoring_validation.py
```

### Option 3 : Utiliser Streamlit
```bash
# Ouvrir l'interface
http://localhost:8502

# Faire 10-20 prédictions manuellement via l'UI
# Les métriques s'accumulent automatiquement
```

---

## 📈 Résumé - Ce Qui Fonctionne

### MLflow ✅
- [x] Serveur accessible (http://localhost:5001)
- [x] Expérience demo_monitoring créée
- [x] 6 runs avec métriques (accuracy 91-97%)
- [x] Prêt pour entraînements de modèles

### Prometheus ✅
- [x] Serveur accessible (http://localhost:9091)
- [x] Scraping API toutes les 10s
- [x] 125 prédictions enregistrées
- [x] Métriques model_* disponibles

### Grafana ✅
- [x] Serveur accessible (http://localhost:3001)
- [x] Datasource Prometheus configurée
- [x] Dashboards provisionnés (API + Model Performance)
- [x] Prêt à afficher les métriques

---

## 🎯 Checklist de Vérification

1. [ ] Ouvrir MLflow → Voir expérience demo_monitoring
2. [ ] Ouvrir Grafana → Login automatique
3. [ ] Aller dans Dashboards → Voir 2 dashboards
4. [ ] Ouvrir "Model Performance" → Voir graphiques avec données
5. [ ] Time range = "Last 1 hour"
6. [ ] Vérifier que les métriques s'affichent (125 predictions)

---

## 💡 Astuce : Rafraîchir les Données

Si Grafana n'affiche pas les données :

1. **Vérifier le time range** : Last 1 hour minimum
2. **Cliquer sur Refresh** (🔄) en haut à droite
3. **Vérifier la datasource** : Configuration → Data Sources → Prometheus → Test
4. **Redémarrer Grafana** : `docker compose restart grafana`

---

**Auteur** : Claude Sonnet 4.5
**Date** : 2026-01-29
**Status** : ✅ MONITORING OPÉRATIONNEL
