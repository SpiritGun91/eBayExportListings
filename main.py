import asyncio
import aiohttp
import configparser
from lxml import etree
import csv

# Read the IAF_TOKEN from config.ini
config = configparser.ConfigParser()
config.read('config.ini')
IAF_TOKEN = config['eBayAPI']['IAF_TOKEN']

# eBay API endpoint
EBAY_API_ENDPOINT = 'https://api.ebay.com/ws/api.dll'

async def fetch(session, url, data, headers):
    async with session.post(url, data=data, headers=headers) as response:
        response.raise_for_status()
        return await response.text()

async def get_ebay_listings():
    page_number = 1
    all_listings = []

    async with aiohttp.ClientSession() as session:
        while True:
            print(f"Fetching page {page_number}...")

            # XML request body for GetMyeBaySelling with pagination
            xml_request_body = f"""
            <?xml version="1.0" encoding="utf-8"?>
            <GetMyeBaySellingRequest xmlns="urn:ebay:apis:eBLBaseComponents">    
                <ErrorLanguage>en_US</ErrorLanguage>
                <WarningLevel>High</WarningLevel>
                <DetailLevel>ReturnAll</DetailLevel>
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

            try:
                response_text = await fetch(session, EBAY_API_ENDPOINT, xml_request_body, headers)
                root = etree.fromstring(response_text.encode('utf-8'))
                active_list = root.find('.//{urn:ebay:apis:eBLBaseComponents}ActiveList')
                if active_list is not None:
                    items = active_list.findall('.//{urn:ebay:apis:eBLBaseComponents}Item')
                    if not items:
                        break
                    all_listings.extend(items)
                    page_number += 1
                else:
                    break

            except Exception as err:
                print(f"An error occurred: {err}")
                break

    return all_listings

async def get_item_details(session, item_id):
    # XML request body for GetItem
    xml_request_body = f"""
    <?xml version="1.0" encoding="utf-8"?>
    <GetItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
        <ErrorLanguage>en_US</ErrorLanguage>
        <WarningLevel>High</WarningLevel>
        <DetailLevel>ReturnAll</DetailLevel>
        <ItemID>{item_id}</ItemID>
    </GetItemRequest>
    """

    # HTTP headers
    headers = {
        'X-EBAY-API-SITEID': '0',
        'X-EBAY-API-COMPATIBILITY-LEVEL': '967',
        'X-EBAY-API-CALL-NAME': 'GetItem',
        'X-EBAY-API-IAF-TOKEN': IAF_TOKEN,
    }

    try:
        response_text = await fetch(session, EBAY_API_ENDPOINT, xml_request_body, headers)
        root = etree.fromstring(response_text.encode('utf-8'))
        return root

    except Exception as err:
        print(f"An error occurred: {err}")

    return None

async def main():
    listings = await get_ebay_listings()
    print(f"Total listings fetched: {len(listings)}")

    async with aiohttp.ClientSession() as session:
        tasks = []
        for listing in listings:
            item_id = listing.find('.//{urn:ebay:apis:eBLBaseComponents}ItemID').text
            print(f"Fetching details for item ID: {item_id}")
            tasks.append(get_item_details(session, item_id))

        item_details_list = await asyncio.gather(*tasks)

        try:
            # Open CSV file for writing
            with open('ebay_listings.csv', mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # Write CSV headers
                writer.writerow([
                    'ItemID', 'Title', 'Price', 'Currency', 'Category', 'Condition', 'Quantity', 
                    'ListingType', 'StartTime', 'EndTime', 'Location', 'Seller', 'WatchCount', 
                    'HitCount', 'ShippingCost', 'ReturnPolicy', 'PictureURLs'
                ])

                for item_details in item_details_list:
                    if item_details is not None:
                        item_id = item_details.find('.//{urn:ebay:apis:eBLBaseComponents}ItemID')
                        title = item_details.find('.//{urn:ebay:apis:eBLBaseComponents}Title')
                        price = item_details.find('.//{urn:ebay:apis:eBLBaseComponents}CurrentPrice')
                        currency = item_details.find('.//{urn:ebay:apis:eBLBaseComponents}CurrentPrice')
                        category = item_details.find('.//{urn:ebay:apis:eBLBaseComponents}PrimaryCategory')
                        category_name = category.find('.//{urn:ebay:apis:eBLBaseComponents}CategoryName') if category is not None else None
                        condition = item_details.find('.//{urn:ebay:apis:eBLBaseComponents}ConditionDisplayName')
                        quantity = item_details.find('.//{urn:ebay:apis:eBLBaseComponents}Quantity')
                        listing_type = item_details.find('.//{urn:ebay:apis:eBLBaseComponents}ListingType')
                        start_time = item_details.find('.//{urn:ebay:apis:eBLBaseComponents}StartTime')
                        end_time = item_details.find('.//{urn:ebay:apis:eBLBaseComponents}EndTime')
                        location = item_details.find('.//{urn:ebay:apis:eBLBaseComponents}Location')
                        seller = item_details.find('.//{urn:ebay:apis:eBLBaseComponents}Seller')
                        seller_user_id = seller.find('.//{urn:ebay:apis:eBLBaseComponents}UserID') if seller is not None else None
                        watch_count = item_details.find('.//{urn:ebay:apis:eBLBaseComponents}WatchCount')
                        hit_count = item_details.find('.//{urn:ebay:apis:eBLBaseComponents}HitCount')
                        shipping_cost_summary = item_details.find('.//{urn:ebay:apis:eBLBaseComponents}ShippingCostSummary')
                        shipping_cost = shipping_cost_summary.find('.//{urn:ebay:apis:eBLBaseComponents}ShippingServiceCost') if shipping_cost_summary is not None else None
                        return_policy = item_details.find('.//{urn:ebay:apis:eBLBaseComponents}ReturnPolicy')
                        returns_accepted_option = return_policy.find('.//{urn:ebay:apis:eBLBaseComponents}ReturnsAcceptedOption') if return_policy is not None else None
                        picture_urls = item_details.findall('.//{urn:ebay:apis:eBLBaseComponents}PictureURL')

                        picture_urls_text = ', '.join([url.text for url in picture_urls if url is not None])

                        writer.writerow([
                            item_id.text if item_id is not None else '',
                            title.text if title is not None else '',
                            price.text if price is not None else '',
                            currency.attrib['currencyID'] if currency is not None else '',
                            category_name.text if category_name is not None else '',
                            condition.text if condition is not None else '',
                            quantity.text if quantity is not None else '',
                            listing_type.text if listing_type is not None else '',
                            start_time.text if start_time is not None else '',
                            end_time.text if end_time is not None else '',
                            location.text if location is not None else '',
                            seller_user_id.text if seller_user_id is not None else '',
                            watch_count.text if watch_count is not None else '',
                            hit_count.text if hit_count is not None else '',
                            shipping_cost.text if shipping_cost is not None else '',
                            returns_accepted_option.text if returns_accepted_option is not None else '',
                            picture_urls_text
                        ])
        except Exception as e:
            print(f"An error occurred while writing to the CSV file: {e}")

# Run the main function
asyncio.run(main())
