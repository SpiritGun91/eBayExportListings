import csv

# Read item IDs from items.txt
with open('items.txt', 'r') as file:
    item_ids = {line.strip() for line in file}

# Read ebay_listings.csv and filter rows
filtered_rows = []
with open('ebay_listings.csv', 'r', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    header = next(reader)
    filtered_rows.append(header)
    
    for row in reader:
        if row[0] in item_ids:
            filtered_rows.append(row)

# Write filtered rows to a new CSV file
with open('filtered_ebay_listings.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(filtered_rows)