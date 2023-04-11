import argparse
from elasticsearch import Elasticsearch

def main():
    parser = argparse.ArgumentParser(description='Lists dashboards in Elasticsearch that are in a specified file and adds a tag to each matching dashboard. Also deletes dashboards in Elasticsearch that have the specified tag but are not in the dashboard file.')
    parser.add_argument('--host', type=str, required=True, help='Elasticsearch host')
    parser.add_argument('--user', type=str, required=True, help='Elasticsearch user')
    parser.add_argument('--password', type=str, required=True, help='Elasticsearch password')
    parser.add_argument('--file', type=str, required=True, help='File containing a list of dashboard names')
    parser.add_argument('--tag', type=str, required=True, help='Tag name to add to matching dashboards and delete from non-matching dashboards')
    parser.add_argument('--index', type=str, default='.kibana_1', help='Elasticsearch index')
    parser.add_argument('-y', '--yes', action='store_true', help='Delete non-matching dashboards without prompting for confirmation')
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

    non_matching_dashboard_ids = set([hit['_id'] for hit in hits if args.tag in hit['_source']['tags'] and hit['_source']['type'] == 'dashboard']) - matching_dashboard_ids

    if non_matching_dashboard_ids:
        if args.yes:
            delete = True
        else:
            print(f'The following {len(non_matching_dashboard_ids)} dashboards have the tag "{args.tag}" but are not in the file:')
            for dashboard_id in non_matching_dashboard_ids:
                print(f'- {dashboard_id}')
            response = input(f'Do you want to delete these dashboards? (y/n) ')
            delete = True if response.lower() == 'y' else False

        if delete:
            for dashboard_id in non_matching_dashboard_ids:
                res = es.delete(
                    index=args.index,
                    id=dashboard_id,
                )
            print(f'{len(non_matching_dashboard_ids)} dashboards were deleted.')
        else:
            print('No dashboards were deleted.')
    else:
        print('No dashboards were found with the specified tag that are not in the file.')

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

