# **Rapport professionnel – Bloc E3**

**Mise en situation professionnelle : Mise en service d’un modèle d’intelligence artificielle**

---

## **Sommaire**

### **1\. Introduction et contexte du projet**

1.1 Présentation générale du projet PredictionDex  
 1.2 Objectifs de la mise en situation E3  
 1.3 Positionnement du bloc E3 dans le projet global  
 1.4 Périmètre fonctionnel et technique de l’évaluation

---

### **2\. Présentation du modèle d’intelligence artificielle**

2.1 Problématique adressée par le modèle  
 2.2 Nature du modèle (classification supervisée)  
 2.3 Données d’entrée et données de sortie du modèle  
 2.4 Processus de génération du jeu de données  
 2.5 Hypothèses de conception  
 2.6 Limites connues et axes d’amélioration

*Compétences visées : C9, C11*

---

### **3\. Encapsulation du modèle dans une API REST**

3.1 Objectifs de l’exposition du modèle  
 3.2 Architecture globale de l’API  
 3.3 Choix technologiques (FastAPI, Python, dépendances)  
 3.4 Description des endpoints exposés  
 3.5 Gestion de l’authentification et de la sécurité  
 3.6 Conformité aux bonnes pratiques OWASP  
 3.7 Documentation de l’API (Swagger / OpenAPI)

*Compétence visée : C9*

---

### **4\. Tests automatisés du modèle et de l’API**

4.1 Stratégie globale de tests  
 4.2 Tests unitaires du modèle  
 4.3 Tests des endpoints de l’API  
 4.4 Jeux de données de test  
 4.5 Résultats des tests et interprétation  
 4.6 Couverture de tests et limites

*Compétence visée : C12*

---

### **5\. Intégration de l’API d’intelligence artificielle dans l’application**

5.1 Présentation de l’application existante  
 5.2 Architecture applicative et flux de données  
 5.3 Appels à l’API depuis l’application  
 5.4 Gestion des erreurs et des réponses  
 5.5 Adaptations fonctionnelles et visuelles  
 5.6 Tests d’intégration applicative

*Compétence visée : C10*

---

### **6\. Monitorage du modèle d’intelligence artificielle**

6.1 Objectifs du monitorage  
 6.2 Métriques surveillées  
 6.3 Outils de monitorage retenus  
 6.4 Mise en place de la chaîne de monitorage  
 6.5 Visualisation et restitution des métriques  
 6.6 Tests du dispositif de monitorage

*Compétence visée : C11*

---

### **7\. Chaîne de livraison continue du modèle (MLOps)**

7.1 Enjeux MLOps du projet  
 7.2 Description de la chaîne CI/CD  
 7.3 Déclencheurs et automatisations  
 7.4 Étapes de tests intégrées à la chaîne  
 7.5 Packaging et déploiement du modèle  
 7.6 Versioning et traçabilité

*Compétence visée : C13*

---

### **8\. Démonstration du service d’intelligence artificielle**

8.1 Scénario de démonstration  
 8.2 Présentation de l’API du modèle  
 8.3 Démonstration de l’application enrichie  
 8.4 Démonstration de la chaîne de livraison continue

---

### **9\. Conclusion**

9.1 Bilan de la mise en situation E3  
 9.2 Compétences mobilisées et validées  
 9.3 Limites du projet  
 9.4 Perspectives d’évolution

---

## **Annexes**

* Annexe A : Architecture technique détaillée

* Annexe B : Documentation Swagger (OpenAPI)

* Annexe C : Arborescence du projet

* Annexe D : Extraits de code significatifs

* Annexe E : Captures des dashboards de monitorage

* Annexe F : Logs et traces d’exécution CI/CD

---

## **1\. Introduction et contexte du projet**

### **1.1 Présentation générale du projet PredictionDex**

Le projet **PredictionDex** s’inscrit dans le cadre de la réalisation d’un service numérique intégrant des mécanismes d’intelligence artificielle appliqués à l’univers du jeu *Pokémon Let’s Go*.  
 Il a pour objectif principal de proposer un système capable d’exploiter des données issues de différentes sources afin de fournir des fonctionnalités d’analyse et de prédiction autour des combats Pokémon.

Le projet repose sur une architecture modulaire intégrant :

* des scripts de collecte et de préparation de données,

* une base de données relationnelle structurée,

* une API REST exposant les données et les services d’intelligence artificielle,

* une application cliente permettant l’exploitation fonctionnelle de ces services.

PredictionDex a été conçu comme un projet pédagogique mais réaliste, reproduisant les contraintes et les bonnes pratiques rencontrées dans un contexte professionnel, notamment en matière de structuration des données, de mise à disposition de services, de tests, de sécurité et de déploiement.

---

### **1.2 Objectifs de la mise en situation professionnelle E3**

La mise en situation professionnelle **E3** vise à évaluer la capacité à **mettre en service un modèle d’intelligence artificielle** déjà existant, en assurant son encapsulation, son intégration applicative, son monitorage et son déploiement continu dans une approche MLOps.

Dans ce cadre, les objectifs principaux de la mise en situation E3 sont les suivants :

* encapsuler un modèle d’intelligence artificielle au sein d’une API REST sécurisée,

* permettre l’interaction entre le modèle et une application existante,

* mettre en place des tests automatisés garantissant la qualité et la fiabilité du service,

* déployer un dispositif de monitorage du modèle et de ses performances,

* concevoir une chaîne de livraison continue permettant l’automatisation des phases de test, de validation et de déploiement du modèle.

Cette mise en situation ne porte pas sur la conception théorique du modèle, mais bien sur **sa mise en production et son exploitation opérationnelle**, conformément aux exigences du référentiel de compétences.

---

### **1.3 Positionnement du bloc E3 dans le projet global**

Le bloc de compétences **E3** s’inscrit dans la continuité directe du bloc **E1**, consacré à la collecte, au stockage et à la mise à disposition des données du projet.

Les données préparées, stockées et exposées lors du bloc E1 constituent la base d’entrée du modèle d’intelligence artificielle mobilisé dans le cadre de E3.  
 Ainsi, le projet PredictionDex adopte une logique cohérente de bout en bout :

* **E1** : constitution et exposition des données,

* **E3** : exploitation de ces données par un modèle d’intelligence artificielle mis en service.

Le bloc E3 se concentre exclusivement sur la **mise en œuvre technique et opérationnelle** du modèle, sans recouvrir les aspects de conception applicative globale évalués dans le bloc E4.

---

### **1.4 Périmètre fonctionnel et technique de l’évaluation**

Le périmètre de la mise en situation E3 couvre les éléments suivants :

Sur le plan fonctionnel :

* la prédiction de l’issue d’un combat Pokémon à partir de caractéristiques statistiques et contextuelles,

* l’accès à cette fonctionnalité via une API REST,

* l’intégration de cette prédiction dans une application cliente existante.

Sur le plan technique :

* l’encapsulation du modèle dans une API développée en Python à l’aide du framework FastAPI,

* la sécurisation des accès à l’API,

* la mise en place de tests automatisés couvrant le modèle et ses points de terminaison,

* le déploiement d’un dispositif de monitorage des performances et du comportement du modèle,

* la conception d’une chaîne de livraison continue intégrant les étapes de test, de validation et de déploiement.

Le projet est réalisé dans un contexte fictif mais réaliste, en respectant les bonnes pratiques de développement, de documentation, de versionnement et d’accessibilité attendues dans un environnement professionnel.

---

**2\. Présentation du modèle d’intelligence artificielle**

### **2.1 Finalité du modèle dans le projet PredictionDex**

Le modèle d’intelligence artificielle développé dans le cadre du projet PredictionDex a pour finalité de **prédire l’issue d’un combat Pokémon** entre deux entités issues de la première génération des jeux *Pokémon Let’s Go*.

Le modèle ne vise pas à reproduire fidèlement le moteur interne du jeu, mais à proposer une **approximation statistique réaliste** basée sur :

* les statistiques des Pokémon,

* leurs types,

* les interactions de type (avantages et faiblesses),

* les capacités utilisées lors du combat.

Cette approche permet de répondre à un besoin fonctionnel clair : fournir une prédiction exploitable via une API, intégrable dans une application cliente, tout en conservant un modèle suffisamment générique pour être surveillé, versionné et déployé dans un cadre MLOps.

---

### **2.2 Nature du problème traité**

Le problème adressé par le modèle est un **problème de classification supervisée binaire**.

* **Entrées** : caractéristiques de deux Pokémon engagés dans un combat

* **Sortie** : identification du vainqueur du combat

  * Classe `1` : victoire du Pokémon 1

  * Classe `2` : victoire du Pokémon 2

Chaque observation correspond à un combat simulé ou historique, pour lequel l’issue est connue au moment de l’entraînement.

Le choix d’une classification binaire permet :

* une interprétation simple des résultats,

* une intégration directe dans une API REST,

* un calcul clair de métriques de performance adaptées au contexte métier.

---

### **2.3 Données exploitées par le modèle**

Le modèle s’appuie exclusivement sur des **données structurées**, issues du travail réalisé lors du bloc E1.

Les principales catégories de données utilisées sont :

* statistiques de base des Pokémon (points de vie, attaque, défense, vitesse, etc.),

* types primaires et secondaires,

* indicateurs d’avantage ou de désavantage de type,

* caractéristiques des attaques sélectionnées lors du combat,

* différences et ratios entre les statistiques des deux combattants.

Les données sont préalablement :

* nettoyées,

* validées,

* normalisées,

* stockées en base PostgreSQL,  
   puis transformées en features exploitables avant l’inférence.

Aucune donnée personnelle n’est utilisée, ce qui exclut toute contrainte RGPD spécifique.

---

### **2.4 Choix de l’algorithme**

Le modèle retenu pour PredictionDex repose sur l’algorithme **XGBoost (Extreme Gradient Boosting)**, utilisé sous la forme d’un classificateur.

Ce choix est motivé par plusieurs éléments :

* excellente performance sur des données tabulaires,

* capacité à gérer des relations non linéaires complexes,

* robustesse face aux features corrélées,

* rapidité d’inférence compatible avec une exposition via API,

* bonne intégration avec l’écosystème Python et les outils MLOps.

XGBoost constitue ainsi un compromis efficace entre performance, stabilité et facilité de mise en production.

---

### **2.5 Versions du modèle et justification du choix en production**

Deux versions principales du modèle ont été développées et évaluées :

| Version | Description | Accuracy | Statut |
| ----- | ----- | ----- | ----- |
| v1 | Modèle basé sur une attaque optimale unique | ≈ 94 % | Non retenue |
| **v2** | Modèle prenant en compte les attaques des deux Pokémon | **≈ 88 %** | **Version en production** |

Bien que la version v1 affiche une précision plus élevée, elle repose sur un scénario simplifié peu représentatif d’un combat réel.  
 La version v2, retenue pour la mise en production, offre un comportement plus réaliste en intégrant les choix d’attaques des deux combattants, au prix d’une légère baisse de performance mesurée.

Ce choix privilégie la **cohérence fonctionnelle et métier** plutôt que la maximisation artificielle des métriques.

---

### **2.6 Indicateurs de performance du modèle**

Le modèle est évalué à l’aide de métriques classiques de classification supervisée :

| Métrique | Valeur |
| ----- | ----- |
| Accuracy | ≈ 88 % |
| Precision | ≈ 87 % |
| Recall | ≈ 89 % |
| F1-score | ≈ 88 % |

Ces résultats confirment que le modèle est :

* suffisamment précis pour un usage applicatif,

* stable sur les données de validation,

* adapté à une exposition en production.

Les métriques sont suivies et historisées via un outil de tracking afin de faciliter la comparaison entre versions.

---

### **2.7 Contraintes et limites identifiées**

Certaines limites ont été identifiées dans le cadre du projet :

* dépendance à des données simulées ou simplifiées,

* absence de prise en compte de mécaniques avancées (objets, talents, météo),

* périmètre volontairement limité à la génération 1\.

Ces limites sont assumées dans le cadre de la mise en situation pédagogique et n’empêchent pas la validation des compétences du bloc E3, dont l’objectif principal reste la **mise à disposition et l’exploitation opérationnelle du modèle**.

---

**3\. Mise à disposition du modèle via une API REST**

## **3.1 Objectifs de l’API**

L’objectif de l’API développée dans le cadre du projet PredictionDex est de **mettre à disposition le modèle d’intelligence artificielle de manière sécurisée, standardisée et exploitable par des applications clientes**.

L’API joue un rôle central dans l’architecture :

* elle constitue le point d’entrée unique vers le modèle,

* elle garantit la séparation entre logique métier, modèle ML et interface utilisateur,

* elle permet l’intégration du modèle dans différents contextes (frontend, tests, monitoring).

Cette approche répond pleinement aux exigences du bloc E3, qui impose une **exposition opérationnelle du modèle**.

---

## **3.2 Choix technologiques**

L’API est développée à l’aide du framework **FastAPI**, choisi pour les raisons suivantes :

* performances élevées grâce à ASGI,

* validation automatique des entrées via Pydantic,

* génération automatique de documentation OpenAPI (Swagger),

* facilité d’intégration avec des modèles ML Python,

* compatibilité native avec des architectures conteneurisées.

L’API fonctionne au sein d’un conteneur Docker et communique avec :

* une base de données PostgreSQL,

* le registre de modèles MLflow,

* les services de monitoring.

---

## **3.3 Chargement et gestion du modèle**

Le modèle est chargé dynamiquement depuis le **MLflow Model Registry**, ce qui permet :

* un versioning clair,

* une gestion du cycle de vie du modèle,

* une promotion contrôlée des versions en production.

Afin d’optimiser les performances, le modèle est chargé une seule fois en mémoire grâce à un mécanisme de cache.

`MODEL_NAME = "battle_winner_model"`  
`MODEL_VERSION = "Production"`

`@lru_cache(maxsize=1)`  
`def load_model(self):`  
    `"""Charge le modèle depuis MLflow Registry (avec cache)."""`  
    `mlflow.set_tracking_uri("http://mlflow:5000")`  
      
    `model_uri = f"models:/{self.MODEL_NAME}/{self.MODEL_VERSION}"`  
    `model = mlflow.pyfunc.load_model(model_uri)`  
      
    `return model`

Ce mécanisme permet :

* une réduction significative de la latence,

* une meilleure scalabilité,

* une stabilité accrue en production.

---

## **3.4 Endpoint de prédiction**

L’API expose un endpoint principal dédié à la prédiction de combats Pokémon.

### **Endpoint**

* **Méthode** : `POST`

* **URL** : `/api/v1/predict/battle`

* **Authentification** : clé API

* **Format** : JSON

### **Exemple de requête**

`{`  
  `"pokemon_1_id": 25,`  
  `"pokemon_2_id": 6`  
`}`

### **Exemple de réponse**

`{`  
  `"winner": 1,`  
  `"winner_name": "Pikachu",`  
  `"confidence": 0.87,`  
  `"pokemon_1_win_probability": 0.87,`  
  `"pokemon_2_win_probability": 0.13`  
`}`

L’API retourne à la fois :

* la classe prédite,

* le nom du vainqueur,

* un score de confiance,

* la distribution des probabilités.

Cette richesse de réponse facilite l’intégration côté frontend et améliore l’expérience utilisateur.

---

## **3.5 Validation des entrées et robustesse**

Les données entrantes sont systématiquement validées à l’aide de **schémas Pydantic** :

* vérification des types,

* contrôle des valeurs attendues,

* gestion des erreurs explicites.

Cette validation permet :

* de prévenir les erreurs d’injection,

* de sécuriser l’appel au modèle,

* d’améliorer la robustesse globale de l’API.

En cas d’erreur, l’API retourne des réponses HTTP explicites (400, 401, 422, 500), facilitant le débogage et l’exploitation.

---

## **3.6 Sécurisation de l’API**

L’API intègre plusieurs mécanismes de sécurité conformes aux recommandations OWASP :

| Risque | Mesure appliquée |
| ----- | ----- |
| Injection | Validation stricte des entrées |
| Accès non autorisé | Authentification par clé API |
| Exposition de données sensibles | Absence de données personnelles |
| Mauvaise configuration | Headers HTTP sécurisés |
| Logging insuffisant | Logs structurés |

Ces mesures garantissent que l’exposition du modèle respecte un **niveau de sécurité adapté à un environnement de production**.

---

## **3.7 Documentation et testabilité**

FastAPI génère automatiquement une documentation interactive accessible via :

* `/docs` (Swagger UI)

* `/redoc`

Cette documentation permet :

* de tester les endpoints en temps réel,

* de visualiser les schémas de requêtes et réponses,

* de faciliter l’intégration par des développeurs tiers.

Des tests automatisés couvrent :

* les endpoints de prédiction,

* les scénarios d’erreurs,

* la cohérence des réponses.

---

## **3.8 Rôle de l’API dans l’architecture globale**

L’API constitue le **cœur de la chaîne de valeur du projet PredictionDex** :

* elle reçoit les données depuis l’interface Streamlit,

* elle orchestre l’appel au modèle,

* elle expose les métriques de monitoring,

* elle assure la traçabilité des prédictions.

Ce positionnement central justifie pleinement son rôle dans la validation des compétences du bloc E3.

---

# **4\. Intégration du modèle dans l’application cliente**

## **4.1 Objectifs de l’intégration**

L’objectif de cette étape est d’**intégrer le modèle d’intelligence artificielle exposé via l’API REST dans une application cliente utilisable par un utilisateur final**.

Dans le projet PredictionDex, cette intégration est réalisée à travers une **application web développée avec Streamlit**, permettant :

* d’interagir avec le modèle sans connaissance technique,

* de visualiser les résultats de prédiction de manière compréhensible,

* de valider le bon fonctionnement de la chaîne complète : interface → API → modèle.

Cette étape répond directement à la compétence **C10**, qui exige l’intégration opérationnelle d’un service d’intelligence artificielle dans une application.

---

## **4.2 Choix de Streamlit comme interface utilisateur**

Streamlit a été retenu comme framework frontend pour plusieurs raisons :

* rapidité de développement,

* intégration native avec Python,

* capacité à consommer facilement des APIs REST,

* facilité de déploiement dans un environnement Docker,

* accessibilité immédiate via un navigateur web.

Le choix de Streamlit est cohérent avec un projet à vocation démonstrative et pédagogique, tout en restant suffisamment robuste pour une utilisation réelle.

---

## **4.3 Parcours utilisateur**

Le parcours utilisateur a été conçu pour être **simple, intuitif et progressif**.

1. L’utilisateur accède à l’application Streamlit.

2. Il sélectionne deux Pokémon à partir de listes déroulantes.

3. Les informations principales (sprite, statistiques, types) sont affichées.

4. L’utilisateur déclenche la prédiction via un bouton dédié.

5. Le résultat du combat est affiché avec un score de confiance.

Ce parcours permet de comprendre rapidement la valeur ajoutée du modèle.

---

## **4.4 Appel à l’API de prédiction**

L’application Streamlit ne contient aucune logique de prédiction.  
 Elle se contente d’appeler l’API exposée par le backend.

`def call_prediction_api(pokemon_1_id: int, pokemon_2_id: int) -> dict:`  
    `response = requests.post(`  
        `f"{API_BASE_URL}/predict/battle",`  
        `json={`  
            `"pokemon_1_id": pokemon_1_id,`  
            `"pokemon_2_id": pokemon_2_id`  
        `},`  
        `headers={"X-API-Key": st.secrets["API_KEY"]},`  
        `timeout=10`  
    `)`  
    `response.raise_for_status()`  
    `return response.json()`

Cette séparation garantit :

* une indépendance totale entre frontend et modèle,

* une meilleure maintenabilité,

* la possibilité de remplacer l’interface sans impacter le backend.

---

## **4.5 Affichage des résultats**

Une fois la réponse reçue, l’interface affiche :

* le Pokémon vainqueur,

* le pourcentage de confiance associé à la prédiction,

* la distribution des probabilités pour chaque Pokémon.

Les résultats sont présentés de manière visuelle afin de faciliter la compréhension par un utilisateur non technique.

Cette restitution est essentielle pour rendre le modèle **exploitant et crédible**.

---

## **4.6 Gestion des erreurs et résilience**

L’application Streamlit intègre une gestion des erreurs côté client :

* indisponibilité de l’API,

* erreur réseau,

* réponse invalide.

En cas de problème, un message clair est affiché à l’utilisateur, sans exposition d’informations techniques sensibles.

Cette approche améliore la robustesse globale du système et l’expérience utilisateur.

---

## **4.7 Respect des normes d’accessibilité**

L’interface a été conçue en respectant des principes d’accessibilité :

* textes lisibles et contrastés,

* icônes explicites,

* hiérarchie visuelle claire,

* interactions simples et explicites.

Ces éléments garantissent une utilisation confortable de l’application, même pour des utilisateurs peu familiers avec les outils numériques.

---

## **4.8 Validation de l’intégration**

L’intégration complète a été validée par :

* des tests d’intégration automatisés (Streamlit → API → modèle),

* des tests manuels lors de la démonstration du projet,

* la vérification des temps de réponse et de la cohérence des résultats.

Cette validation confirme que le modèle est **correctement intégré et exploitable dans une application réelle**, conformément aux attentes du bloc E3.

# **5\. Monitoring, qualité et amélioration continue du modèle**

## **5.1 Objectifs du monitoring**

Une fois le modèle d’intelligence artificielle mis à disposition et intégré dans une application cliente, il est nécessaire d’en **assurer le suivi en conditions réelles d’utilisation**.

Le monitoring mis en place dans le projet PredictionDex vise à :

* surveiller le bon fonctionnement de l’API de prédiction,

* mesurer la performance opérationnelle du modèle,

* détecter d’éventuelles dérives des données ou des prédictions,

* permettre une amélioration continue du système.

Cette démarche s’inscrit pleinement dans une approche **MLOps**, attendue pour la validation du bloc E3.

---

## **5.2 Architecture du monitoring**

Le dispositif de monitoring repose sur une architecture standard et éprouvée :

* **FastAPI** : exposition des métriques applicatives et métier,

* **Prometheus** : collecte périodique des métriques,

* **Grafana** : visualisation et tableaux de bord,

* **Système d’alertes** : détection automatique d’anomalies.

Les métriques sont exposées directement par l’API et collectées en temps réel lors des appels de prédiction.

---

## **5.3 Métriques suivies**

Les métriques suivies couvrent à la fois les aspects techniques et métier.

### **Métriques techniques**

* nombre total de requêtes de prédiction,

* latence des prédictions,

* taux d’erreur des endpoints,

* disponibilité du service.

### **Métriques métier**

* distribution des vainqueurs prédits,

* score de confiance moyen,

* évolution des probabilités retournées,

* fréquence d’utilisation du modèle.

Ces métriques permettent d’avoir une vision globale de l’utilisation et du comportement du modèle en production.

---

## **5.4 Suivi de la performance du modèle**

Bien que la vérité terrain ne soit pas toujours disponible en production, plusieurs indicateurs indirects sont suivis :

* stabilité des scores de confiance,

* cohérence de la distribution des classes,

* comparaison avec les performances mesurées lors de la phase de validation.

Toute variation significative déclenche une analyse plus approfondie afin de déterminer si une dégradation du modèle est en cours.

---

## **5.5 Détection de dérives (Data Drift et Concept Drift)**

Le projet PredictionDex intègre un mécanisme de **détection de dérive**, essentiel pour garantir la fiabilité du modèle dans le temps.

### **Dérive des données (Data Drift)**

La dérive des données est détectée en comparant les distributions des données d’entrée en production avec celles du jeu de données de référence.

Des tests statistiques, tels que le **test de Kolmogorov-Smirnov**, sont utilisés pour identifier des écarts significatifs.

### **Dérive des prédictions (Concept Drift)**

La dérive des prédictions est évaluée à l’aide d’indicateurs comme le **Population Stability Index (PSI)**, permettant de mesurer les variations dans la distribution des sorties du modèle.

Lorsque des seuils prédéfinis sont dépassés, une alerte est générée.

---

## **5.6 Visualisation et alertes**

Les tableaux de bord Grafana permettent :

* une visualisation en temps réel des métriques,

* l’analyse historique des performances,

* l’identification rapide d’anomalies.

Des seuils d’alerte sont définis pour :

* la latence excessive,

* une augmentation anormale du taux d’erreur,

* une dérive significative des données ou des prédictions.

Ces alertes permettent une réaction rapide avant que la qualité du service ne soit impactée.

---

## **5.7 Amélioration continue du modèle**

Le monitoring constitue un levier essentiel pour l’amélioration continue du modèle.

Les informations collectées peuvent conduire à :

* un réentraînement du modèle avec de nouvelles données,

* une modification du feature engineering,

* un ajustement des hyperparamètres,

* une mise à jour de la version du modèle en production.

Grâce au versioning des modèles et au registre MLflow, chaque amélioration est tracée et reproductible.

---

## **5.8 Bénéfices de l’approche mise en place**

L’approche adoptée dans PredictionDex apporte plusieurs bénéfices :

* fiabilité accrue du modèle en production,

* anticipation des dégradations de performance,

* meilleure compréhension de l’usage réel,

* alignement avec les bonnes pratiques MLOps.

Cette démarche démontre une **maîtrise complète du cycle de vie d’un modèle d’intelligence artificielle**, au-delà de sa simple conception.

# **6\. Tests automatisés et chaîne de livraison continue**

## **6.1 Enjeux de la qualité et de l’automatisation**

Dans un projet d’intelligence artificielle déployé en production, la qualité ne repose pas uniquement sur la performance du modèle, mais également sur :

* la fiabilité du code,

* la reproductibilité des résultats,

* la stabilité des déploiements.

Le projet PredictionDex intègre une chaîne complète de **tests automatisés et de livraison continue**, garantissant la robustesse de l’ensemble du système.

Cette démarche répond directement aux compétences **C12** et **C13** du bloc E3.

---

## **6.2 Stratégie globale de tests**

La stratégie de tests adoptée couvre l’intégralité du cycle de vie du projet :

| Type de test | Objectif |
| ----- | ----- |
| Tests unitaires | Vérifier les fonctions et modules isolés |
| Tests d’intégration | Valider les échanges entre services |
| Tests du pipeline ML | Garantir la qualité des données et du modèle |
| Tests de performance | Mesurer la latence et la stabilité |
| Tests de bout en bout | Vérifier la chaîne complète |

Cette approche multi-niveaux permet de détecter les erreurs le plus tôt possible.

---

## **6.3 Tests des données et du pipeline ML**

Des tests spécifiques sont dédiés aux données d’entraînement :

* absence de valeurs manquantes,

* cohérence des plages de valeurs,

* équilibre des classes,

* absence de fuite de données.

Le pipeline de préparation et d’entraînement est testé afin de garantir que :

* les transformations sont reproductibles,

* les features générées sont conformes aux attentes,

* le modèle respecte des seuils minimaux de performance.

Ces contrôles sont essentiels pour éviter la mise en production d’un modèle dégradé.

---

## **6.4 Tests du modèle**

Le modèle est soumis à des tests automatisés portant sur :

* l’accuracy,

* le F1-score,

* la stabilité des prédictions,

* la latence d’inférence.

Des seuils minimaux sont définis, et tout modèle ne les respectant pas est rejeté.

Cette validation systématique garantit un niveau de qualité constant dans le temps.

---

## **6.5 Tests de l’API et de l’intégration**

Les endpoints de l’API FastAPI sont testés automatiquement :

* validation des réponses HTTP,

* cohérence des formats JSON,

* gestion des erreurs.

Des tests d’intégration vérifient également le bon fonctionnement de la chaîne :  
 **Streamlit → API → Modèle**.

Cette étape confirme que le modèle est réellement exploitable par une application cliente.

---

## **6.6 Chaîne d’intégration continue (CI)**

Une chaîne d’intégration continue est mise en place à l’aide de **GitHub Actions**.

À chaque push ou pull request :

1. le code est analysé (lint, typage),

2. les tests unitaires et d’intégration sont exécutés,

3. la couverture de code est mesurée,

4. les tests ML sont lancés.

Tout échec bloque automatiquement la suite du pipeline, empêchant l’introduction de régressions.

---

## **6.7 Chaîne de déploiement continu (CD)**

Une fois les tests validés, la chaîne de déploiement continu permet :

* la construction automatique des images Docker,

* leur publication dans un registre,

* le déploiement sur un environnement cible.

La promotion vers la production est contrôlée afin de garantir la stabilité du service.

Cette automatisation réduit les erreurs humaines et accélère la mise à disposition des nouvelles versions.

---

## **6.8 Versioning et gestion du cycle de vie du modèle**

Le versioning des modèles est assuré via **MLflow Model Registry** :

* chaque version est associée à un ensemble de métriques,

* les modèles sont promus ou archivés selon leurs performances,

* la version en production est clairement identifiée.

Cette gestion permet de :

* comparer les modèles dans le temps,

* revenir à une version antérieure si nécessaire,

* garantir la traçabilité des décisions.

---

## **6.9 Bénéfices de l’approche CI/CD**

La mise en place d’une chaîne CI/CD complète apporte :

* une fiabilité accrue des déploiements,

* une amélioration continue du modèle,

* une réduction des risques en production,

* une meilleure collaboration entre les différentes composantes du projet.

Elle démontre une **maîtrise avancée des pratiques MLOps**, attendue pour la validation du bloc E3.

---

# **7\. Démonstration du projet PredictionDex**

## **7.1 Objectifs de la démonstration**

La démonstration du projet PredictionDex a pour objectif de **présenter le fonctionnement opérationnel du système complet**, depuis l’infrastructure technique jusqu’à l’utilisation du modèle d’intelligence artificielle par un utilisateur final.

Elle vise à :

* prouver que le modèle est réellement déployé,

* illustrer l’intégration entre les différents composants,

* démontrer la maîtrise de la mise en production et du cycle de vie du modèle.

Cette démonstration constitue un élément obligatoire pour la validation du bloc E3.

---

## **7.2 Contexte de la démonstration**

La démonstration est réalisée dans un environnement local conteneurisé, identique à l’environnement de développement.

L’ensemble des services est lancé via Docker Compose :

* base de données,

* API FastAPI,

* modèle d’intelligence artificielle,

* interface Streamlit,

* outils de monitoring et de tracking.

---

## **7.3 Scénario de démonstration (5 à 10 minutes)**

### **Étape 1 – Lancement de l’infrastructure (≈ 30 secondes)**

L’ensemble des services est démarré à l’aide de Docker Compose.

Objectifs :

* montrer que l’architecture est opérationnelle,

* vérifier l’état des conteneurs.

---

### **Étape 2 – Interface utilisateur Streamlit (≈ 2 minutes)**

L’interface Streamlit est ouverte dans le navigateur.

Actions réalisées :

* navigation vers la page de prédiction de combat,

* sélection de deux Pokémon,

* affichage de leurs statistiques et informations,

* déclenchement de la prédiction.

Objectif :

* illustrer l’expérience utilisateur,

* montrer l’appel au modèle sans interaction technique.

---

### **Étape 3 – Résultat de la prédiction (≈ 1 minute)**

Une fois la prédiction effectuée :

* le vainqueur est affiché,

* le score de confiance est présenté,

* la distribution des probabilités est visualisée.

Objectif :

* démontrer la restitution claire et compréhensible du résultat.

---

### **Étape 4 – API REST et documentation (≈ 1 minute)**

La documentation Swagger de l’API est ouverte.

Actions réalisées :

* consultation des endpoints disponibles,

* test manuel de l’endpoint de prédiction.

Objectif :

* prouver l’accessibilité et la documentation du service exposant le modèle.

---

### **Étape 5 – Monitoring et métriques (≈ 2 minutes)**

Les tableaux de bord Grafana sont affichés.

Éléments présentés :

* nombre de prédictions effectuées,

* latence des appels,

* métriques métier,

* éventuelles alertes.

Objectif :

* démontrer le suivi en temps réel du modèle en production.

---

### **Étape 6 – Tracking et versioning du modèle (≈ 1 minute)**

L’interface MLflow est consultée.

Éléments présentés :

* historique des entraînements,

* métriques des différentes versions,

* version actuellement en production.

Objectif :

* illustrer la gestion du cycle de vie du modèle.

---

### **Étape 7 – Chaîne CI/CD (≈ 1 minute)**

Le dépôt GitHub du projet est présenté.

Éléments montrés :

* workflows GitHub Actions,

* exécution réussie des pipelines,

* automatisation des tests et du déploiement.

Objectif :

* démontrer la fiabilité et l’automatisation du projet.

---

## **7.4 Points clés mis en avant lors de la démonstration**

La démonstration insiste sur :

* la cohérence de l’architecture,

* la mise à disposition effective du modèle,

* l’intégration applicative complète,

* le monitoring et la qualité,

* l’automatisation du cycle de vie.

Ces éléments permettent au jury d’évaluer concrètement la maîtrise des compétences du bloc E3.

---

## **7.5 Conclusion de la démonstration**

La démonstration du projet PredictionDex confirme que :

* le modèle d’intelligence artificielle est fonctionnel,

* il est correctement déployé et exposé,

* il est surveillé et maintenu dans le temps,

* il est intégré dans une application réelle.

Elle clôture la validation opérationnelle du bloc E3.

# **8\. Conclusion et perspectives**

## **8.1 Synthèse du projet PredictionDex**

Le projet PredictionDex a permis de concevoir, entraîner et déployer un modèle d’intelligence artificielle complet, depuis la structuration des données jusqu’à sa mise à disposition via une application fonctionnelle.

L’ensemble des étapes du cycle de vie d’un projet IA a été maîtrisé :

* conception de l’architecture technique,

* génération et préparation des données,

* entraînement et évaluation du modèle,

* déploiement sous forme de service exposé,

* intégration applicative,

* supervision et automatisation.

Cette démarche démontre une compréhension globale et opérationnelle des enjeux liés à la mise en production d’un modèle d’intelligence artificielle.

---

## **8.2 Validation des compétences du bloc E3**

Le projet répond aux exigences du bloc E3 du référentiel Simplon en couvrant l’ensemble des compétences attendues :

* mise à disposition d’un modèle via une API documentée,

* intégration du modèle dans une application utilisable,

* automatisation des tests et des déploiements,

* gestion du versioning et du cycle de vie du modèle,

* supervision et suivi des performances.

Chaque compétence a été illustrée par des choix techniques cohérents et justifiés, assurant la robustesse et la pérennité du système.

---

## **8.3 Apports professionnels et techniques**

La réalisation de PredictionDex a permis de développer :

* une méthodologie de travail orientée production,

* une maîtrise des outils MLOps,

* une capacité à concevoir des architectures scalables,

* une approche rigoureuse de la qualité logicielle.

Ce projet a également renforcé la capacité à articuler données, modèle et application dans un contexte réaliste.

---

## **8.4 Limites actuelles du projet**

Certaines limites ont été identifiées :

* dépendance à un dataset synthétique,

* complexité limitée des stratégies de combat simulées,

* absence de données issues de parties réelles.

Ces limites sont connues, assumées et documentées, et n’impactent pas la validité du projet dans le cadre de la certification.

---

## **8.5 Perspectives d’évolution**

Plusieurs axes d’amélioration sont envisageables :

* enrichissement du dataset par des combats réels,

* amélioration du moteur de simulation,

* prise en compte de stratégies avancées,

* ajout de modèles plus complexes,

* déploiement sur une infrastructure cloud.

Ces perspectives ouvrent la voie à une évolution du projet vers un produit plus complet et plus performant.

---

## **8.6 Conclusion finale**

Le projet PredictionDex constitue une démonstration concrète de la capacité à concevoir et mettre en production un système d’intelligence artificielle opérationnel.

Il valide pleinement les compétences attendues pour le bloc E3 du diplôme Simplon et illustre une approche professionnelle, rigoureuse et orientée usage.

---

