from bs4 import BeautifulSoup
import concurrent.futures
from lxml import etree
import requests
import csv

HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Sec-Fetch-Mode': 'navigate',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"'
}

NUM_OF_CHUNKS = 30


def fetch_price(mpn):
    price = 'N/A'
    try:
        response = requests.get(f'https://www.tme.eu/gb/details/tme0303s/dc-dc-converters/traco-power/', headers=HEADERS)
        if response.status_code == 200:
            print(mpn, response)
            soup = BeautifulSoup(response.content, "html.parser")
            dom = etree.HTML(str(soup))
            price_elements = dom.xpath("(//script/text())[16]")
            print(price_elements)
            return
            if price_elements:
                price = price_elements.strip()
            else:
                print(mpn, "Price not found")
            print(price)
        else:
            print(f'Failed to visit {mpn} with status code: {response.status_code}')
    except requests.exceptions.RequestException as e:
        price = f'Error: {e}'
    return mpn, price

fetch_price('99')
#
# def process_chunk(chunk):
#     return [fetch_price(mpn) for mpn in chunk]
#
#
# def divide_chunks(data, n):
#     for i in range(0, len(data), n):
#         yield data[i:i + n]
#
#
# def process_csv_file(csv_file_path):
#     mpns = []
#
#     # Read the MPNs from the CSV file
#     with open(f'references/{csv_file_path}', mode='r', encoding='utf-8') as file:
#         reader = csv.reader(file)
#         mpns = [row[0].strip() for row in reader if row]
#
#     # Divide the MPNs into chunks
#     chunk_size = max(len(mpns) // NUM_OF_CHUNKS, 1)
#     chunks = list(divide_chunks(mpns, chunk_size))
#
#     # Process each chunk in parallel and maintain the order
#     with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_OF_CHUNKS) as executor:
#         results = list(executor.map(process_chunk, chunks))
#
#     # Flatten the list of results
#     ordered_results = [item for sublist in results for item in sublist]
#
#     # Write the results to a new CSV file
#     with open(f'updated_prices/scats-{csv_file_path}', mode='w', encoding='utf-8', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow(['MPN', 'Price'])  # Writing header
#         writer.writerows(ordered_results)
#
#
# # Example usage
# process_csv_file('mpns.csv')
