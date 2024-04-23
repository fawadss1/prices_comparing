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

# csv_file_path = 'references/weidmuller.csv'
#
# with open(csv_file_path, mode='r', encoding='utf-8') as file:
#     reader = csv.reader(file)
#
#     for row in reader:
#         if row and row[0].strip():
#             url = row[0].strip()
#             try:
#                 response = requests.get(f'https://www.bpx.co.uk/store/product/{url}', headers=HEADERS)
#                 if response.status_code == 200:
#                     soup = BeautifulSoup(response.content, "html.parser")
#                     dom = etree.HTML(str(soup))
#                     price = dom.xpath("//div[@class='col-xs-6 product-price-ex']//p[@class='form-control-static']")[0].text
#                 else:
#                     print(f'Failed to visit {url} with status code: {response.status_code}')
#             except requests.exceptions.RequestException as e:
#                 print(f'An error occurred while trying to visit {url}: {e}')

csv_file_paths = ['allen-bradley.csv', 'banner.csv', 'schneider.csv', 'tese-tel.csv', 'wago.csv', 'weidmuller.csv']


def process_csv_file(csv_file_path):
    rows = []
    with open(f'references/{csv_file_path}', mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            price = 'N/A'
            if row and row[0].strip():
                mpn = row[0].strip()
            try:
                response = requests.get(f'https://www.bpx.co.uk/store/product/{mpn}', headers=HEADERS)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, "html.parser")
                    dom = etree.HTML(str(soup))
                    price = dom.xpath("//div[@class='col-xs-6 product-price-ex']//p[@class='form-control-static']")[0].text
                else:
                    print(f'Failed to visit {mpn} with status code: {response.status_code} from {csv_file_path}')
                row.append(price)
            except requests.exceptions.RequestException as e:
                row.append(f'Error: {e}')
            rows.append(row)

    with open(f'updated_prices/{csv_file_path}', mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)


for path in csv_file_paths:
    process_csv_file(path)
