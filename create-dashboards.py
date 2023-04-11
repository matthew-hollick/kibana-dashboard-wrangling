import argparse
import random
import string
from elasticsearch import Elasticsearch

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Create empty dashboards with random titles.")
    parser.add_argument("--host", required=True, help="Elasticsearch host URL.")
    parser.add_argument("--user", required=True, help="Elasticsearch username for authentication.")
    parser.add_argument("--password", required=True, help="Elasticsearch password for authentication.")
    parser.add_argument("--count", type=int, required=True, help="Number of dashboards to create.")
    parser.add_argument("--tags", nargs="+", required=True, help="Tags to apply to the dashboards.")
    parser.add_argument("--index", default=".kibana", help="Elasticsearch index to create dashboards in. Default is '.kibana'.")
    args = parser.parse_args()

    # Connect to Elasticsearch
    es = Elasticsearch(args.host, http_auth=(args.user, args.password))

    # Generate random dashboard titles and create empty dashboards with specified tags
    for i in range(args.count):
        dashboard_title = "".join(random.choices(string.ascii_letters, k=10))
        dashboard_doc = {
            "type": "dashboard",
            "title": dashboard_title,
            "panelsJSON": "[]",
            "optionsJSON": "{}",
            "version": 1,
            "timeRestore": False,
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": "{\"query\":{\"query\":\"\",\"language\":\"lucene\"},\"filter\":[]}"
            },
            "attributes": {
                "description": "",
                "hits": 0,
                "kibanaSavedObjectMeta": {
                    "searchSourceJSON": "{\"query\":{\"query\":\"\",\"language\":\"lucene\"},\"filter\":[]}"
                },
                "title": dashboard_title,
                "uiStateJSON": "{}",
                "version": 1
            },
            "references": [],
            "migrationVersion": {
                "dashboard": "7.16.0"
            },
            "updated_at": "2023-04-12T00:00:00.000Z"
        }

        # Apply specified tags to the dashboard
        dashboard_doc["attributes"]["tags"] = args.tags

        # Save the dashboard to Elasticsearch
        es.create(index=args.index, doc_type="_doc", body=dashboard_doc)

        print(f"Created dashboard with title '{dashboard_title}' and tags '{args.tags}'.")

if __name__ == "__main__":
    main()

