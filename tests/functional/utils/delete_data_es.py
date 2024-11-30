from elasticsearch import Elasticsearch

from tests.functional.settings import test_settings

indexes = [
    "genres",
    "movies",
    "persons"
]

if __name__ == '__main__':
    es_client = Elasticsearch(hosts=test_settings.es_url_to_connect, verify_certs=False, ssl_show_warn=False)
    for index in indexes:
        print("Зачистка - ", index)
        es_client.delete_by_query(index=index, body={
                "query": {
                    "match_all": {}
                }
            }
        )