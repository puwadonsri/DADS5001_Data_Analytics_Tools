import sys
import pytchat
import pymongo
from pymongo.errors import ConnectionFailure

VIDEO_ID = "brE8_gE014w"
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "youtube"
COLLECTION_NAME = "chat_log"

def main():
    print(f"Connecting to YouTube Live: {VIDEO_ID}")
    try:
        chat = pytchat.create(video_id=VIDEO_ID)
    except Exception as e:
        print(f"Failed to create pytchat instance: {e}")
        sys.exit(1)

    try:
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
    except ConnectionFailure:
        print("Cannot connect to MongoDB. Make sure MongoDB is running.")
        sys.exit(1)

    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    print("Listening for chat messages... (Press Ctrl+C to stop)")
    try:
        while chat.is_alive():
            for c in chat.get().sync_items():
                print(f"{c.datetime} [{c.author.name}]: {c.message}")
                data = {
                    'dateTime': c.datetime,
                    'authorName': c.author.name,
                    'Message': c.message,
                }
                collection.insert_one(data)
    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        print(f"Error during chat capture: {e}")
    finally:
        client.close()
        print(f"Chat data saved to MongoDB ({DB_NAME}.{COLLECTION_NAME})")

if __name__ == "__main__":
    main()
