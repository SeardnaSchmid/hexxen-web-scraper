import requests
from bs4 import BeautifulSoup
import csv
import urllib.parse

def extract_beast_info(individual_beast_soup, source_url):
    # Extract relevant information from the individual beast page
    name = individual_beast_soup.find('div', class_='ce_text first block').find('h1').text.strip()
    band = individual_beast_soup.find('div', class_='ce_text first block').find('p').text.strip()
    stats = individual_beast_soup.find('div', class_='ce_text block').find('p').text.strip()
    publication = individual_beast_soup.find('div', class_='ce_text last block').find('p').text.strip()

    return {'Name': name, 'Band': band, 'Stats': stats, 'Publication': publication, 'SourceURL': source_url}

def scrape_beast_data(main_url, root_url, items_scraped_limit):
    main_response = requests.get(main_url)
    main_soup = BeautifulSoup(main_response.text, 'html.parser')

    # Find links to different types of beasts
    beast_type_links = main_soup.find_all('a', class_='ulSubMenu')

    data_to_store = []
    items_scraped = 0  # Counter for the number of items scraped

    # Loop through each beast type and get links to individual beasts
    for beast_type_link in beast_type_links:
        print(f"Scraping beast type: {beast_type_link.text}")

        # Check if the href starts with "index.php/" and handle accordingly
        if beast_type_link['href'].startswith('index.php/'):
            beast_type_url = urllib.parse.urljoin(root_url, beast_type_link['href'])
        else:
            beast_type_url = beast_type_link['href']

        beast_type_response = requests.get(beast_type_url)
        print(f"Requesting URL: {beast_type_url}")

        beast_type_soup = BeautifulSoup(beast_type_response.text, 'html.parser')

        # Find links to individual beasts
        individual_beast_links = beast_type_soup.find_all('a', class_='ulSubMenu')

        # Loop through each individual beast and extract information
        for individual_beast_link in individual_beast_links:
            print(f"Scraping individual beast: {individual_beast_link.text}")

            # Check if the href starts with "index.php/" and handle accordingly
            if individual_beast_link['href'].startswith('index.php/'):
                individual_beast_url = urllib.parse.urljoin(root_url, individual_beast_link['href'])
            else:
                individual_beast_url = individual_beast_link['href']

            individual_beast_response = requests.get(individual_beast_url)
            print(f"Requesting URL: {individual_beast_url}")

            individual_beast_soup = BeautifulSoup(individual_beast_response.text, 'html.parser')

            # Extract relevant information from the individual beast page
            extracted_info = extract_beast_info(individual_beast_soup, individual_beast_url)
            extracted_info['Type'] = beast_type_link.text.strip()
            data_to_store.append(extracted_info)

            items_scraped += 1
            if items_scraped >= items_scraped_limit:
                break  # Break out of the loop when the specified number of items are scraped

        if items_scraped >= items_scraped_limit:
            break  # Break out of the outer loop when the specified number of items are scraped

    return data_to_store

def write_to_csv(data_to_store, csv_file_path):
    fieldnames = ['Name', 'Band', 'Stats', 'Publication', 'SourceURL', 'Type']
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for entry in data_to_store:
            writer.writerow(entry)

    print(f'Data has been written to {csv_file_path}')

# Example usage
main_url = 'http://hexxen1733-regelwiki.de/index.php/Hex_Bestiarium.html'
root_url = 'http://hexxen1733-regelwiki.de/'
items_scraped_limit = 5
csv_file_path = 'beastiary_data.csv'

beast_data = scrape_beast_data(main_url, root_url, items_scraped_limit)
write_to_csv(beast_data, csv_file_path)
