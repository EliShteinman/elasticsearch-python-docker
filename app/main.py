import logging
from contextlib import asynccontextmanager

from elasticsearch import Elasticsearch
from fastapi import FastAPI

import config

logging.basicConfig(
    level=config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

logger.info(
    f"Initializing Elasticsearch client with URL: {config.ELESTICSEARCH_WWW}://{config.ELESTICSEARCH_HOST}:{config.ELESTICSEARCH_PORT}")
es = Elasticsearch(f"{config.ELESTICSEARCH_WWW}://{config.ELESTICSEARCH_HOST}:{config.ELESTICSEARCH_PORT}/")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application lifespan startup")

    try:
        logger.info("Testing Elasticsearch connection")
        if not es.ping():
            logger.error("Failed to connect to Elasticsearch")
            raise Exception("Elasticsearch connection failed")

        logger.info("Elasticsearch connection successful")

        index_name = config.ELESTICSEARCH_INDEX
        logger.info(f"Working with index: {index_name}")

        mapping = {
            'properties': {
                'title': {'type': 'text'},
                'body': {'type': 'text'},
                'tag': {'type': 'keyword', 'ignore_above': 256}
            }
        }

        if not es.indices.exists(index=index_name):
            logger.info(f"Index {index_name} does not exist, creating new index")
            es.indices.create(index=index_name, mappings=mapping)
            logger.info(f"Index {index_name} created successfully")

            documents = [
                {
                    "title": "Magellan Update - Venus Mission Status",
                    "body": "Marshall is investigating a small but odd pressure rise in one SRB during the Jan 12 Endeavour launch. It lasted only three seconds and the thrust difference between the two SRBs was not enough to cause nozzle gimballing. The SRB casing shows no abnormalities. Magellan has completed 7225 orbits of Venus and is now 39 days from the end of Cycle-4 and the start of the Transition Experiment.",
                    "tag": "sci.space"
                },
                {
                    "title": "DC-1 Future Space Technology Discussion",
                    "body": "I once read an article on Computer technology which stated that every new computer technology was actually lower and slower than what it replaced. Silicon was less effective than the germanium products then available. GaAs was less capable than Silicon. Multi-processors were slower than existent single processors. The DC-1 may fit into this same model. ELV's can certainly launch more weight than a SSRT, but an SSRT offers the prospect of greater cycle times and lower costs.",
                    "tag": "sci.space"
                },
                {
                    "title": "First Spacewalk Historical Discussion",
                    "body": "At one time there was speculation that the first spacewalk (Alexei Leonov) was a staged fake. Has any evidence to support or contradict this claim emerged? Was this claim perhaps another fevered Cold War hallucination? The Apollo program cost something like 25 billion dollars at a time when the value of a dollar was worth more than it is now.",
                    "tag": "sci.space"
                }
            ]

            logger.info(f"Starting to index {len(documents)} documents")
            for idx, doc in enumerate(documents, 1):
                logger.debug(f"Indexing document {idx}: {doc['title'][:50]}...")
                es.index(index=index_name, body=doc)
                logger.debug(f"Document {idx} indexed successfully")

            logger.info("All documents indexed, refreshing index")
            es.indices.refresh(index=index_name)
            logger.info("Index refresh completed")
            logger.info("Elasticsearch initialization completed successfully")
        else:
            logger.info(f"Index {index_name} already exists, skipping initialization")

    except Exception as e:
        logger.error(f"Error during Elasticsearch initialization: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        raise

    logger.info("Application startup completed")
    yield

    logger.info("Starting application shutdown")
    logger.info("Application shutdown completed")


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Hello World"}


@app.get("/search/{term}")
async def search(term: str):
    logger.info(f"Search endpoint accessed with term: {term}")

    try:
        logger.debug(f"Building search query for term: {term}")
        query = {
            "query": {
                "match": {
                    "body": term
                }
            }
        }

        logger.debug(f"Executing search query: {query}")
        results = es.search(index=config.ELESTICSEARCH_INDEX, body=query)

        total_hits = results['hits']['total']['value']
        max_score = results['hits']['max_score']
        took = results['took']

        logger.info(f"Search completed: found {total_hits} results in {took}ms with max_score {max_score}")

        response_data = {
            "found": total_hits,
            "max_score": max_score,
            "took_ms": took,
            "results": []
        }

        logger.debug("Processing search results")
        for hit in results['hits']['hits']:
            result_item = {
                "id": hit['_id'],
                "score": hit['_score'],
                "title": hit['_source']['title'],
                "tag": hit['_source']['tag'],
                "body_preview": hit['_source']['body'][:200]
            }
            response_data["results"].append(result_item)
            logger.debug(f"Processed result: id={hit['_id']}, score={hit['_score']:.3f}")

        logger.info(f"Search response prepared with {len(response_data['results'])} results")
        return response_data

    except Exception as e:
        logger.error(f"Error during search operation: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Search term: {term}")
        return {"error": str(e), "term": term}


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting uvicorn server")
    uvicorn.run(app, host="0.0.0.0", port=8182)