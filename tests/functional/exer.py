from elasticsearch import AsyncElasticsearch

es_client = AsyncElasticsearch(
        # hosts=test_settings.es_url_to_connect,
        "http://localhost:9200/",
        verify_certs=False
    )

print(es_client)