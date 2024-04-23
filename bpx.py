from bs4 import BeautifulSoup
from itertools import cycle
import concurrent.futures
from lxml import etree
import requests
import psycopg2
import csv


def get_database_connection():
    DB_CONFIG = {
        "host": "10.10.10.227",
        "database": "crawling_db",
        "user": "enrgtech",
        "password": "Enrgtech@50",
    }
    return psycopg2.connect(**DB_CONFIG)


deletedProxies = 0


def fetch_proxies():
    conn = get_database_connection()
    proxies = []
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT protocol, ip_address FROM ip_addresses")  # Assuming you have a 'port' column
            for protocol, ip_address in cur.fetchall():
                if protocol in ['socks4', 'socks5']:
                    proxy_format = f"{protocol}://{ip_address}"
                else:
                    proxy_format = f"http://{ip_address}"  # Default to HTTP if not socks
                proxies.append({'http': proxy_format, 'https': proxy_format})
    conn.close()
    return proxies


HEADERS = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'en-US,en;q=0.9',
    'Content-Length': '0',
    'Content-Type': 'text/plain',
    'Cookie': 'ar_debug=1',
    'Origin': 'https://bpx.co.uk',
    'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

NUM_OF_CHUNKS = 30


def fetch_price(mpn, proxy):
    price = 'N/A'
    try:
        response = requests.get(f'https://www.bpx.co.uk/store/product/{mpn}', headers=HEADERS, proxies=proxy, timeout=10)
        # response = requests.get(f'https://httpbin.org/ip', headers=HEADERS, proxies=proxy, timeout=10)
        if response.status_code == 200:
            print(response.status_code)
            print(proxy)
            # soup = BeautifulSoup(response.content, "html.parser")
            # dom = etree.HTML(str(soup))
            # price = dom.xpath("//div[@class='col-xs-6 product-price-ex']//p[@class='form-control-static']")[0].text
        else:
            print(f'Failed {mpn} at {proxy} status code: {response.status_code}')
    except requests.exceptions.RequestException as e:
        price = f'Error: {e}'
    return mpn, price


def process_chunk(chunk, proxy):
    return [fetch_price(mpn, proxy) for mpn, proxy in zip(chunk, cycle(proxy))]
    # return [fetch_price(mpn, proxy) for mpn in chunk]


def divide_chunks(data, n):
    for i in range(0, len(data), n):
        yield data[i:i + n]


def process_csv_file(csv_file_path):
    mpns = []
    proxies = fetch_proxies()

    # Read the MPNs from the CSV file
    with open(f'references/{csv_file_path}', mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        mpns = [row[0].strip() for row in reader if row]

    # Divide the MPNs into chunks
    chunk_size = max(len(mpns) // NUM_OF_CHUNKS, 1)
    chunks = list(divide_chunks(mpns, chunk_size))
    proxy_chunks = list(divide_chunks(proxies, chunk_size))

    # Process each chunk in parallel and maintain the order
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_OF_CHUNKS) as executor:
        results = executor.map(process_chunk, chunks, proxy_chunks)

    # Flatten the list of results
    ordered_results = [item for sublist in results for item in sublist]

    # Write the results to a new CSV file
    with open(f'updated_prices/bpx-{csv_file_path}', mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['MPN', 'Price'])  # Writing header
        writer.writerows(ordered_results)


# Example usage
process_csv_file('mpns.csv')
