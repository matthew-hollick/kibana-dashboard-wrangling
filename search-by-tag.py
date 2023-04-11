import argparse
from elasticsearch import Elasticsearch

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Search all dashboards for a specified tag.")
    parser.add_argument("--host", required=True, help="Elasticsearch host URL.")
    parser.add_argument("--user", required=True, help="Elasticsearch username for authentication.")
    parser.add_argument("--password", required=True, help="Elasticsearch password for authentication.")
    parser.add_argument("--tag", required=True, help="Tag to search for in dashboards.")
    parser.add_argument("--index", default=".kibana", help="Elasticsearch index to search in. Default is '.kibana'.")
    args = parser.parse_args()

    # Connect to Elasticsearch
    es = Elasticsearch(args.host, http_auth=(args.user, args.password))

    # Search for dashboards with the specified tag
    search_query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "type": "dashboard"
                        }
                    },
                    {
                        "term": {
                            f"tags.keyword": args.tag
                        }
                    }
                ]
            }
        }
    }

    search_results = es.search(index=args.index, body=search_query)

    # Print the dashboards that have the specified tag along with their titles
    print(f"Dashboards with tag '{args.tag}':")
    for hit in search_results["hits"]["hits"]:
        dashboard_id = hit["_id"]
        dashboard_title = hit["_source"]["title"]
        print(f"{dashboard_id} - {dashboard_title}")

if __name__ == "__main__":
    main()

