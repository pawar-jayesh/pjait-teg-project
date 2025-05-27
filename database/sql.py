import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from langchain_core.runnables.config import RunnableConfig
from dbsetup import Team, Location, User, PaidLeave
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from sqlalchemy import text, inspect
from langgraph.graph import StateGraph, END

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///example.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class AgentState(TypedDict):
    question: str
    sql_query: str
    query_result: str
    query_rows: list
    current_user: str
    attempts: int
    relevance: str
    sql_error: bool

def get_database_schema(engine):
    inspector = inspect(engine)
    schema = ""
    for table_name in inspector.get_table_names():
        schema += f"Table: {table_name}\n"
        for column in inspector.get_columns(table_name):
            col_name = column["name"]
            col_type = str(column["type"])
            if column.get("primary_key"):
                col_type += ", Primary Key"
            if column.get("foreign_keys"):
                fk = list(column["foreign_keys"])[0]
                col_type += f", Foreign Key to {fk.column.table.name}.{fk.column.name}"
            schema += f"- {col_name}: {col_type}\n"
        schema += "\n"
    print("Retrieved database schema.")
    return schema

class GetCurrentUser(BaseModel):
    current_user: str = Field(
        description="The name of the current user based on the provided user email."
    )

def get_current_user(state: AgentState, config: RunnableConfig):
    print("Retrieving the current user based on user email.")
    user_email = config["configurable"].get("current_user_email", None)
    if not user_email:
        state["current_user"] = "User not found"
        print("No user ID provided in the configuration.")
        return state

    session = SessionLocal()
    try:
        user = session.query(User).filter(User.email == user_email).first()
        if user:
            state["current_user"] = user.name
            print(f"Current user set to: {state['current_user']}")
        else:
            state["current_user"] = "User not found"
            print("User not found in the database.")
    except Exception as e:
        state["current_user"] = "Error retrieving user"
        print(f"Error retrieving user: {str(e)}")
    finally:
        session.close()
    return state

class CheckRelevance(BaseModel):
    relevance: str = Field(
        description="Indicates whether the question is related to the database schema. 'relevant' or 'not_relevant'."
    )

def check_relevance(state: AgentState, config: RunnableConfig):
    question = state["question"]
    schema = get_database_schema(engine)
    print(f"Checking relevance of the question: {question}")
    system = """You are an assistant that determines whether a given question is related to the following database schema. The user is allowed to query database for deatils about comapny, collegues contact info, their info ans so on. If the user tries to insert,update or delete records mark it is 'not_revelant'

Schema:
{schema}

Respond with only "relevant" or "not_relevant".
""".format(schema=schema)
    human = f"Question: {question}"
    check_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", human),
        ]
    )
    llm = ChatOpenAI(model_name="gpt-4o-mini",
    openai_api_key=os.environ['OPENAI_API_KEY_TEG_07'],
    temperature=0
    )
    structured_llm = llm.with_structured_output(CheckRelevance)
    relevance_checker = check_prompt | structured_llm
    relevance = relevance_checker.invoke({})
    state["relevance"] = relevance.relevance
    print(f"Relevance determined: {state['relevance']}")
    return state

class ConvertToSQL(BaseModel):
    sql_query: str = Field(
        description="The SQL query corresponding to the user's natural language question."
    )

def convert_nl_to_sql(state: AgentState, config: RunnableConfig):
    question = state["question"]
    current_user = state["current_user"]
    schema = get_database_schema(engine)
    print(f"Converting question to SQL for user '{current_user}': {question}")
    system = """You are an assistant that converts natural language questions into SQL queries based on the following schema:

{schema}


Provide only the SQL query without any explanations. Alias columns appropriately to match the expected keys in the result.
For example, alias 'Location.office_name' as 'office_name', 'Location.city' as 'city', Team.name as 'team_names', COUNT(*) as 'count', user.email as 'email', 'PaidLeaves.utilized' as 'utilized' and 'PaidLeaves.total_allocated' as 'total_allocated'.
""".format(schema=schema, current_user=current_user)
    convert_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "Question: {question}"),
        ]
    )
    llm = ChatOpenAI(model_name="gpt-4o-mini",
    openai_api_key=os.environ['OPENAI_API_KEY_TEG_07'],
    temperature=0
    )
    structured_llm = llm.with_structured_output(ConvertToSQL)
    sql_generator = convert_prompt | structured_llm
    result = sql_generator.invoke({"question": question})
    state["sql_query"] = result.sql_query
    print(f"Generated SQL query: {state['sql_query']}")
    return state

def execute_sql(state: AgentState):
    sql_query = state["sql_query"].strip()
    session = SessionLocal()
    print(f"Executing SQL query: {sql_query}")
    try:
        result = session.execute(text(sql_query))
        if sql_query.lower().startswith("select"):
            rows = result.fetchall()
            columns = result.keys()
            if rows:
                header = ", ".join(columns)
                state["query_rows"] = [dict(zip(columns, row)) for row in rows]
                print(f"Raw SQL Query Result: {state['query_rows']}")
                # Format the result for readability
                # data = "; ".join([f"{row.get('food_name', row.get('name'))} for ${row.get('price', row.get('food_price'))}" for row in state["query_rows"]])


                if isinstance(state['query_rows'], list) and all(isinstance(row, dict) for row in state['query_rows']):
                    # Get all unique keys across all rows
                    keys_found = set()
                    for row in state['query_rows']:
                        keys_found.update(row.keys())

                    print("Detected keys:", keys_found)

                    if 'office_name' in keys_found:
                        office_names = [row['office_name'] for row in state['query_rows'] if row.get('office_name')]
                        # generate office message
                        office_list = ', '.join(office_names[:-1]) + ', and ' + office_names[-1] if len(office_names) > 1 else office_names[0]
                        # print("office_list",office_list)
                        formatted_result = f"{header}\n{office_list}"
                    
                    elif 'team_names' in keys_found:
                        team_names = [row['team_names'] for row in state['query_rows'] if row.get('team_names')]
                        # generate office message
                        team_names_list = ', '.join(team_names[:-1]) + ', and ' + team_names[-1] if len(team_names) > 1 else cities[0]
                        print("office_list",team_names_list)
                        formatted_result = f"{header}\n{team_names_list}"

                    elif 'members' in keys_found:
                        members = [row['members'] for row in state['query_rows'] if row.get('members')]
                        # generate office message
                        members_list = ', '.join(members[:-1]) + ', and ' + members[-1] if len(members) > 1 else cities[0]
                        print("office_list",members_list)
                        formatted_result = f"{header}\n{members_list}"

                    elif 'city' in keys_found:
                        cities = [row['city'] for row in state['query_rows'] if row.get('city')]
                        # generate office message
                        cities_list = ', '.join(cities[:-1]) + ', and ' + cities[-1] if len(cities) > 1 else cities[0]
                        print("office_list",cities_list)
                        formatted_result = f"{header}\n{cities_list}"

                    elif 'email' in keys_found:
                        emails = [row['email'] for row in state['query_rows'] if row.get('email')]
                        # generate email message
                        if emails:
                            if len(emails) > 1:
                                email_list = ', '.join(emails[:-1]) + ', and ' + emails[-1]
                            else:
                                email_list = emails[0]

                            formatted_result = f"{header}\n{email_list}"
                            
                    elif any(key.lower() in ['leaves_left', 'remaining_leaves'] for key in keys_found):
                        # Get the first matching count key
                        leaves = next((key for key in keys_found if key.lower() in ['leaves_left', 'remaining_leaves']), None)
                        
                        if leaves:
                            leaves = state['query_rows'][0].get(leaves)
                            formatted_result = f"{header}\n{leaves}"
                        
                        print("leaves-->", leaves)
                    
                    elif 'total_allocated' in keys_found:
                        total_allocated = state['query_rows'][0].get(total_allocated)
                        formatted_result = f"{header}\n{total_allocated}"
                        print("formatted_result,,,,,,,",formatted_result)
                    
                    elif any(key.lower() in ['total_utilized_leaves', 'utilized'] for key in keys_found):
                        utilized_leaves = next((key for key in keys_found if key.lower() in ['total_utilized_leaves', 'utilized']), None)
                        
                        if utilized_leaves:
                            utilized_leaves = state['query_rows'][0].get(utilized_leaves)
                            formatted_result = f"{header}\n{utilized_leaves}"
                        
                        print("utilized_leaves-->", utilized_leaves)

                    
                    elif any(key.lower() in ['count(*)', 'count', 'total', 'user_count'] for key in keys_found):
                        # Get the first matching count key
                        count_key = next((key for key in keys_found if key.lower() in ['count(*)', 'count', 'total', 'user_count']), None)
                        if count_key:
                            count_value = state['query_rows'][0].get(count_key)
                            formatted_result = f"{header}\n{count_value}"

                    else:
                        formatted_result = f"{header}"

                else:
                    formatted_result = f"{header}"

            else:
                state["query_rows"] = []
                formatted_result = "No results found."
            state["query_result"] = formatted_result
            state["sql_error"] = False
            print("SQL SELECT query executed successfully.")
        else:
            state["query_result"] = f"Error executing SQL query: {str(e)}"
            state["sql_error"] = True
            print(f"Error executing SQL query: {str(e)}")
    except Exception as e:
        state["query_result"] = f"Error executing SQL query: {str(e)}"
        state["sql_error"] = True
        print(f"Error executing SQL query: {str(e)}")
    finally:
        session.close()
    return state


def generate_human_readable_answer(state: AgentState):
    sql = state["sql_query"]
    result = state["query_result"]
    current_user = state["current_user"]
    query_rows = state.get("query_rows", [])
    sql_error = state.get("sql_error", False)
    print("Generating a human-readable answer.")
    system = """You are an assistant that converts SQL query results into clear, natural language responses, if there are multiple results from the you list them all in human readable format. Start the response with a friendly greeting that includes the user's name.
    """
    if sql_error:
        # Directly relay the error message
        generate_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                (
                    "human",
                    f"""SQL Query:
{sql}

Result:
{result}

Formulate a clear and understandable error message in a single sentence, starting with 'Hello {current_user},' informing them about the issue."""
                ),
            ]
        )
    elif sql.lower().startswith("select"):
        if not query_rows:
            # Handle cases with no orders
            generate_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system),
                    (
                        "human",
                        f"""SQL Query:
{sql}

Result:
{result}

Formulate a clear and understandable answer to the original question in a single sentence, starting with 'Hello {current_user},' and mention that there are no records found."""
                    ),
                ]
            )
        else:
            # Handle displaying 
            generate_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system),
                    (
                        "human",
                        f"""SQL Query:
{sql}

Result:
{result}

Formulate a clear and understandable answer to the original question in a single sentence, starting with 'Hello {current_user},' and the output in human readable format, the data query might contain list or single values or count of rows, you can format it properly. For example: 'Hello Bob, we have the following details about you present in our database.', 'Hello Alice we currently have offices at these locations eg: Warsaw, etc.', 'Hello Alan, there are the emails of all the HRs with their departments', 'Hello Betty, There are 3 person working in IT department' """
                    ),
                ]
            )
    

    llm = ChatOpenAI(model_name="gpt-4o-mini",
    openai_api_key=os.environ['OPENAI_API_KEY_TEG_07'],
    temperature=0
    )
    human_response = generate_prompt | llm | StrOutputParser()
    answer = human_response.invoke({})
    state["query_result"] = answer
    print("Generated human-readable answer.")
    return state

class RewrittenQuestion(BaseModel):
    question: str = Field(description="The rewritten question.")

def regenerate_query(state: AgentState):
    question = state["question"]
    print("Regenerating the SQL query by rewriting the question.")
    system = """You are an assistant that reformulates an original question to enable more precise SQL queries. Ensure that all necessary details, such as table joins, are preserved to retrieve complete and accurate data.
    """
    rewrite_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            (
                "human",
                f"Original Question: {question}\nReformulate the question to enable more precise SQL queries, ensuring all necessary details are preserved.",
            ),
        ]
    )
    llm = ChatOpenAI(model_name="gpt-4o-mini",
    openai_api_key=os.environ['OPENAI_API_KEY_TEG_07'],
    temperature=0
    )
    structured_llm = llm.with_structured_output(RewrittenQuestion)
    rewriter = rewrite_prompt | structured_llm
    rewritten = rewriter.invoke({})
    state["question"] = rewritten.question
    state["attempts"] += 1
    print(f"Rewritten question: {state['question']}")
    return state

def generate_funny_response(state: AgentState):
    print("Generating a funny response for an unrelated question.")
    system = """You are a charming and funny assistant who responds in a playful manner.
    """
    human_message = "I can not help with that.I only can fecth data from the database, cannot modify data."
    funny_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", human_message),
        ]
    )
    llm = ChatOpenAI(model_name="gpt-4o-mini",
    openai_api_key=os.environ['OPENAI_API_KEY_TEG_07'],
    temperature=0
    )
    funny_response = funny_prompt | llm | StrOutputParser()
    message = funny_response.invoke({})
    state["query_result"] = message
    print("Generated funny response.")
    return state

def end_max_iterations(state: AgentState):
    state["query_result"] = "Please try again."
    print("Maximum attempts reached. Ending the workflow.")
    return state

def relevance_router(state: AgentState):
    if state["relevance"].lower() == "relevant":
        return "convert_to_sql"
    else:
        return "generate_funny_response"

def check_attempts_router(state: AgentState):
    if state["attempts"] < 3:
        return "convert_to_sql"
    else:
        return "end_max_iterations"

def execute_sql_router(state: AgentState):
    if not state.get("sql_error", False):
        return "generate_human_readable_answer"
    else:
        return "regenerate_query"

workflow = StateGraph(AgentState)

workflow.add_node("get_current_user", get_current_user)
workflow.add_node("check_relevance", check_relevance)
workflow.add_node("convert_to_sql", convert_nl_to_sql)
workflow.add_node("execute_sql", execute_sql)
workflow.add_node("generate_human_readable_answer", generate_human_readable_answer)
workflow.add_node("regenerate_query", regenerate_query)
workflow.add_node("generate_funny_response", generate_funny_response)
workflow.add_node("end_max_iterations", end_max_iterations)

workflow.add_edge("get_current_user", "check_relevance")

workflow.add_conditional_edges(
    "check_relevance",
    relevance_router,
    {
        "convert_to_sql": "convert_to_sql",
        "generate_funny_response": "generate_funny_response",
    },
)

workflow.add_edge("convert_to_sql", "execute_sql")

workflow.add_conditional_edges(
    "execute_sql",
    execute_sql_router,
    {
        "generate_human_readable_answer": "generate_human_readable_answer",
        "regenerate_query": "regenerate_query",
    },
)

workflow.add_conditional_edges(
    "regenerate_query",
    check_attempts_router,
    {
        "convert_to_sql": "convert_to_sql",
        "max_iterations": "end_max_iterations",
    },
)

workflow.add_edge("generate_human_readable_answer", END)
workflow.add_edge("generate_funny_response", END)
workflow.add_edge("end_max_iterations", END)

workflow.set_entry_point("get_current_user")

app = workflow.compile()

# fake_config = {"configurable": {"current_user_email": "chang@example.com"}}

# user_question_1 = "Give me list of all office locations in poland"
# result_1 = app.invoke({"question": user_question_1, "attempts": 0}, config=fake_config)
# print("Result:", result_1["query_result"])

def askDbQuestion(email, user_question) -> str:
    config = {"configurable": {"current_user_email": email}}
    response = app.invoke({"question": user_question, "attempts": 0}, config=config)
    return response["query_result"]


def checkEmail(email) -> bool:
    user_email = email.lower()
    if not user_email:
        return False

    session = SessionLocal()
    try:
        user = session.query(User).filter(User.email == user_email).first()
        if user:
            return True
        else:
            return False

    except Exception as e:
        return False
    finally:
        session.close()

# print(checkEmail("chaNg@example.com"))
# print(askDbQuestion("chang@example.com", "How many paid leaves do I have left? my id is 10"))