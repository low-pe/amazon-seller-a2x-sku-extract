# amazon-seller-a2x-sku-extract

This script assists Amazon.com sellers in associating their A2X SKUs with the actual product name, making it easier to perform reconciliation or COGS-related tasks.

99% of the data can be matched using the criteria defined in main.py:

{ "sender": "donotreply@amazon.com", "title_keyword": "Refund Initiated for Order", "description": "Refund Initiated" }

{ "sender": "seller-notification@amazon.com", "title_keyword": "Sold, ship now", "description": "Sold Ship Now" }

{ "sender": "seller-notification@amazon.com", "title_keyword": "Amazon Listing Created -", "description": "Listing Created" }

We'll be adding additional criteria in the future, including support for Canada and Mexico, as A2X supports those marketplaces.

This script uses gpt-3.5-turbo to assist in identifying product names from the body of the email, as the verbiage can vary.

While the script runs, it provides a progress bar indicating completion percentage, as well as a "SKUs per second" metric, useful if you're processing thousands of SKUs.

The results are stored in sku_results.csv, in a comma-delimited format:

SKU,Item Name,Email Subject

This format helps with troubleshooting, especially if you're trying to determine which type of email the SKU was found in.

Once the script is complete, a Discord webhook will be sent with a summary of how many new SKUs were identified.

# Instructions:
1) Update updatesheets.py to include your spreadsheet ID

This sheet should be in the format of an A2X costs export, for example:

sku	cost	name	fnsku	last-seen

2) Update auth.py with your gmail, gmail app password, and openAI token

3) Update credentials.json with your google sheets API project credentials

4) Update main.py with a discord webhook

5) Add the list of your skus to skus.txt

Optional: skuremoval.py can help clean up local SKU clutter

## How to run:

```
python3 main.py
```
It will ask you where your sku list is, tell it skus.txt
```
python3 updatesheets.py
```
