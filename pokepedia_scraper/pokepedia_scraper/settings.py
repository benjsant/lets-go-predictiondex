"""
Scrapy settings for pokepedia_scraper

Projet pédagogique – Pokémon Let's Go (LGPE)
Objectif :
- Scraping responsable de Poképédia
- Données éducatives (mécaniques Pokémon)
- Conforme E1 (identification, robots.txt, logs, cache)

Auteur : Projet letsgo_predictiondex
"""

# ==================================================
# 🧱 Configuration de base Scrapy
# ==================================================

BOT_NAME = "pokepedia_scraper"

SPIDER_MODULES = ["pokepedia_scraper.spiders"]
NEWSPIDER_MODULE = "pokepedia_scraper.spiders"


# ==================================================
# 🧑‍💻 Identification claire du bot (IMPORTANT E1)
# ==================================================
# → Transparence totale sur l'usage
# → Poképédia peut identifier l'intention pédagogique

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0 Safari/537.36 "
    "(Educational project – Pokémon Let's Go data analysis)"
)


# ==================================================
# 🤖 Respect strict des règles du site
# ==================================================

ROBOTSTXT_OBEY = True


# ==================================================
# 🐢 Comportement humain / non agressif
# ==================================================
# Objectif :
# - Ne pas surcharger Poképédia
# - Simuler un utilisateur réel
# - Rester dans des seuils acceptables

CONCURRENT_REQUESTS = 8
CONCURRENT_REQUESTS_PER_DOMAIN = 2

DOWNLOAD_DELAY = 1.2
RANDOMIZE_DOWNLOAD_DELAY = True

DOWNLOAD_TIMEOUT = 15


# ==================================================
# 🔁 Retry contrôlé (erreurs réseau uniquement)
# ==================================================
# Pas de spam :
# - Peu de retries
# - Seulement pour erreurs serveur ou timeout

RETRY_ENABLED = True
RETRY_TIMES = 2

RETRY_HTTP_CODES = [
    500, 502, 503, 504, 522, 524, 408
]


# ==================================================
# 🚦 AutoThrottle (adaptation automatique)
# ==================================================
# Scrapy adapte la vitesse selon la réponse du site

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1.0
AUTOTHROTTLE_MAX_DELAY = 5.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = False


# ==================================================
# 🧪 Pipelines (post-traitement des données)
# ==================================================
# Centralisation :
# - nettoyage
# - normalisation
# - futur stockage BDD

ITEM_PIPELINES = {
    "pokepedia_scraper.pipelines.PokemonMovePipeline": 300,
}


# ==================================================
# 💾 Cache HTTP (ESSENTIEL pour Poképédia)
# ==================================================
# Objectifs :
# - Éviter de re-scraper inutilement
# - Réduire la charge serveur
# - Accélérer le dev / debug

HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600  # 1 heure
HTTPCACHE_DIR = "httpcache"

HTTPCACHE_IGNORE_HTTP_CODES = [
    500, 502, 503, 504
]

HTTPCACHE_STORAGE = (
    "scrapy.extensions.httpcache.FilesystemCacheStorage"
)


# ==================================================
# 📜 Logs propres et exploitables
# ==================================================

LOG_LEVEL = "INFO"


# ==================================================
# 📤 Export & encodage
# ==================================================

FEED_EXPORT_ENCODING = "utf-8"


# ==================================================
# ⚙️ Compatibilité Scrapy moderne (>= 2.10)
# ==================================================

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"

TWISTED_REACTOR = (
    "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
)
