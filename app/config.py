import os

# Elasticsearch Configuration
ELESTICSEARCH_WWW = os.getenv("ELASTICSEARCH_WWW", "http")
ELESTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "localhost")
ELESTICSEARCH_PORT = int(os.getenv("ELASTICSEARCH_PORT", 9200))
ELESTICSEARCH_INDEX = os.getenv("ELASTICSEARCH_INDEX", "newsgroups")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Data Loading Configuration
DEFAULT_MAX_DOCUMENTS = int(os.getenv("DEFAULT_MAX_DOCUMENTS", 1000))
DEFAULT_SUBSET = os.getenv("DEFAULT_SUBSET", "train")

# API Configuration
MAX_BULK_SIZE = int(os.getenv("MAX_BULK_SIZE", 1000))
DEFAULT_SEARCH_LIMIT = int(os.getenv("DEFAULT_SEARCH_LIMIT", 10))
MAX_SEARCH_LIMIT = int(os.getenv("MAX_SEARCH_LIMIT", 100))