# eBayExtract

eBayExtract is a Python script that retrieves active eBay listings using the eBay API and prints them in a readable XML format or outputs them to a CSV file.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Filtering Listings](#filtering-listings)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/yourusername/eBayExtract.git
   cd eBayExtract
   ```

2. Create a virtual environment and activate it:

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:

   ```sh
   pip install -r requirements.txt
   ```

## Configuration

1. Create a `config.ini` file in the root directory of the project with the following content:

   ```ini
   [eBayAPI]
   IAF_TOKEN = your_ebay_api_token
   ```

## Usage

Run the script to fetch and print active eBay listings:

```sh
python main.py
```

## Filtering Listings

To filter the listings based on item IDs specified in `items.txt`, run the `filter.py` script:

```sh
python filter.py
```

This will generate a `filtered_ebay_listings.csv` file containing only the listings with item IDs specified in `items.txt`.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
