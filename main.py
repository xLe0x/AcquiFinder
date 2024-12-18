import os
from dotenv import load_dotenv
from apify_client import ApifyClient
from re import findall
import sys
from termcolor import colored


def load_api_key():
    load_dotenv()
    api_key = os.getenv("Apify_API_KEY")
    if not api_key:
        raise ValueError(colored(
            "API key not found. Please set Apify_API_KEY in your .env file.", "red"))
    return api_key


def perform_scrape(client, company_name):
    query = f'site:crunchbase.com "{company_name} acquires"'
    run_input = {
        "queries": query,
        "resultsPerPage": 100,
        "maxPagesPerQuery": 10,
    }

    try:
        run = client.actor(
            "apify/google-search-scraper").call(run_input=run_input)
        return client.dataset(run["defaultDatasetId"]).iterate_items()
    except Exception as e:
        raise RuntimeError(colored(f"Scraping failed: {e}", "red"))


def extract_acquisitions(company_name, dataset_items):
    titles = [res["title"]
              for item in dataset_items for res in item.get("organicResults", [])]
    pattern = rf"{company_name} acquires ([^-]+)"
    acquisitions = findall(pattern, " ".join(titles))
    return acquisitions


def save_acquisitions_to_file(acquisitions, company_name):
    file_name = f"{company_name}_acquisitions.txt"
    with open(file_name, "w") as file:
        for acquisition in acquisitions:
            file.write(f"{acquisition.strip()}\n")
    print(colored(f"\nAcquisitions saved to {file_name}", "green"))


def main(company_name):
    try:
        api_key = load_api_key()
        client = ApifyClient(api_key)

        dataset_items = perform_scrape(client, company_name)

        acquisitions = extract_acquisitions(company_name, dataset_items)

        if acquisitions:
            print(colored("\nAcquisitions found:", "green"))
            for acquisition in acquisitions:
                print(colored(f"{acquisition.strip()}", "cyan"))
            save_acquisitions_to_file(acquisitions, company_name)
        else:
            print(colored("\nNo acquisitions found for the given company.", "yellow"))

    except Exception as e:
        print(colored(f"Error: {e}", "red"))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(colored("Usage: python main.py <company_name>", "yellow"))
        sys.exit(1)

    company_name_arg = sys.argv[1]
    main(company_name_arg)
