import pandas as pd
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")

# Check connection
client.admin.command("ping")
print("MongoDB connection established successfully!")

# Database and collection
db = client["supermarket_sales"]
collection = db["sales"]

# Read CSV
df = pd.read_csv("supermarket_sales.csv")

# Insert data
data = df.to_dict("records")
collection.insert_many(data)

print("Data imported successfully!")
print("Total records:", collection.count_documents({}))