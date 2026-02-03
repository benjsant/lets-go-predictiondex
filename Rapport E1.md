# **Rapport E1 – Conception et structuration des données**

## **1\. Contexte et objectifs**

Le projet PredictionDex s’inscrit dans le cadre de la validation du bloc de compétences E1 du diplôme Simplon, portant sur la conception et la structuration des données nécessaires à un projet d’intelligence artificielle.

L’objectif de ce rapport est de démontrer la capacité à :

* analyser un besoin applicatif,  
* concevoir un modèle de données cohérent,  
* implémenter une base de données exploitable par un système IA,  
* exposer ces données via des interfaces adaptées.

Le projet repose sur l’univers du jeu *Pokémon Let’s Go*, avec pour finalité la prédiction de l’issue d’un combat entre deux Pokémon.

---

## **2\. Analyse du besoin et contraintes**

Le besoin fonctionnel principal est de disposer de données fiables et structurées permettant :

* de représenter les Pokémon et leurs caractéristiques,  
* de gérer les types et leurs interactions,  
* de décrire les capacités et leurs effets,  
* de supporter des simulations de combat.

Les contraintes identifiées sont :

* absence de dataset directement exploitable,  
* règles métiers complexes issues du jeu,  
* nécessité d’un modèle extensible et normalisé.

---

## **3\. Conception du modèle de données**

### **3.1 Choix méthodologiques**

La conception s’est appuyée sur une approche relationnelle classique, avec une normalisation visant à :

* éviter la redondance des données,  
* garantir la cohérence,  
* faciliter l’évolution du schéma.

Le Modèle Physique de Données (MPD) a été privilégié, car directement exploitable pour l’implémentation.

### **3.2 Présentation du MPD**

Le MPD comprend notamment les entités suivantes :

* Pokémon  
* Types  
* Capacités (Moves)  
* Tables d’association (Pokémon ↔ Types, Pokémon ↔ Capacités)  
* Table d’efficacité des types

Ce modèle permet de représenter fidèlement les règles du jeu tout en restant générique.

*(Le MPD détaillé est fourni en annexe)*

---

## **4\. Implémentation de la base de données**

La base de données a été implémentée sous PostgreSQL.

Les choix techniques incluent :

* utilisation de clés primaires et étrangères,  
* contraintes d’intégrité référentielle,  
* typage strict des champs.

L’implémentation permet une exploitation directe par les services applicatifs et les pipelines de données.

---

## **5\. Accès et exposition des données**

Les données sont exposées via :

* une API REST développée avec FastAPI,  
* des endpoints documentés automatiquement (Swagger).

Ces interfaces permettent :

* la consultation des Pokémon,  
* l’accès aux statistiques et capacités,  
* l’alimentation des simulations de combat.

---

## **6\. Organisation du projet (E1)**

L’arborescence du projet pour la partie E1 est structurée de la manière suivante :

* core/  
  * db/  
  * models/  
  * schemas/  
* api/  
  * routes/  
* data/  
  * seeds/

Cette organisation facilite la maintenance, la lisibilité et l’évolutivité du projet.

---

## **7\. Éléments complémentaires**

Des interfaces Streamlit ont été développées pour :

* afficher la liste des Pokémon,  
* consulter leurs statistiques et capacités.

Ces éléments illustrent la bonne exploitation des données mais sont considérés comme complémentaires au bloc E1.

---

## **8\. Conclusion**

Ce rapport démontre la maîtrise de la conception et de la structuration des données nécessaires à un projet d’intelligence artificielle.

Le travail réalisé constitue une base solide et cohérente pour le bloc E3, consacré à l’entraînement et à la mise à disposition du modèle IA.

