import csv

def map_ebay_to_amazon(row):
    image_urls = row['Image URLs'].split(', ')
    return {
        "sku": row['Item ID'],  # Use eBay ItemID as SKU
        "title": row['Title'][:200],  # Trim to 200 chars for Amazon title
        "description": row['Description'].replace('<p>', '').replace('</p>', '').strip(),  # Clean up HTML
        "standard_price": f"{float(row['Current Price']):.2f}",  # Format price to 2 decimal places
        "quantity": int(row['Quantity']),
        "main_image": image_urls[0],  # Assuming the first image is the main image
        "other_images": ', '.join(image_urls[1:]),  # Join the remaining images as other_images
        "condition_type": map_condition(row['Condition']),  # Map eBay condition to Amazon
        "attributes": {
            "color": row['Colors']
        },
        "brand": row['Brand'],
        "model": row['Model'],
        "size": row['Size'],
        "external_product_id": "",  # Assuming no UPC available
        "external_product_id_type": ""
    }

def map_condition(ebay_condition):
    """ Map eBay condition to Amazon condition types """
    condition_map = {
        "New with tags": "New",
        "New without tags": "New",
        "Pre-owned": "Used - Good"
    }
    return condition_map.get(ebay_condition, "Used - Good")  # Default to "Used - Good"

def convert_csv_to_amazon_format(input_csv, output_csv):
    with open(input_csv, 'r', encoding='utf-8') as infile, open(output_csv, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = ["sku", "title", "description", "standard_price", "quantity", "main_image", "other_images", "condition_type", "attributes", "brand", "model", "size", "external_product_id", "external_product_id_type"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            amazon_row = map_ebay_to_amazon(row)
            writer.writerow(amazon_row)

# Convert the filtered eBay listings to Amazon format
convert_csv_to_amazon_format('filtered_ebay_listings.csv', 'amazon_product_listings.csv')
