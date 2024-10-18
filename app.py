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
from langchain_core.prompts import ChatPromptTemplate
import os
import base64
from PIL import Image
 
# Custom CSS for chat-like interface
st.markdown(
    """
<style>
    body {
        font-family: 'Arial', sans-serif;
        background-color: #ffffff; /* White background */
    }
    .stApp {
        background-color: #ffffff; /* White background */
    }
</style>
""", unsafe_allow_html=True)

def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return encoded_string

logo_path = "logo.png"
image = Image.open(logo_path)
image = image.resize((300, 80))
if os.path.exists(logo_path):
    st.image(image, use_column_width=False)
else:
    st.error(f"Logo file not found at {logo_path}")
 
st.markdown("<h1 class='input-text'><b>Predictive Analyst 360</b></h1>", unsafe_allow_html=True)

    # st.markdown("""
    # <hr style="border: .01rem solid #ddd; width: 100vw; position: absolute; top: -6rem; left: -4.8rem;">
    # """, unsafe_allow_html=True)

    # st.markdown('<h1 style="text-align: center;">Cost saving recommendation</h1>', unsafe_allow_html=True)
# Load environment variables
load_dotenv()

# Set up API keys and Neo4j credentials
# GROQ_API_KEY = os.environ["GROQ_API_KEY"]
# NEO4J_URI = os.environ["NEO4J_URI"]
# NEO4J_USERNAME = os.environ["NEO4J_USERNAME"]
# NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"]
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
NEO4J_URI = st.secrets["NEO4J_URI"]
NEO4J_USERNAME = st.secrets["NEO4J_USERNAME"]
NEO4J_PASSWORD = st.secrets["NEO4J_PASSWORD"]


# Initialize Neo4j graph
graph = Neo4jGraph()
enhanced_graph = Neo4jGraph(
    url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD, enhanced_schema=True,
)

schema = enhanced_graph._enhanced_schema
# Initialize the LLM (Groq)
llm = ChatGroq(
    model="llama-3.2-90b-vision-preview",
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


prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix=""""Task: Generate a Cypher statement to query a graph database.
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
chain1 = GraphCypherQAChain.from_llm(
    graph=enhanced_graph, llm=llm, cypher_prompt=prompt, validate_cypher =True, function_response_system=Str, verbose=True, memoryview=True, allow_dangerous_requests=True, return_direct=True
)


# Streamlit App Interface
# st.title("Graph Cypher Query Assistant")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state["messages"] = []



def generate_response(user_input, schema):
    try:
        initial_result1 = chain1.invoke(user_input)
    except Exception as e:
        return f"An error occurred while processing your query: {str(e)}"

    # Analyze the query and result
    analysis_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    User input: {input}
    Initial result: {result}
    Schema: {schema}
    
    Analyze the user's query and the initial result. Determine:
    1. check if there is any error or Empty in the result that means cypher query was not generated correctly based on the User input to over come this generate simple Follow-up Query which would related to the Schema and User input.  
    2. Is the result satisfactory? Use the following levels:
       - "Yes" if the result is complete and directly answers the user's question.
       - "No" if the result is incomplete or incorrect.
    3. If the result is "Medium" or "No", identify what specific information is missing, unclear, or incorrect based on the user input and schema.
    4. Generate a follow-up query to retrieve the missing or more accurate information. The follow-up query should:
       - Be based on the schema, and identified missing information only
    
    Respond in the following format:
    Satisfactory: [Yes/No]
    Missing Information: [Detailed description of what's missing or needs clarification.]
    Follow-up Query: [Specific, targeted query to get additional information, include even if Satisfactory is "Yes" to potentially enhance the result]
    Reasoning: [Brief explanation of why this follow-up query was chosen and how it addresses the missing information or improves the result]
    """)
    ])

    analysis_chain = analysis_prompt | llm
    analysis = analysis_chain.invoke({
        "input": user_input,
        "result": initial_result1["result"],
        "schema": schema,
    })

    print(analysis)
    analysis_lines = analysis.content.split('\n')
    
    # Extract satisfaction level from the first line
    satisfaction_level = ""
    missing_info = ""
    follow_up_query = ""
    
    # Safely parse the analysis response
    for line in analysis_lines:
        line = line.strip()
        if line.startswith('Satisfactory:'):
            satisfaction_level = line.split(': ')[1].lower()
        elif line.startswith('Missing Information:'):
            missing_info = line.split(': ')[1] if ': ' in line else ""
            if missing_info.lower() == "none":
                missing_info = ""
        elif line.startswith('Follow-up Query:'):
            follow_up_query = line.split(': ')[1] if ': ' in line else ""

    if satisfaction_level == "yes":
        # Present the satisfactory result
        present_prompt = ChatPromptTemplate.from_messages([
            ("system", """
            User input: {input}
            Result: {result}
            Schema: {schema}
            based on the Result form nice and human understandable answers and Present Each and every thing present in the Result. 
            Do not add any other information that wasn't part of the Result, 
            and dont use sentences like 'Based on the provided information, I will form a human-understandable answer'\nwhere ever required alway use($,',',%,-) and tables to structured the output\nAlways interact with user,
            Always approch the user to ask the different comprehensive and logical questions based on the given schema and Result

            """)
        ])

        present_chain = present_prompt | llm
        final_result = present_chain.invoke({
            "input": user_input,
            "result": initial_result1["result"],
            "schema": schema,
        })
        # st.write(initial_result1["result"])

        return final_result.content

    # elif satisfaction_level == "medium":
    #     # Follow-up to retrieve missing information
    #     try:
    #         additional_info = chain1.invoke(follow_up_query)
    #     except Exception as e:
    #         additional_info = f"Unable to retrieve additional information: {str(e)}"
        
    #     present_prompt1 = ChatPromptTemplate.from_messages([
    #         ("system", """
    #         User input: {input}
    #         Schema: {schema}
    #         initial_result: {initial_result1},
    #         follow_up_query: {follow_up_query},
    #         follow_up_result: {additional_info},
    #         Suggest the User the Question asked is insufficent they should ask question like follow_up_query and the result of the follow_up_query is follow_up_result.
    #         Do not add any other information that wasn't part of the follow_up_result, 
    #         and dont use sentences like 'Based on the provided information, I will form a human-understandable answer'\nwhere ever required alway use($,',',%,-) and tables to structured the output\nAlways interact with user,
    #         Always approch the user to ask the different comprehensive and logical questions based on the given schema and follow_up_query
             
    #         """)
    #     ])

    #     present_chain1 = present_prompt1 | llm
    #     final_result = present_chain1.invoke({
    #         "input": user_input,
    #         "schema": schema,
    #         "initial_result1": initial_result1["result"],
    #         "follow_up_query": follow_up_query,
    #         "additional_info": additional_info,
    #     })
    #     st.write(initial_result1)

    #     return final_result.content
    
        

    elif satisfaction_level == "no":
        try:
            additional_info = chain1.invoke(follow_up_query)
        except Exception as e:
            additional_info = f"Unable to retrieve additional information: {str(e)}"
        
        present_prompt1 = ChatPromptTemplate.from_messages([
            ("system", """
            User input: {input}
            Schema: {schema}
            initial_result: {initial_result1},
            follow_up_query: {follow_up_query},
            follow_up_result: {additional_info},
            Suggest the User the Question asked is insufficent they should ask question like follow_up_query and the result of the follow_up_query is follow_up_result.
            Do not add any other information that wasn't part of the follow_up_result, 
            and dont use sentences like 'Based on the provided information, I will form a human-understandable answer'\nwhere ever required alway use($,',',%,-) and tables to structured the output\nAlways interact with user,
            Always approch the user to ask the different comprehensive and logical questions based on the given schema and follow_up_result
            
            """)
        ])

        present_chain1 = present_prompt1 | llm
        final_result = present_chain1.invoke({
            "input": user_input,
            "schema": schema,
            "initial_result1": initial_result1["result"],
            "follow_up_query": follow_up_query,
            "additional_info": additional_info,
        })
        
        return final_result.content

    else:
        return "Unexpected analysis result. Please try again."

# Initialize session state if not present
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Chat input from user
user_input = st.text_input("Ask a question:")

if user_input:
    # Add the user's message to the chat history
    st.session_state["messages"].append({"role": "user", "content": user_input})

    # Generate and display bot response
    response = generate_response(user_input, schema)

    # Check the format of the response and handle accordingly
    if isinstance(response, dict):
        # Format dictionary responses
        formatted_response = ""
        for key, value in response.items():
            formatted_response += f"**{key.capitalize()}:** {value}\n\n"
        st.session_state["messages"].append({"role": "bot", "content": formatted_response})
    elif isinstance(response, list):
        # Format list responses
        formatted_response = "\n".join(f"- {item}" for item in response)
        st.session_state["messages"].append({"role": "bot", "content": formatted_response})
    else:
        # Assume it's a plain text response
        st.session_state["messages"].append({"role": "bot", "content": response})

# Display chat messages
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        message(msg["content"], is_user=True)
    else:
        message(msg["content"])



# # Chat interface
# user_input = st.text_input("Ask a question:")
# if user_input:
#     # Display user message
#     st.session_state["messages"].append({"role": "user", "content": user_input})
#     # Generate and display bot response
#     response = generate_response(user_input, schema)
#     st.session_state["messages"].append({"role": "bot", "content": response})

# # Display chat messages
# for msg in st.session_state["messages"]:
#     if msg["role"] == "user":
#         message(msg["content"], is_user=True)
#     else:
#         message(msg["content"])
