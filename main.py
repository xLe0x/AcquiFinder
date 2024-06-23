from apify_client import ApifyClient
from re import findall
import os
from dotenv import load_dotenv

load_dotenv()

apify_API_KEY = os.getenv("Apify_API_KEY")
client = ApifyClient(apify_API_KEY)
company_name = input("What is the company name? $ ")


run_input = {
    "queries": f"""site:crunchbase.com "{company_name} acquires" """,
    "resultsPerPage": 100,
    "maxPagesPerQuery": 1,
}
run = client.actor("apify/google-search-scraper").call(run_input=run_input)

titles = []

for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    for res in item["organicResults"]:
        titles.append(res["title"])


pattern = rf"{company_name} acquires ([^-]+)"

acquisitions = findall(pattern, str(titles))

for acquisition in acquisitions:
    print(acquisition)
