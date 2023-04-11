import argparse
from elasticsearch import Elasticsearch

def main():
    parser = argparse.ArgumentParser(description='Lists dashboards in Elasticsearch.')
    parser.add_argument('--host', type=str, required=True, help='Elasticsearch host')
    parser.add_argument('--user', type=str, required=True, help='Elasticsearch user')
    parser.add_argument('--password', type=str, required=True, help='Elasticsearch password')
    parser.add_argument('--index', type=str, default='.kibana_1', help='Elasticsearch index')
    parser.add_argument('-help', '--help', action='help', default=argparse.SUPPRESS, help='Show this help message and exit')
    args = parser.parse_args()

    es = Elasticsearch(
        [args.host],
        http_auth=(args.user, args.password),
        scheme='https',
        port=443,
    )

    res = es.search(index=args.index, body={'query': {'match_all': {}}})
    hits = res['hits']['hits']
    dashboards = [hit['_source']['title'] for hit in hits if hit['_source']['type'] == 'dashboard']
    print(dashboards)

if __name__ == '__main__':
    main()

