#https://www.mongodb.com/developer/products/atlas/building-generative-ai-applications-vector-search-open-source-models/


# Connect to your MongoDB instance
import pymongo

client = pymongo.MongoClient("mongodb+srv://ringinmotion:ringinmotion@dlmongodbatlasvectorsea.ujuqjwz.mongodb.net/?retryWrites=true&w=majority")
db = client.sample_mflix
collection = db.embedded_movies


# Set up the embedding creation function
import requests

hf_token = ""
embedding_url = ""

def generate_embedding(text: str) -> list[float]:

	response = requests.post(
		embedding_url,
		headers={"Authorization": f"Bearer {hf_token}"},
		json={"inputs": text})

	if response.status_code != 200:
		raise ValueError(f"Request failed with status code {response.status_code}: {response.text}")

	return response.json()["embeddings"]


# Test if the embeddings are working correctly
print(generate_embedding("MongoDB is awesome"))


# Create and Store the embeddings

for doc in collection.find({'plot':{"$exists": True}}).limit(100):
	doc['plot_embedding_hf'] = generate_embedding(doc['plot'])
	collection.replace_one({'_id': doc['_id']}, doc)

# Create the index on the embeddings is made in the MongoDB Atlas UI because od the free Tier

# Query the database

query = "imaginary characters from outer space at war"

results = collection.aggregate([
    {
        '$search': {
            "index": "PlotSemanticSearch",
            "knnBeta": {
                "vector": generate_embedding(query),
                "k": 4,
                "path": "plot_embedding_hf"}
        }
    }
])

for document in results:
    title = document.get("title", "No Title Available")
    plot = document.get("plot", "No Plot Available")
    print(f'Movie Name: {title},\nMovie Plot: {plot}\n')
