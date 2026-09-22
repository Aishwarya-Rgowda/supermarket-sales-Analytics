import pandas as pd
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")

# Test connection
client.admin.command("ping")
print("MongoDB connection established successfully!")

# Select database and collection
db = client["supermarket_sales"]
collection = db["sales"]

# Read CSV
df = pd.read_csv("supermarket_sales.csv")

print("CSV records:", len(df))

# Convert to dictionary
data = df.to_dict("records")

# Insert into MongoDB
if collection.count_documents({}) == 0:
    collection.insert_many(data)
    print("Data inserted successfully!")
else:
    print("Collection already contains data. No duplicate data inserted.")

# Show final count
print("Total records in MongoDB:", collection.count_documents({}))

client.close()