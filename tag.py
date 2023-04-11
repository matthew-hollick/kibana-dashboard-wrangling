import argparse
from elasticsearch import Elasticsearch

def main():
    parser = argparse.ArgumentParser(description='Lists dashboards in Elasticsearch that are in a specified file and adds a tag to each matching dashboard.')
    parser.add_argument('--host', type=str, required=True, help='Elasticsearch host')
    parser.add_argument('--user', type=str, required=True, help='Elasticsearch user')
    parser.add_argument('--password', type=str, required=True, help='Elasticsearch password')
    parser.add_argument('--file', type=str, required=True, help='File containing a list of dashboard names')
    parser.add_argument('--tag', type=str, required=True, help='Tag name to add to matching dashboards')
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
    dashboard_ids = [hit['_id'] for hit in hits if hit['_source']['type'] == 'dashboard']
    dashboard_titles = [hit['_source']['title'] for hit in hits if hit['_source']['type'] == 'dashboard']
    matching_dashboard_ids = set([dashboard_ids[i] for i in range(len(dashboard_titles)) if dashboard_titles[i] in dashboard_names])

    for dashboard_id in matching_dashboard_ids:
        res = es.update(
            index=args.index,
            id=dashboard_id,
            body={
                "doc": {
                    "tags": args.tag
                }
            }
        )

    print(f'{len(matching_dashboard_ids)} dashboards were found and tagged.')

if __name__ == '__main__':
    main()

