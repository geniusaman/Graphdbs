import openai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

from openai import OpenAI

# Load environment variables
load_dotenv()

# API and Neo4j credentials
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
NEO4J_URI = os.environ["NEO4J_URI"]
NEO4J_USERNAME = os.environ["NEO4J_USERNAME"]
NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"]

# Set up OpenAI and Neo4j driver
openai.api_key = OPENAI_API_KEY
client = OpenAI()
try:
    # Correctly initialize the driver globally
    neo4j_driver = GraphDatabase.driver(
        NEO4J_URI, 
        auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
        encrypted=True  # Use 'neo4j+s://' schemes for encryption
    )
    print("Connected to Neo4j")
except Exception as e:
    print(f"Failed to connect to Neo4j: {e}")
    neo4j_driver = None  # In case connection fails, set driver to None

# Function to retrieve embeddings from Neo4j
def get_stored_embeddings():
    if neo4j_driver is None:
        raise ConnectionError("Neo4j driver is not initialized or failed to connect.")
    
    query = """
    MATCH (n:Chunk)
    RETURN n.question AS question, n.embedding AS embedding
    """
    with neo4j_driver.session() as session:
        results = session.run(query)
        embeddings_data = [(record["question"], record["embedding"]) for record in results]
    return embeddings_data

# Function to calculate cosine similarity
def calculate_similarity(input_embedding, stored_embeddings):
    stored_embeddings_np = np.array([embedding for _, embedding in stored_embeddings])
    input_embedding_np = np.array(input_embedding).reshape(1, -1)
    similarities = cosine_similarity(input_embedding_np, stored_embeddings_np)
    return similarities

# Given input embedding and number of top-k results
def get_top_k_similar(input_embedding, k=5):
    stored_embeddings = get_stored_embeddings()
    similarities = calculate_similarity(input_embedding, stored_embeddings)
    ranked_results = sorted(
        zip(stored_embeddings, similarities[0]),
        key=lambda x: x[1], reverse=True
    )[:k]
    return ranked_results

# Class for example selection
class SemanticSimilarityExampleSelector:
    def __init__(self, similarity_function, input_keys):
        self.similarity_function = similarity_function
        self.input_keys = input_keys

    def select_examples(self, inputs):
        input_embedding = inputs[self.input_keys[0]]
        return self.similarity_function(input_embedding)

# Function to get embedding from OpenAI API
def get_embedding_from_openai(text):
    response = client.embeddings.create(
    input=text,
    model="text-embedding-3-small")
    
    return response.data[0].embedding

# Example usage: Get actual embedding for input text
input_text = "What percentage of POs were issued to suppliers based in the US?"
input_embedding = get_embedding_from_openai(input_text)

# Instantiate example selector
example_selector = SemanticSimilarityExampleSelector(
    similarity_function=get_top_k_similar,
    input_keys=["embedding"]
)

# Select examples using the correct embedding
top_k_examples = example_selector.select_examples({"embedding": input_embedding})

# Print the results
for i, (question, embedding) in enumerate(top_k_examples):
    print(f"Rank {i+1}: Question: {question}")

