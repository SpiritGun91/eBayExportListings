import csv

# Define the input and output file names
input_file = 'combined_listings.csv'
output_file = 'ebay_listings_no_model_size.csv'

# Read the input CSV file and write to the output CSV file with the "Model" and "Size" columns empty
with open(input_file, mode='r', encoding='utf-8') as infile, open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames
    
    # Ensure the "Model" and "Size" columns are present
    if "Model" not in fieldnames or "Size" not in fieldnames:
        raise ValueError("The input CSV file does not contain 'Model' or 'Size' columns.")
    
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for row in reader:
        row["Model"] = ""  # Empty the "Model" column
        row["Size"] = ""   # Empty the "Size" column
        writer.writerow(row)

print(f"New CSV file created: {output_file}")