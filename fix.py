import csv

# Define the input and output file names
ebay_listings_file = 'ebay_listings.csv'
messed_up_file = 'messed_up.csv'
output_file = 'combined_listings.csv'

# Read the ebay_listings.csv file to get all relevant information
listings_info = {}
with open(ebay_listings_file, mode='r', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        listings_info[row['Item ID']] = row

# Read the messed_up.csv file and combine with listings_info
with open(messed_up_file, mode='r', encoding='utf-8') as infile, open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for row in reader:
        item_id = row['Item ID']
        if item_id in listings_info:
            for key in fieldnames:
                if key in listings_info[item_id]:
                    row[key] = listings_info[item_id][key]
        writer.writerow(row)

print(f"New CSV file created: {output_file}")