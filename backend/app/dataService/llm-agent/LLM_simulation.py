import os
import json
import requests
import pandas as pd
from sql_metadata import Parser
from urllib.parse import quote
import time
import logging
from llm_client import initialize_llm_client

# --- 1. Configuration ---
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = "5012"
BASE_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}/api"
DB_ID = "customers_and_addresses"


from dotenv import load_dotenv
flag = load_dotenv(override=True)
if not flag:
    print("Warning: .env file not found. Please ensure it exists in the `dataService` directory or current working directory.")
    exit()

print(f"✅ Backend service URL: {BASE_URL}")

# Configure logging for LLM simulation
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('llm_simulation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.info("=== LLM Simulation Starting ===")

# Initialize the global client and model for simulation context
# Allow provider selection via environment variable or default to auto-selection
preferred_provider = os.getenv("EVAL_LLM_PROVIDER", "openai")  # e.g., "openai" or "deepseek"
client, model_name = initialize_llm_client(provider=preferred_provider)


# --- 2. System Interface Module (API Wrapper) ---
class QRecNLI_LUX_API_Wrapper:
    """
       A wrapper class to handle all API communications with the backend service(QRec-NLI).
       It encapsulates methods for fetching database schema, recommendations, and executing queries.
    """
    def __init__(self, base_url, db_id):
        """
            Initializes the API wrapper.
            Args:
                base_url (str): The base URL of the backend API service.
                db_id (str): The identifier of the database to interact with.
        """
        self.base_url = base_url
        self.db_id = db_id
        self._wait_for_backend()

    def _wait_for_backend(self, retries=5, delay=3):
        """ Waits for the backend service to become available before starting."""
        print(f"Waiting for backend service to be online at {self.base_url}...")
        test_url = f"{self.base_url}/get_tables/{self.db_id}"
        for i in range(retries):
            try:
                response = requests.get(test_url, timeout=5)
                if 200 <= response.status_code < 300:
                    print(f"✅ Backend service is ready!")
                    return True
                else:
                    print(f"🟡 Backend service returned status code {response.status_code}. Retrying in {delay} seconds...")
            except requests.exceptions.RequestException as e:
                print(f"🟡 Could not connect to backend ({e}). Retrying in {delay} seconds...")
            time.sleep(delay)
        print(f"❌ Failed to connect to backend service. Aborting.")
        exit()

    def get_available_databases(self):
        """
        Fetches the list of available databases from the spider dataset.
        
        Returns:
            list: List of available database names, or None if error
        """
        try:
            init_response = requests.get(f"{self.base_url}/initialization/spider")
            init_response.raise_for_status()
            return init_response.json()
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            print(f"Error getting available databases: {e}")
            return None

    def get_initial_state(self):
        """
            Fetches the initial state for the simulation,
            including spider dataset initialization, database schema and cold-start query recommendations.
        """
        print(f"Getting initial state for database '{self.db_id}'...")
        try:
            # Initialize spider dataset and get available databases
            print("🔧 Initializing spider dataset...")
            init_response = requests.get(f"{self.base_url}/initialization/spider")
            init_response.raise_for_status()
            db_lists = init_response.json()
            logger.info(f"Spider dataset initialized. Available databases: {len(db_lists) if isinstance(db_lists, list) else 'unknown count'}")
            print(f"✅ Spider dataset initialized with {len(db_lists) if isinstance(db_lists, list) else 'multiple'} databases")
            
            # Verify that our target database is available
            if isinstance(db_lists, list) and self.db_id not in db_lists:
                logger.warning(f"Target database '{self.db_id}' not found in available databases: {db_lists[:5]}...")
                print(f"⚠️ Warning: Database '{self.db_id}' not found in available databases")
            
            # Get database schema (this also initializes query context automatically)
            print(f"📋 Fetching schema for database '{self.db_id}'...")
            tables_response = requests.get(f"{self.base_url}/get_tables/{self.db_id}")
            tables_response.raise_for_status()
            db_schema = tables_response.json()
            db_schema = db_schema.get('tables', db_schema)
            logger.info(f"Schema fetched for {self.db_id} - query context should now be initialized")
            print(f"✅ Schema fetched (query context automatically initialized)")
            print(f"Retrieved schema: {json.dumps(db_schema, indent=2, ensure_ascii=False)}")

            # Set request headers to avoid compression issues, then get SQL recommendations
            headers = {'Accept-Encoding': None, 'User-Agent': 'curl/7.81.0'}
            print(f"🎯 Fetching initial query recommendations...")
            logger.info(f"Fetching SQL suggestions from backend: {self.base_url}/sql_sugg/{self.db_id}")
            sugg_response = requests.get(f"{self.base_url}/sql_sugg/{self.db_id}", headers=headers)
            sugg_response.raise_for_status()
            text_recommendations = sugg_response.json().get("nl", [])
            logger.info(f"Received {len(text_recommendations)} NL recommendations from backend")
            print(f"Directly fetched NL recommendations: {text_recommendations[:5]}")
            
            return {
                "schema": db_schema, 
                "recommendations": text_recommendations,
                "available_databases": db_lists
            }
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            print(f"Error getting initial state: {e}")
            return None

    def execute_query_and_get_next_state(self, query_text: str):
        """
            Sends a natural language query to the backend, gets the resulting SQL and data,
            and then fetches new interesting recommendations for the next turn.
        """
        try:
            print(f"Executing query: '{query_text}'...")
            text2sql_payload = {"user_text": query_text, "db_id": self.db_id}
            response = requests.post(f"{self.base_url}/text2sql", json=text2sql_payload)
            response.raise_for_status()
            result = response.json()
            sql_query = result.get('sql', '')
            print(f"Generated SQL: {sql_query}")
            print("Fetching new interesting recommendations...")
            headers = {'Accept-Encoding': None, 'User-Agent': 'curl/7.81.0'}
            logger.info(f"Fetching interesting SQL suggestions after query execution")
            sugg_response = requests.get(f"{self.base_url}/sql_sugg/{self.db_id}", headers=headers)
            sugg_response.raise_for_status()
            new_text_recs = sugg_response.json().get("nl", [])
            logger.info(f"Received {len(new_text_recs)} new interesting NL recommendations")
            print(f"Directly fetched new NL recommendations: {new_text_recs[:5]}")
            return {"sql": sql_query, "data": result.get('data', []), "recommendations": new_text_recs}
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            print(f"Error executing query or fetching new recommendations: {e}")
            return None


# --- 3. Result Textualization Module ---
def data_to_text(sql: str, data: list) -> str:
    """ Converts structured query results (data) into a human-readable text summary."""
    if not data: return "The query returned no results."
    if not sql: return "No valid SQL was generated, cannot parse results."
    try:
        columns = Parser(sql).columns
        if not columns: columns = [f"Column_{i + 1}" for i in range(len(data[0]))]
        df = pd.DataFrame(data, columns=columns)
    except Exception:
        df = pd.DataFrame(data)
        columns = [f"Column_{i + 1}" for i in range(len(df.columns))]
        df.columns = columns
    num_rows, num_cols = df.shape
    if num_rows == 1 and num_cols == 1:
        return f"The result is a single value: {df.iloc[0, 0]}."

    top_rows_str_list = []
    for _, row in df.head(3).iterrows():
        try:
            row_str = ", ".join([f"{col}: '{row[col]}'" for col in df.columns])
        except KeyError:
            row_str = ", ".join([f"Column_{i + 1}: '{val}'" for i, val in enumerate(row)])
        top_rows_str_list.append(f"({row_str})")
    top_rows_summary = "; ".join(top_rows_str_list)
    return f"The result is a table with {num_rows} rows. The first {min(3, num_rows)} rows are: {top_rows_summary}."


# --- 4. Agent & Prompt Logic ---
class LLMAnalystAgent:
    """
        Represents the AI agent that performs data analysis.
        It maintains its own memory and uses an LLM to make decisions at each turn.
    """
    def __init__(self, persona, goal):
        """
            Initializes the agent.

            Args:
                persona (str): A description of the agent's role and characteristics.
                goal (str): The high-level objective the agent is trying to achieve.
        """
        self.persona = persona
        self.goal = goal
        self.memory = []
        self.interaction_log = []
        self.db_schema = None

    def add_insight_to_memory(self, insight):
        """ Adds a new piece of information learned from a query result to the agent's memory."""
        if insight and insight not in self.memory:
            print(f"\n🧠 Agent Memory Update: New insight added -> '{insight}'")
            self.memory.append(insight)

    def log_turn(self, turn_data):
        """ Records the data from a single interaction turn into the agent's log."""
        self.interaction_log.append(turn_data)

    def _call_llm(self, prompt_text):
        """
            A private method to call the LLM with a given prompt.

            Args:
                prompt_text (str): The complete prompt to send to the LLM.

            Returns:
                dict or None: The parsed JSON response from the LLM, or None if an error occurs.
        """
        print("\n🤖 LLM is thinking...")
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt_text}],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error calling LLM ({model_name}) or parsing its response: {e}")
            return None

    def decide_first_query(self, db_schema, initial_recommendations):
        """ Makes the first decision of the simulation (cold start)."""
        self.db_schema = db_schema
        prompt_template = f"""
        **AI Data Analyst Context**
        **Your Role:** {self.persona}
        **Your High-Level Goal:** {self.goal}

        **Your Task: Step 1 (Cold Start)**
        You are connected to the database '{DB_ID}' for your first query. The system has provided the database schema and some general initial exploration questions.

        **1. Database Schema (Tables and Columns):**
        ---
        {json.dumps(self.db_schema, indent=2, ensure_ascii=False)}
        ---
        **2. System-Recommended Initial Exploration Questions (Natural Language):**
        ---
        {chr(10).join([f'{i + 1}. {rec}' for i, rec in enumerate(initial_recommendations[:5])]) if initial_recommendations else "None"}
        ---

        **Your Decision Task:** Based on the information above, decide on the first natural language query to start your analysis. You have three options:

        A) **Choose a Recommendation (CHOOSE_RECOMMENDATION):** If one of the recommended questions is a perfect starting point, adopt it directly.
        B) **Refine a Recommendation (REFINE_RECOMMENDATION):** If a recommended question is in the right direction but not specific enough, you can refine it. For example, by adding grouping, filtering, etc.
        C) **Formulate a New Question (FORMULATE_NEW):** If none of the recommendations are suitable, or you want to start from a completely different angle, formulate a new question based on the database schema.

        **Please provide your output strictly in the following JSON format:**
        {{
          "evaluation": "Overall assessment of the database schema and initial recommendations.",
          "decision_rationale": "Detailed explanation of why you chose A, B, or C.",
          "first_action_type": "CHOOSE_RECOMMENDATION" | "REFINE_RECOMMENDATION" | "FORMULATE_NEW",
          "first_query_text": "This is your first natural language query."
        }}
        """
        return self._call_llm(prompt_template)

    def decide_next_query(self, last_query, query_result_text, recommendations, use_recommendations=True):
        """ Makes a decision for the next step based on the previous turn's results."""
        memory_log = "\n".join([f"- {item}" for item in self.memory]) if self.memory else "No insights have been gained yet."
        recs_text = "The system did not provide any contextual recommendations."
        if use_recommendations and recommendations:
            recs_text = chr(10).join([f'{i + 1}. {rec}' for i, rec in enumerate(recommendations[:5])])

        prompt_template = f"""
        **AI Data Analyst Context**
        **Your Goal:** {self.goal}
        **Your Memory (What you have learned so far):**
        ---
        {memory_log}
        ---
        **Available Database Schema (For your reference to build queries):**
        ---
        {json.dumps(self.db_schema, indent=2, ensure_ascii=False)}
        ---
        **Your last query was:** "{last_query}"
        **The system returned the following information:**
        **Query Result:** {query_result_text} **Important Constraint:** Focus only on the thematically relevant parts of the query results; ignore irrelevant outliers.
        **Based on your last query, the system recommends the following next steps (Natural Language):** {recs_text}
        **Your Task:** Analyze the information above and decide on your next step.

        1. **Extract Insight:** What key information did you learn from the query result?
        2. **Evaluate Recommendations & Decide:**
           You have three options. Please consider them carefully before making a decision:

           A) **Choose a Recommendation (CHOOSE_RECOMMENDATION):** If one of the recommended questions perfectly aligns with your next analysis step, adopt it directly.

           B) **Refine a Recommendation (REFINE_RECOMMENDATION):** If a recommended question is generally useful, but you want to elaborate on it.
              *For example: The recommendation is "Show all customers," but you want to see "Show customers grouped by city."*
              In this case, you need to formulate a **new, more detailed** natural language query and explain why this refinement is necessary.

           C) **Formulate a New Question (FORMULATE_NEW):** If all recommendations are irrelevant to your line of thought, or you need to explore a completely different direction.
              *For example: You just analyzed the geographical distribution of customers and now want to analyze their other thematic features.*
              In this case, you need to formulate a brand new question and explain why you need to start this new exploration path.

        **Please provide your output strictly in the following JSON format:**
        {{
          "new_insight": "...",
          "recommendation_evaluation": "An evaluation of the system's recommendations, explaining if they were useful and why you made your final decision.",
          "decision_rationale": "A detailed explanation of why you chose A, B, or C.",
          "next_action_type": "CHOOSE_RECOMMENDATION" | "REFINE_RECOMMENDATION" | "FORMULATE_NEW",
          "next_query_text": "This is your next natural language query."
        }}
        """
        return self._call_llm(prompt_template)


# --- 5. Main Simulation Loop ---
def run_simulation(max_turns=6, use_recommendations=True):
    """
        The main function that orchestrates the entire simulation from start to finish.
        It initializes the agent and API wrapper, runs the cold start phase,
        and then enters the main interaction loop for a specified number of turns.
        Finally, it saves the complete interaction log.
    """
    mode_str = 'With Recommendations' if use_recommendations else 'No Recommendations'
    print("======================================================")
    print(f"      Starting LLM Data Analyst Simulation v8 (Revised)      ")
    print(f"      Target Database: {DB_ID}")
    print(f"      Mode: {mode_str}")
    print("======================================================")

    api = QRecNLI_LUX_API_Wrapper(BASE_URL, DB_ID)
    agent_persona = "You are a professional data analyst skilled in exploratory analysis with incomplete information. You can only interact with the system through natural language, including viewing recommended exploration questions."
    agent_goal = f"Analyze the '{DB_ID}' database to understand basic customer information."
    agent = LLMAnalystAgent(persona=agent_persona, goal=agent_goal)

    # --- Phase 1: Cold Start ---
    print("\n--- 🚀 Phase 1: Cold Start ---")
    initial_state = api.get_initial_state()
    if not initial_state:
        print("Failed to get initial state, aborting simulation.")
        return

    cold_start_decision = agent.decide_first_query(
        initial_state["schema"],
        initial_state["recommendations"] if use_recommendations else []
    )
    if not cold_start_decision:
        print("Cold start decision failed, aborting simulation.")
        return

    print("\n✅ Analyst's Cold Start Decision:")
    print(json.dumps(cold_start_decision, indent=2, ensure_ascii=False))
    current_query = cold_start_decision.get("first_query_text")
    agent.log_turn({"turn": 0, "type": "cold_start", "decision": cold_start_decision})

    # --- Phase 2: Interaction Loop ---
    for turn in range(1, max_turns + 1):
        print(f"\n--- 🔄 Phase 2: Interaction Turn {turn}/{max_turns} ---")
        if not current_query:
            print("Analyst did not decide on a query, ending simulation.")
            break

        print(f"🗣️ Analyst's Query: '{current_query}'")
        response_state = api.execute_query_and_get_next_state(current_query)
        if not response_state:
            print("Failed to execute query, ending simulation.")
            break

        result_text = data_to_text(response_state['sql'], response_state['data'])
        print(f"\n📄 System's textualized result:\n{result_text}")

        next_decision = agent.decide_next_query(
            last_query=current_query,
            query_result_text=result_text,
            recommendations=response_state.get('recommendations', []) if use_recommendations else [],
            use_recommendations=use_recommendations
        )
        if not next_decision:
            print("Analyst decision failed, ending simulation.")
            break

        print("\n✅ Analyst's Decision for this turn:")
        print(json.dumps(next_decision, indent=2, ensure_ascii=False))
        agent.add_insight_to_memory(next_decision.get("new_insight", "No insight generated."))
        # Use the interaction-loop-specific key name
        current_query = next_decision.get("next_query_text")
        agent.log_turn(
            {"turn": turn, "type": "interaction", "system_response": response_state, "decision": next_decision})
    else:
        print("\n--- Reached maximum number of interaction turns ---")

    # --- End ---
    print("\n\n======================================================")
    print("           🏁 Simulation Ended 🏁          ")
    print("======================================================")
    print("\n📝 Analyst Report Summary (Based on Memory):")
    if agent.memory:
        for i, insight in enumerate(agent.memory):
            print(f"{i + 1}. {insight}")
    else:
        print("No insights were formed during the simulation.")

    final_log_data = {
        "metadata": {
            "agent_persona": agent.persona,
            "agent_goal": agent.goal,
            "db_id": DB_ID,
            "simulation_mode": 'with_recs' if use_recommendations else 'no_recs',
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "interaction_log": agent.interaction_log
    }

    log_filename = f"simulation_log_{'with_lux_recs' if use_recommendations else 'no_lux_recs'}_{DB_ID}.json"
    with open(log_filename, 'w', encoding='utf-8') as f:
        json.dump(final_log_data, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Full interaction log saved to '{log_filename}'")


if __name__ == "__main__":
    # Run with recommendations mode
    run_simulation(max_turns=5, use_recommendations=True)

    # # # For comparison, you can run the no-recommendations mode
    # print("\n\n" + "=" * 80 + "\n\n")
    # run_simulation(max_turns=5, use_recommendations=False)


