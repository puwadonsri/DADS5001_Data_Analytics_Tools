import csv
import re
import pandas as pd
import pymongo
from pymongo.errors import ConnectionFailure

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "youtube"
CHAT_COLLECTION = "chat_log"
ANALYTICS_COLLECTION = "chat_analytics"

def load_chat_data(collection):
    data = list(collection.find())
    if not data:
        return pd.DataFrame()
    records = []
    for doc in data:
        vals = list(doc.values())
        records.append({
            'Date': vals[1][0:10] if len(vals) > 1 else '',
            'Name': vals[2] if len(vals) > 2 else '',
            'Chat': vals[3] if len(vals) > 3 else ''
        })
    return pd.DataFrame(records)

def load_stock_codes(csv_path="json_dataset/company.csv"):
    df_set = pd.read_csv(csv_path)
    return df_set['SET_CODE'].dropna().astype(str).str.strip().tolist()

def count_stock_mentions(df_chat, stock_codes):
    results = []
    for code in stock_codes:
        if not code:
            continue
        pattern = r'\b' + re.escape(code) + r'\b'
        try:
            match_count = df_chat['Chat'].str.contains(
                pattern, na=False, case=False, regex=True
            ).sum()
        except re.error:
            continue
        if match_count > 0:
            results.append({'setName': code, 'setAmount': int(match_count)})
    return results

def save_results(collection, results):
    collection.delete_many({})
    if results:
        collection.insert_many(results)

def main():
    try:
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
    except ConnectionFailure:
        print("Cannot connect to MongoDB. Make sure MongoDB is running.")
        return

    db = client[DB_NAME]
    chat_collection = db[CHAT_COLLECTION]
    analytics_collection = db[ANALYTICS_COLLECTION]

    print("Loading chat data...")
    df_chat = load_chat_data(chat_collection)
    if df_chat.empty:
        print("No chat data found in MongoDB.")
        client.close()
        return
    print(f"Loaded {len(df_chat)} chat messages.")

    print("Loading stock codes from company.csv...")
    stock_codes = load_stock_codes()
    print(f"Loaded {len(stock_codes)} stock codes.")

    print("Counting stock mentions (using word-boundary regex matching)...")
    results = count_stock_mentions(df_chat, stock_codes)

    if results:
        results.sort(key=lambda x: x['setAmount'], reverse=True)
        print(f"Found mentions for {len(results)} stocks. Top 10:")
        for r in results[:10]:
            print(f"  {r['setName']}: {r['setAmount']} mentions")
    else:
        print("No stock mentions found.")

    print("Saving results to MongoDB...")
    save_results(analytics_collection, results)
    print("Done!")

    client.close()

if __name__ == "__main__":
    main()
