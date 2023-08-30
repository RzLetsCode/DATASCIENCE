# BitcoinTalk.org Scraper

This is a Python script for scraping and analyzing data from a Bitcoin Talk forum topic. The script fetches posts from multiple pages of a specified topic, performs sentiment analysis, and stores the data in a PostgreSQL database.

## Installation

Before running the script, please install the required Python libraries using the following command:

```bash
pip install -r requirements.txt
```

## Database Setup

1. Create a PostgreSQL database with a table to store the scraped data. You can use the following SQL code as a template:

```sql
CREATE TABLE bitcoin_talk (
    post_id int,
    post_url varchar(500),
    post_timestamp timestamp,
    post_page int,
    post_author varchar(255),
    post_full varchar,
    post_no_quote varchar,
    topic_name varchar(500),
    sentiment_compound float,
    sentiment_positive float,
    sentiment_negative float,
    inserted_timestamp timestamp
);
```

Replace `database_table_name` with your desired table name.

2. Update the connection information in the `connection.py` file with your PostgreSQL database details.

## Usage

1. Run the script `main.py` to initiate the data scraping and analysis process.

```bash
python main.py
```

The script will retrieve posts from the specified Bitcoin Talk topic, perform sentiment analysis using VADER, and insert the processed data into the specified PostgreSQL database table.

2. The script will check for existing post IDs in the database before inserting new data, ensuring that duplicate entries are not added.

3. The sentiment analysis scores (compound, positive, and negative) are calculated for each post and stored in the database.

4. The `inserted_timestamp` field is automatically populated with the current date and time.

## Notes

- This script assumes you have a PostgreSQL database set up and accessible with the provided connection information.

- Ensure you have the necessary permissions to create tables and insert data into the specified database.

- The script relies on web scraping techniques, so any changes to the structure of the Bitcoin Talk forum could potentially affect its functionality.

- This script is intended as a starting point and can be customized or extended based on your specific requirements.

Happy data scraping!
```

Replace `database_table_name` with your actual table name and update any other placeholders as needed. This README file provides instructions on installation, database setup, and usage of your Bitcoin Talk scraper script.