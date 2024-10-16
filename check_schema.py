from dotenv import load_dotenv
import os

# Read local .env file
load_dotenv()

# Environment variables
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
NEO4J_URI = os.environ["NEO4J_URI"]
NEO4J_USERNAME = os.environ["NEO4J_USERNAME"]
NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"]

# Initialize Neo4jGraph
from langchain_community.graphs import Neo4jGraph
graph = Neo4jGraph()
enhanced_graph = Neo4jGraph(
    url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD,
    enhanced_schema=True,
)
# Fetch the schema
schema = graph.query("CALL apoc.meta.schema()")

# Write schema to a txt file
schema_str = str(schema)  # Ensure the schema is in string format
with open("graph_schema.txt", "w") as file:
    file.write(schema_str)

print("Graph schema has been written to graph_schema.txt")