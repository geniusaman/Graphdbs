import streamlit as st
from langchain.chains import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from examples import examples
from langchain_community.vectorstores import Neo4jVector
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from streamlit_chat import message

# Load environment variables
load_dotenv()

# Set up API keys and Neo4j credentials
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
NEO4J_URI = os.environ["NEO4J_URI"]
NEO4J_USERNAME = os.environ["NEO4J_USERNAME"]
NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"]

# Initialize Neo4j graph
graph = Neo4jGraph()
enhanced_graph = Neo4jGraph(
    url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD, enhanced_schema=True,
)

schema = enhanced_graph._enhanced_schema
# Initialize the LLM (Groq)
llm = ChatGroq(
    model="llama-3.1-70b-versatile",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# Set up example selector and prompt
example_selector = SemanticSimilarityExampleSelector.from_examples(
    examples,
    OpenAIEmbeddings(),
    Neo4jVector,
    k=5,
    input_keys=["question"],
)

example_prompt = PromptTemplate.from_template(
    "User input: {question}\nCypher query: {query}"
)
qa_prompt = PromptTemplate(
    template = "User input: {question}\nCypher query result: {context}" + "\n" + f"Schema:{schema}" + "\nbased on the User input, Cypher query and Cypher query result form nice and human \nunderstandable answers\nDo not add any other information that wasn't part of the query and result, and use\nwhere ever required alway use($,',',%,-), tables and graphs to structured the output\nAlways interact with user,\nAlways approch the user to ask the comprehensive and logical questions related to Data stored in db(schema)\nif context is empty that means user should ask the correct questions which is related to stored Data in garph db(schema) and you try to fine grain the question with user if the question doesnot meets the schema.",
    input_variables = ['question','context'],
)

prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix="""Task: Generate a Cypher statement to query a graph database.
            Instructions:
            You are a Neo4j expert. Given an input question, create a syntactically correct Cypher query to run.
            Use only the provided relationship types and properties in the schema.
            Do not use any other relationship types or properties that are not provided.
            Schema:
            {schema}

            Note: Do not include any explanations or apologies in your responses.
            Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
            Do not include any text except the generated Cypher statement.
            The date format should be MM/dd/yyyy.
            Always use apoc.date.parse() to parse the date.
            If the generated Cypher query contains a date, convert it to date format instead of directly matching with a string. Example: (d.date >= date("2023-01-01") AND d.date <= date("2023-12-31")).
            Before making any Cypher query, please check the schema to match the cases of the nodes and relationships strictly.
            Double check the Cypher query before executing it. It should be syntactically correct.

            Below are a number of examples of questions and their corresponding Cypher queries:"""
,
    suffix="User input: {question}\nCypher query: ",
    input_variables=["question", "schema"],
)

Str = "You are an assistant that helps to form nice and human \nunderstandable answers based on the provided information from tools.\nDo not add any other information that wasn't present in the tools, and use \nvery concise style in interpreting results!\n"

# Initialize the chain
chain = GraphCypherQAChain.from_llm(
    graph=enhanced_graph, llm=llm, cypher_prompt=prompt, validate_cypher =True, qa_prompt=qa_prompt, function_response_system=Str, verbose=True, allow_dangerous_requests=True
)


# Streamlit App Interface
st.title("Graph Cypher Query Assistant")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Function to handle user input and generate response
def generate_response(user_input):
    result = chain.invoke(user_input)
    return result['result']

# Chat interface
user_input = st.text_input("Ask a question:")
if user_input:
    # Display user message
    st.session_state["messages"].append({"role": "user", "content": user_input})
    # Generate and display bot response
    response = generate_response(user_input)
    st.session_state["messages"].append({"role": "bot", "content": response})

# Display chat messages
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        message(msg["content"], is_user=True)
    else:
        message(msg["content"])
