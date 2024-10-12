# eBayExportListings

eBayExportListings is a Python script that retrieves active eBay listings using the eBay API and prints them in a readable XML format or outputs them to a CSV file.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [License](#license)

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/yourusername/eBayExportListings.git
   cd eBayExportListings
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

This will generate a csv file with all your listings.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
