import requests
import configparser
from lxml import etree

# Read the IAF_TOKEN from config.ini
config = configparser.ConfigParser()
config.read('config.ini')
IAF_TOKEN = config['eBayAPI']['IAF_TOKEN']

# eBay API endpoint
EBAY_API_ENDPOINT = 'https://api.ebay.com/ws/api.dll'

def get_ebay_listings():
    page_number = 1
    all_listings = []

    while True:
        # XML request body for GetMyeBaySelling with pagination
        xml_request_body = f"""
        <?xml version="1.0" encoding="utf-8"?>
        <GetMyeBaySellingRequest xmlns="urn:ebay:apis:eBLBaseComponents">    
            <ErrorLanguage>en_US</ErrorLanguage>
            <WarningLevel>High</WarningLevel>
            <ActiveList>
                <Sort>TimeLeft</Sort>
                <Pagination>
                    <EntriesPerPage>200</EntriesPerPage>
                    <PageNumber>{page_number}</PageNumber>
                </Pagination>
            </ActiveList>
        </GetMyeBaySellingRequest>
        """

        # HTTP headers
        headers = {
            'X-EBAY-API-SITEID': '0',
            'X-EBAY-API-COMPATIBILITY-LEVEL': '967',
            'X-EBAY-API-CALL-NAME': 'GetMyeBaySelling',
            'X-EBAY-API-IAF-TOKEN': IAF_TOKEN,
        }

        # Send the request
        response = requests.post(EBAY_API_ENDPOINT, data=xml_request_body, headers=headers)

        # Check the response status
        if response.status_code == 200:
            # Parse the response XML
            root = etree.fromstring(response.content)
            active_list = root.find('.//{urn:ebay:apis:eBLBaseComponents}ActiveList')
            if active_list is not None:
                items = active_list.findall('.//{urn:ebay:apis:eBLBaseComponents}Item')
                if not items:
                    break
                all_listings.extend(items)
                page_number += 1
            else:
                break
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            break

    return all_listings

listings = get_ebay_listings()
for listing in listings:
    print(etree.tostring(listing, pretty_print=True, encoding='utf8').decode('utf8'))