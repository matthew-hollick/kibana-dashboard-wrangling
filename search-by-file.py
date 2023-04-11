import argparse
from elasticsearch import Elasticsearch

def main():
    parser = argparse.ArgumentParser(description='Lists dashboards in Elasticsearch that are in a specified file.')
    parser.add_argument('--host', type=str, required=True, help='Elasticsearch host')
    parser.add_argument('--user', type=str, required=True, help='Elasticsearch user')
    parser.add_argument('--password', type=str, required=True, help='Elasticsearch password')
    parser.add_argument('--file', type=str, required=True, help='File containing a list of dashboard names')
    parser.add_argument('--index', type=str, default='.kibana_1', help='Elasticsearch index')
    parser.add_argument('-help', '--help', action='help', default=argparse.SUPPRESS, help='Show this help message and exit')
    args = parser.parse_args()

    es = Elasticsearch(
        [args.host],
        http_auth=(args.user, args.password),
        scheme='https',
        port=443,
    )

    with open(args.file, 'r') as f:
        dashboard_names = [line.strip() for line in f.readlines()]

    res = es.search(index=args.index, body={'query': {'match_all': {}}})
    hits = res['hits']['hits']
    dashboard_titles = [hit['_source']['title'] for hit in hits if hit['_source']['type'] == 'dashboard']
    matching_dashboards = set(dashboard_names) & set(dashboard_titles)
    non_matching_dashboards = set(dashboard_names) - set(dashboard_titles)

    print('Matching dashboards:')
    for dashboard_name in matching_dashboards:
        print(dashboard_name)

    print('Non-matching dashboards:')
    for dashboard_name in non_matching_dashboards:
        print(dashboard_name)

if __name__ == '__main__':
    main()

