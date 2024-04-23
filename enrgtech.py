from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
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


def fetch_price(url):
    try:
        response = requests.get(url, headers=HEADERS)
        print(response)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            dom = etree.HTML(str(soup))
            price_elements = dom.xpath("(//span[@class='text-orange fw-600'])[1]")
            price = price_elements[0].text.strip() if price_elements else 'N/A'
        else:
            print(f'Failed to visit {url} with status code: {response.status_code}')
            price = 'Failed'
    except requests.exceptions.RequestException as e:
        print(f'An error occurred while trying to visit {url}: {e}')
        price = 'Error'
    return url, price


# Function to process URLs in chunks with parallel requests
def process_urls_in_chunks(csv_file_path, output_file_path, chunk_size=10):
    urls = []

    # Load URLs from CSV
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        urls = [row[0].strip() for row in reader if row and row[0].strip()]

    with open(output_file_path, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['URL', 'Price'])

        # Process each chunk of URLs
        for i in range(0, len(urls), chunk_size):
            with ThreadPoolExecutor() as executor:
                futures = [executor.submit(fetch_price, url) for url in urls[i:i + chunk_size]]
                for future in as_completed(futures):
                    url, price = future.result()
                    writer.writerow([url, price])


# Update these paths as necessary
csv_file_path = 'updated_prices/enrgtech_urls.csv'
output_file_path = 'newEnrgtech.csv'

process_urls_in_chunks(csv_file_path, output_file_path)
