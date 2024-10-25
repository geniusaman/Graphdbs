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
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda
from langchain.schema.output_parser import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_cohere import ChatCohere
import os
import base64
from PIL import Image
from langchain_anthropic import ChatAnthropic
 


st.set_page_config(layout="wide")

# Custom CSS for chat-like interface
st.markdown(
    """
<style>
    body {
        font-family: 'Arial', sans-serif;
        background-color: #ffffff;
    }
    .stApp {
        background-color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# Logo setup
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return encoded_string

logo_path = "logo.png"
if os.path.exists(logo_path):
    image = Image.open(logo_path)
    image = image.resize((300, 80))
    st.image(image, use_column_width=False)
else:
    st.error(f"Logo file not found at {logo_path}")

st.markdown("<h1 class='input-text'><b>Predictive Analyst 360</b></h1>", unsafe_allow_html=True)

# Load environment variables
load_dotenv()

# Set up API keys and Neo4j credentials
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
NEO4J_URI = os.environ["NEO4J_URI"]
NEO4J_USERNAME = os.environ["NEO4J_USERNAME"]
NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"]
COHERE_API_KEY = os.environ["COHERE_API_KEY"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# Initialize Neo4j graph
enhanced_graph = Neo4jGraph(
    url=NEO4J_URI, 
    username=NEO4J_USERNAME, 
    password=NEO4J_PASSWORD, 
    enhanced_schema=True,
)

schema = enhanced_graph.schema

# Initialize LLM
groq_llm = ChatGroq(
    model="llama-3.1-8b-instant",
)
# co = cohere.Client('Cohere-Api-Key')
open_llm = ChatOpenAI(model="gpt-3.5-turbo")
 
llm_cohere = ChatCohere(model="command-r-plus")
llm_sonnete = ChatAnthropic(
    model="claude-3-5-sonnet-20240620",
    temperature=0,
    max_tokens=1024,
    timeout=None,
    max_retries=2,
    # other params...
)


# Set up example selector
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
            If the generated Cypher query contains a date, convert it to date format instead of directly matching with a string. Example: (d.date >= date("2023-01-01") AND d.date <= date("2023-12-31")).
            Before making any Cypher query, please check the schema to match the cases of the nodes and relationships strictly.
            Double check the Cypher query before executing it. It should be syntactically correct.
            Below are a number of examples of questions and their corresponding Cypher queries:""",
    suffix="User input: {question}\nCypher query: ",
    input_variables=["question", "schema"],
)

Str = "You are an assistant that helps to form nice and human \nunderstandable answers based on the provided information from tools.\nDo not add any other information that wasn't present in the tools, and use \nvery concise style in interpreting results!\n"

# Initialize the chain
chain1 = GraphCypherQAChain.from_llm(
    graph=enhanced_graph,
    llm=groq_llm,
    cypher_prompt=prompt,
    validate_cypher=True,
    function_response_system=Str,
    verbose=True,
    memoryview=True,
    allow_dangerous_requests=True,
    return_direct=True
)

# Initialize session states
if "messages" not in st.session_state:
    st.session_state.messages = []

if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

# Function to get memory
def get_memory():
    if "memory" not in st.session_state:
        st.session_state.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
    return st.session_state.memory

def generate_response(user_input, schema):
    memory = get_memory()

    validation_prompt = ChatPromptTemplate.from_template("""
    Previous conversation:
    {chat_history}
    
    User Question: {question}
    Schema: {schema}
    
    Determine if the user question is related to given Schema while considering the conversation history.
    If the question is related (either directly or through context), return "Valid" and provide a reformed complete question.
    If not related, return "Invalid" and provide alternative corrected questions.

    For Valid questions that reference previous context:
    - if User Question can easily be answerd through Previous conversation or the User Question is present in Previous conversation than return "dependent Previous conversation: yes" else "No"
    - Create a reformed question that includes all necessary context and consider the latest context of the conversation history.
    - Make it self-contained and complete for database querying

    Example:
    Chat history: "what is the total spend of HP Elite 800 G6 in second quarter 2024?"
    Current question: "Is there a specific catalog id for this product"
    Reformed: "Is there a specific catalog id for HP Elite 800 G6 product?"

    ###Respond in this format:
    Validity: [Valid/Invalid]
    dependent Previous conversation: [yes/no]
    Reformed Question: [If Valid, provide complete self-contained question. If Invalid, leave empty]
    Corrected Questions: [If Invalid, list 3 corrected questions separated by commas. If Valid, leave empty]
    """)

    validation_chain = (
        {
            "question": RunnablePassthrough(), 
            "schema": RunnablePassthrough(), 
            "chat_history": RunnableLambda(lambda _: memory.chat_memory.messages)
        }
        | validation_prompt
        | llm_cohere
        | StrOutputParser()
    )

    
    validation_response = validation_chain.invoke({"question": user_input, "schema": schema})
    print(validation_response)
    validity = ""
    reformed_question = ""
    corrected_questions = ""
    dependent_Previous_conversation = ""
    
    validation_lines = validation_response.split('\n')
    
    for line in validation_lines:
        line = line.strip()
        if line.startswith('Validity:'):
            validity = line.split(': ')[1].lower()
        elif line.startswith('dependent Previous conversation:'):
            dependent_Previous_conversation = line.split(': ')[1].lower()
        elif line.startswith('Reformed Question:'):
            reformed_question = line.split(': ')[1] if ': ' in line else ""
        elif line.startswith('Corrected Questions:'):
            corrected_questions = line.split(': ')[1] if ': ' in line else ""

    if validity == "valid":
        # Save to memory
        # st.session_state.memory.save_context(
        #     {"input": user_input},
        #     {"output": reformed_question if reformed_question else user_input}
        # )
        # st.write("memory")
        # st.write(memory.chat_memory.messages)
        # st.write("reformed question")
        # st.write(reformed_question)
        query_input = reformed_question if reformed_question else user_input
        
        try:
            # initial_result = None
            # if dependent_Previous_conversation == "no":
            initial_result = chain1.invoke(query_input)

            # analysis_prompt = ChatPromptTemplate.from_template("""
            # Previous conversation:
            # {chat_history} 
                                                                                                                
            # User input: {question}
            # Initial result: {initial_result}
            # Schema: {schema}
                                                            
            
            # Analyze the user's query and the initial result. Determine:
            # 1. Check if there is any error that means cypher query was not generated correctly based on the User input to overcome this generate simple Follow-up Query which would related to the Schema and Previous conversation.  \
            # 2. check if Initial result is None that means the User input can be answerd through Previous conversation in this case it would be satisfied.
            # 3. Is the result satisfactory? Use the following levels:
            # - "Yes" if the Initial result is complete and directly answers the user's question or the Initial result is completely None.
            # - "No" if the Initial result is incomplete or incorrect.
            # 4. If "No", identify what specific information is missing, unclear, or incorrect based on the user input, schema and Previous conversation.
            # 5. Generate a follow-up query to retrieve the missing or more accurate information.
            
            # Respond in the following format:
            # Satisfactory: [Yes/No]
            # Missing Information: [Detailed description of what's missing or needs clarification]
            # Follow-up Query: [Specific query to get additional information]
            # Reasoning: [Brief explanation of the follow-up query choice]
            # """)

            # analysis_chain = (
            #     {
            #         "question": RunnablePassthrough(), 
            #         "initial_result": RunnablePassthrough(), 
            #         "schema": RunnablePassthrough(), 
            #         "chat_history": RunnableLambda(lambda _: memory.chat_memory.messages)
            #     }
            #     | analysis_prompt
            #     | llm_cohere
            #     | StrOutputParser()
            # )
            
            # analysis = analysis_chain.invoke({
            #     "question": user_input,
            #     "initial_result": initial_result["result"] if initial_result else "",
            #     "schema": schema,
            # })
            
            # print(analysis)
            # satisfaction_level = ""
            # missing_info = ""
            # follow_up_query = ""
            
            # analysis_lines = analysis.split('\n')
            # for line in analysis_lines:
            #     line = line.strip()
            #     if line.startswith('Satisfactory:'):
            #         satisfaction_level = line.split(': ')[1].lower()
            #     elif line.startswith('Missing Information:'):
            #         missing_info = line.split(': ')[1] if ': ' in line else ""
            #     elif line.startswith('Follow-up Query:'):
            #         follow_up_query = line.split(': ')[1] if ': ' in line else ""

            # if satisfaction_level:
            present_prompt = ChatPromptTemplate.from_template("""
            ##Previous conversation:
            {chat_history} 
                                                                
            ##User input: {question}
            ##Result: {result}
            ##Schema: {schema}
            
            ###Form a clear, human-understandable answer that:
            - Give the Answer of the User input based on the Result. Include Each and Every Information From Result. Do not Include Previous conversation in your response.
            - Uses appropriate formatting ($,',',%,-) and tables
            - Dont Include Schema Information in your response
            """)

            present_chain = (
                {
                    "question": RunnablePassthrough(), 
                    "result": RunnablePassthrough(), 
                    "schema": RunnablePassthrough(), 
                    "chat_history": RunnableLambda(lambda _: memory.chat_memory.messages)
                }
                | present_prompt
                | llm_cohere
                | StrOutputParser()
            )
            
            final_result = present_chain.invoke({
                "question": user_input,
                "result": initial_result["result"] if initial_result else "",
                "schema": schema,
            })
            
            # Save the final result to memory
            memory.save_context(
                {"input": user_input},
                {"output": final_result}
            )
            
            return final_result

            # elif satisfaction_level == "no" and follow_up_query:
            #     additional_info = chain1.invoke(follow_up_query)

                
            #     present_prompt = ChatPromptTemplate.from_template("""
            #     Previous conversation:
            #     {chat_history} 
                                                                    
            #     User input: {question}
            #     Initial result: {initial_result}
            #     Additional information: {additional_info}
            #     Schema: {schema}
                
            #     Form a comprehensive answer that:
            #     - Presents only information from the Result and Additional information that is the current answer of the User input. Dont Include Previous conversation in your response
            #     - Uses appropriate formatting ($,',',%,-) and tables
            #     - Dont Include Schema Information in your response
            #     """)

            #     present_chain = (
            #         {
            #             "question": RunnablePassthrough(), 
            #             "initial_result": RunnablePassthrough(), 
            #             "additional_info": RunnablePassthrough(), 
            #             "schema": RunnablePassthrough(), 
            #             "chat_history": RunnableLambda(lambda _: memory.chat_memory.messages)
            #         }
            #         | present_prompt
            #         | llm_cohere
            #         | StrOutputParser()
            #     )
                
            #     final_result = present_chain.invoke({
            #         "question": user_input,
            #         "initial_result": initial_result["result"] if initial_result else "",
            #         "additional_info": additional_info["result"],
            #         "schema": schema,
            #     })
                
            #     # Save the final result to memory
            #     memory.save_context(
            #         {"input": user_input},
            #         {"output": final_result}
            #     )
                
            #     return final_result
            
            # else:
            #     return "Unable to generate a satisfactory response. Please try rephrasing your question."
        except Exception as e:
            return f"An error occurred while processing your query: {str(e)}"
    else:
        return f"Sorry, the question seems insufficient. Here's what you can ask: {corrected_questions}"
        
    

def clear_conversation_history():
    """Clear the conversation history"""
    if "memory" in st.session_state:
        st.session_state.memory.clear()
    st.session_state.messages = []

# Add clear button
if st.button("Clear Conversation"):
    clear_conversation_history()

# Chat input
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

# Display chat messages in reverse order (latest first)
messages = reversed(st.session_state["messages"])
# Group messages into pairs
message_pairs = list(zip(messages, messages))

# Display each pair (user message followed by bot response)
for bot_msg, user_msg in message_pairs:
    message(user_msg["content"], is_user=True)
    message(bot_msg["content"])
