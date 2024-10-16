from langchain.chains import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
from examples import examples
from langchain_community.vectorstores import Neo4jVector
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate


load_dotenv() # read local .env file

GROQ_API_KEY = os.environ["GROQ_API_KEY"]
OPENAI_API_KEY =  os.environ["OPENAI_API_KEY"]
NEO4J_URI = os.environ["NEO4J_URI"]
NEO4J_USERNAME = os.environ["NEO4J_USERNAME"]
NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"]

graph = Neo4jGraph()
enhanced_graph = Neo4jGraph(
    url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD,
    enhanced_schema=True,
)
llm = ChatGroq(
    model="llama-3.1-70b-versatile",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,  
)
# llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)


print(graph._enhanced_schema)

# example_selector = SemanticSimilarityExampleSelector.from_examples(
#     examples,
#     OpenAIEmbeddings(),
#     Neo4jVector,
#     k=5,
#     input_keys=["question"],
# )
# # print(example_selector.select_examples({"question": "how many artists are there?"}))

# example_prompt = PromptTemplate.from_template(
#     "User input: {question}\nCypher query: {query}"
# )

# prompt = FewShotPromptTemplate(
#     examples=examples,
#     example_prompt=example_prompt,
#     prefix="""Task: Generate a Cypher statement to query a graph database.
#             Instructions:
#             You are a Neo4j expert. Given an input question, create a syntactically correct Cypher query to run.
#             Use only the provided relationship types and properties in the schema.
#             Do not use any other relationship types or properties that are not provided.
#             Schema:
#             {schema}

#             Note: Do not include any explanations or apologies in your responses.
#             Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
#             Do not include any text except the generated Cypher statement.
#             The date format should be YYYY-MM-DD.
#             If the generated Cypher query contains a date, convert it to date format instead of directly matching with a string. Example: (d.date >= date("2023-01-01") AND d.date <= date("2023-12-31")).
#             Before making any Cypher query, please check the schema to match the cases of the nodes and relationships strictly.
#             Double check the Cypher query before executing it. It should be syntactically correct.

#             Below are a number of examples of questions and their corresponding Cypher queries:"""
# ,
#     suffix="User input: {question}\nCypher query: ",
#     input_variables=["question", "schema"],
# )

# # print(prompt.format(question="How many artists are there?", schema="foo"))

# chain = GraphCypherQAChain.from_llm(       
#     graph=enhanced_graph, llm=llm, cypher_prompt=prompt, verbose=True, allow_dangerous_requests=True
# )

# print(chain.invoke("Which parent category has the highest total spend?"))

