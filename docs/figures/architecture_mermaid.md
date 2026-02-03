# Architecture Technique

```mermaid
flowchart TB
    subgraph Sources["📥 Sources de Données"]
        PA[PokéAPI]
        PP[Pokepedia]
        CSV[Fichiers CSV]
    end
    
    subgraph ETL["🔄 Pipeline ETL"]
        EXT[Extraction]
        TRANS[Transformation]
        LOAD[Chargement]
    end
    
    subgraph Storage["💾 Stockage"]
        PG[(PostgreSQL)]
        MLF[(MLflow)]
    end
    
    subgraph ML["🤖 Machine Learning"]
        TRAIN[Entraînement]
        MODEL[XGBoost v2]
    end
    
    subgraph API["🔌 API REST"]
        FAST[FastAPI]
        PRED[/predict]
        DATA[/pokemon]
    end
    
    subgraph Frontend["🖥️ Interface"]
        ST[Streamlit]
    end
    
    subgraph Monitoring["📊 Monitoring"]
        PROM[Prometheus]
        GRAF[Grafana]
        DRIFT[Drift Detection]
    end
    
    PA --> EXT
    PP --> EXT
    CSV --> EXT
    EXT --> TRANS
    TRANS --> LOAD
    LOAD --> PG
    
    PG --> TRAIN
    TRAIN --> MODEL
    TRAIN --> MLF
    MODEL --> FAST
    
    PG --> DATA
    MODEL --> PRED
    
    FAST --> ST
    FAST --> PROM
    PROM --> GRAF
    FAST --> DRIFT
    
    style MODEL fill:#FF6B6B,color:white
    style PG fill:#336791,color:white
    style FAST fill:#009688,color:white
    style ST fill:#FF4B4B,color:white
    style GRAF fill:#F46800,color:white

```
