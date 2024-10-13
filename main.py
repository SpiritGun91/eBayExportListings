import asyncio
import aiohttp
import configparser
import csv
from lxml import etree, html

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
    max_retries = 5
    retry_delay = 1  # Initial delay in seconds

    async with aiohttp.ClientSession() as session:
        while True:
            print(f"Fetching page {page_number}...")

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

            headers = {
                'X-EBAY-API-SITEID': '0',
                'X-EBAY-API-COMPATIBILITY-LEVEL': '967',
                'X-EBAY-API-CALL-NAME': 'GetMyeBaySelling',
                'X-EBAY-API-IAF-TOKEN': IAF_TOKEN,
                'Content-Type': 'text/xml'
            }

            for attempt in range(max_retries):
                try:
                    response_text = await fetch(session, EBAY_API_ENDPOINT, xml_request_body, headers)
                    root = etree.fromstring(response_text.encode('utf-8'))

                    ack = root.find(".//{urn:ebay:apis:eBLBaseComponents}Ack")
                    if ack is not None and ack.text == "Failure":
                        print("Error: API call failed.")
                        errors = root.findall(".//{urn:ebay:apis:eBLBaseComponents}Errors")
                        for error in errors:
                            short_message = error.find(".//{urn:ebay:apis:eBLBaseComponents}ShortMessage").text
                            long_message = error.find(".//{urn:ebay:apis:eBLBaseComponents}LongMessage").text
                            print(f"Error: {short_message} - {long_message}")
                        if "usage limit" in long_message.lower():
                            print(f"Retrying in {retry_delay} seconds...")
                            await asyncio.sleep(retry_delay)
                            retry_delay *= 2  # Exponential backoff
                            continue
                        else:
                            break

                    items = root.findall(".//{urn:ebay:apis:eBLBaseComponents}Item")
                    all_listings.extend(items)

                    total_pages_element = root.find(".//{urn:ebay:apis:eBLBaseComponents}TotalNumberOfPages")
                    if total_pages_element is None:
                        print("Error: TotalNumberOfPages element not found in the response.")
                        print("Response text:", response_text)
                        break

                    total_pages = int(total_pages_element.text)
                    if page_number >= total_pages:
                        return all_listings  # Exit the loop if all pages are fetched

                    page_number += 1
                    retry_delay = 1  # Reset delay after a successful request
                    break
                except Exception as e:
                    print(f"Exception occurred: {e}")
                    print(f"Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff

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

    headers = {
        'X-EBAY-API-SITEID': '0',
        'X-EBAY-API-COMPATIBILITY-LEVEL': '967',
        'X-EBAY-API-CALL-NAME': 'GetItem',
        'X-EBAY-API-IAF-TOKEN': IAF_TOKEN,
        'Content-Type': 'text/xml'
    }

    try:
        response_text = await fetch(session, EBAY_API_ENDPOINT, xml_request_body, headers)
        return etree.fromstring(response_text.encode('utf-8'))
    except Exception as err:
        print(f"Error fetching details for item {item_id}: {err}")
        return None

async def main():
    listings = await get_ebay_listings()
    print(f"Total listings fetched: {len(listings)}")

    async with aiohttp.ClientSession() as session:
        tasks = []
        for item in listings:
            item_id = item.find("{urn:ebay:apis:eBLBaseComponents}ItemID").text
            title = item.find("{urn:ebay:apis:eBLBaseComponents}Title").text
            current_price = item.find(".//{urn:ebay:apis:eBLBaseComponents}CurrentPrice").text
            quantity = item.find("{urn:ebay:apis:eBLBaseComponents}Quantity").text
            time_left = item.find("{urn:ebay:apis:eBLBaseComponents}TimeLeft").text
            watch_count = item.find("{urn:ebay:apis:eBLBaseComponents}WatchCount").text if item.find("{urn:ebay:apis:eBLBaseComponents}WatchCount") is not None else "N/A"

            tasks.append(get_item_details(session, item_id))

        item_details_list = await asyncio.gather(*tasks)

        with open('ebay_listings.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Item ID", "Title", "Current Price", "Quantity", "Time Left", "Watch Count", "Description", "Image URLs"])

            for item, item_details in zip(listings, item_details_list):
                if item_details is not None:
                    description = item_details.find(".//{urn:ebay:apis:eBLBaseComponents}Description")
                    if description is not None:
                        description_html = html.fromstring(description.text)
                        description_text = description_html.text_content()
                    else:
                        description_text = "N/A"

                    picture_urls = item_details.findall(".//{urn:ebay:apis:eBLBaseComponents}PictureURL")
                    picture_urls_text = ', '.join([pic.text for pic in picture_urls]) if picture_urls else "N/A"

                    writer.writerow([
                        item.find("{urn:ebay:apis:eBLBaseComponents}ItemID").text,
                        item.find("{urn:ebay:apis:eBLBaseComponents}Title").text,
                        item.find(".//{urn:ebay:apis:eBLBaseComponents}CurrentPrice").text,
                        item.find("{urn:ebay:apis:eBLBaseComponents}Quantity").text,
                        item.find("{urn:ebay:apis:eBLBaseComponents}TimeLeft").text,
                        item.find("{urn:ebay:apis:eBLBaseComponents}WatchCount").text if item.find("{urn:ebay:apis:eBLBaseComponents}WatchCount") is not None else "N/A",
                        description_text,
                        picture_urls_text
                    ])

# Run the main function
asyncio.run(main())
