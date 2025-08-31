import os
import json
from llm_client import initialize_llm_client


from dotenv import load_dotenv
flag = load_dotenv(override=True)
if not flag:
    print("Warning: .env file not found. Please ensure it exists in the `dataService` directory or current working directory.")
    exit()

# Initialize LLM client (supports multiple providers)
# Allow provider selection via environment variable or default to auto-selection
preferred_provider = os.getenv("EVAL_LLM_PROVIDER", "openai")  # e.g., "openai" or "deepseek"
client, model_name = initialize_llm_client(provider=preferred_provider)

# --- Questionnaire Definition ---
QUESTIONNAIRE = {
    # Part 1: Quality of the Recommendations Themselves
    "Q1": "The system generates topically relevant suggestions for the user's domain of interest.",
    "Q2": "The system provides context-aware suggestions for the user's next exploration step.",
    "Q3": "The user can easily understand the natural language query suggestions recommended by the system.",

    # Part 2: Impact of Recommendations on the User and Insights
    "Q4": "The system effectively helps the user decide on the next exploration action.",
    "Q5": "The system helps the user discover interesting and valuable data insights, not just repetitive or obvious information.",
    "Q6": "Through its recommendations, the system helps the user discover previously unknown data attributes or analytical dimensions.",

    # Part 3: Impact of Recommendations on the Overall Analysis Process
    "Q7": "Guided by the system, the user's exploration path is logically coherent, strategically efficient, and successfully achieves its core analytical goals."
}


# --- Core Evaluation Function ---
def generate_evaluation_prompt(interaction_log: list, agent_persona: str, agent_goal: str, simulation_mode: str) -> str:
    """
    Constructs a detailed prompt for the LLM to evaluate the simulation log.

    Args:
        interaction_log (list): A list of dictionaries, where each dictionary represents a turn in the simulation.
        agent_persona (str): A description of the AI agent's role and behavior.
        agent_goal (str): The high-level objective of the AI agent during the simulation.
        simulation_mode (str): The simulation mode (e.g., "with_recs" or "no_recs") to adjust evaluation instructions.

    Returns:
        str: A fully formatted prompt string ready to be sent to the LLM.
    """
    log_summary = ""
    for turn in interaction_log:
        turn_num = turn.get('turn')
        decision = turn.get('decision', {})
        system_response = turn.get('system_response', {})

        if turn_num == 0:
            action_type = decision.get('first_action_type')
            query = decision.get('first_query_text')
            rationale = decision.get('decision_rationale', 'N/A')
            new_insight = system_response.get('data_summary', 'N/A')
        else:
            action_type = decision.get('next_action_type')
            query = decision.get('next_query_text')
            rationale = decision.get('decision_rationale', 'N/A')
            new_insight = decision.get('new_insight', 'N/A')

        log_summary += f"--- Turn {turn_num} ---\n"
        if turn_num > 0 and new_insight and new_insight != 'N/A':
            log_summary += f"Insight from the previous turn: {new_insight}\n"

        recommendations = system_response.get('recommendations', [])
        if recommendations:
            log_summary += "System Recommendations:\n"
            for i, rec in enumerate(recommendations, 1):
                log_summary += f"  - R{i}: {rec}\n"

        log_summary += f"Action Type this turn: {action_type}\n"
        log_summary += f"Query chosen this turn: {query}\n"
        log_summary += f"Rationale: {rationale}\n\n"

    prompt_template = f"""
    **Your Role:** You are an expert Human-Computer Interaction (HCI) researcher. Your task is to evaluate the performance of a "Query Recommendation System" in a user study session and fill out a standard user experience questionnaire. Please remain fair and impartial.

    **Query Recommendation System Background:**
    The system is designed to help users, especially those unfamiliar with the database schema and domain knowledge, perform systematic data exploration by providing step-wise query recommendations. 
    This query recommendation system is built upon Lux. Lux is a Python library that intelligently recommends visualizations and data exploration paths, helping users understand the characteristics and relationships within a dataset.
    
    Its core value lies in guiding users to discover meaningful analytical paths and data insights. You will be provided with the complete interaction log of an AI agent (playing the role of a "user") with this system.
    
    **Study Session Information:**
    An AI agent acts as a "user" to perform an exploratory data analysis task. The agent's characteristics and its complete interaction log with the system are provided below.
    * **AI User Persona:** {agent_persona}
    * **AI User Goal:** {agent_goal}
    * **Simulation Mode:** {simulation_mode}

    **Action Type Definitions:**
    To help you understand the exploration path, here are the definitions for the "action_type" values:
    * **CHOOSE_RECOMMENDATION:** The agent directly selects one of the system's recommendations as its next query.
    * **REFINE_RECOMMENDATION:** The agent modifies or elaborates on one of the system's recommendations to create its next query.
    * **FORMULATE_NEW:** The agent ignores the system's recommendations entirely and formulates a new query from scratch.

    **Complete Interaction Log:**
    ==============================
    {log_summary}
    ==============================

    **Your Task:**
    Based *only* on the provided interaction log, please fill out the following questionnaire. For each question (statement), you must provide a score from 1 (Strongly Disagree) to 5 (Strongly Agree), along with a detailed, evidence-based rationale. Your rationale *must* cite specific events or patterns from the interaction log.

    **Questionnaire:**
    {json.dumps(QUESTIONNAIRE, indent=2)}

    **Rating Scale:**
    * **5 (Strongly Agree):** The evidence strongly and consistently supports the statement.
    * **4 (Agree):** The evidence generally supports the statement.
    * **3 (Neutral):** The evidence is mixed, unclear, or insufficient.
    * **2 (Disagree):** The evidence generally contradicts the statement.
    * **1 (Strongly Disagree):** The evidence strongly and consistently contradicts the statement.

    **Special Instructions:**
    1.  **For Question Q5**: If your score is **4 or higher**, you *must* also provide a `discovered_insights` field. This field should be a list of strings, where each string is a specific, interesting insight that was discovered. For example: ["Discovered that most high-value orders are concentrated on weekends", "Identified that a specific product's sales have an anomalous peak in a particular season"].

    2.  **For Question Q7**: You *must* include an `exploration_path` field. This field should be a list of strings, where each string is a concise summary of a key step or sub-topic in the user's analytical journey.
        Furthermore, if your rating for Q7 is **below 4 (Agree)**, please answer the following in a separate `incoherence_reason` field: What specific events or turns in the interaction log caused the exploration path to be less logical or coherent? What was the cause (e.g., sudden change of focus, lack of follow-up, etc.)?

    **Please provide your final evaluation in the following JSON format strictly. Ensure you include all questions from Q1 to Q7 and add the special fields according to the instructions above.**
    {{
      "Q1": {{ "score": <1-5>, "rationale": "..." }},
      "Q2": {{ "score": <1-5>, "rationale": "..." }},
      "Q3": {{ "score": <1-5>, "rationale": "..." }},
      "Q4": {{ "score": <1-5>, "rationale": "..." }},
      "Q5": {{ "score": <1-5>, "rationale": "...", "discovered_insights": ["...", "..."] }},
      "Q6": {{ "score": <1-5>, "rationale": "..." }},
      "Q7": {{ "score": <1-5>, "rationale": "...", "exploration_path": ["...", "..."], "incoherence_reason": "..." }}
    }}
    """
    return prompt_template


def evaluate_log_file(log_filename: str):
    """
    The main function to read a log file with metadata and call the LLM for evaluation.
    """
    print(f"--- Evaluating log file: {log_filename} ---")
    try:
        with open(log_filename, 'r', encoding='utf-8') as f:
            log_data = json.load(f)

        metadata = log_data.get("metadata", {})
        interaction_log = log_data.get("interaction_log", [])

        if not metadata or not interaction_log:
            raise ValueError("Log file is improperly formatted or missing 'metadata'/'interaction_log' keys.")

        agent_persona = metadata.get("agent_persona", "Unknown Persona")
        agent_goal = metadata.get("agent_goal", "Unknown Goal")
        simulation_mode = metadata.get("simulation_mode", "unknown")

    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        print(f"Could not read or parse the log file: {e}")
        return

    prompt = generate_evaluation_prompt(interaction_log, agent_persona, agent_goal, simulation_mode)

    print("\n🤖 AI Evaluator is analyzing the log and filling out the questionnaire...")
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        evaluation_result = json.loads(response.choices[0].message.content)

        if "Q1" not in evaluation_result or "score" not in evaluation_result["Q1"]:
            raise ValueError("The JSON format returned by the LLM is incorrect.")

    except Exception as e:
        print(f"An error occurred while calling the LLM ({model_name}) or parsing the evaluation: {e}")
        return

    output_filename = log_filename.replace('.json', '_EVALUATION.json')
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(evaluation_result, f, indent=4)

    print("\n--- ✅ Evaluation Complete ---")
    print(f"Evaluation results have been saved to: {output_filename}")
    print("\n--- Evaluation Summary ---")
    total_score, num_questions = 0, 0
    discovered_insights, exploration_path, incoherence_reason = None, None, None

    for q_id, result in evaluation_result.items():
        if isinstance(result, dict) and 'score' in result:
            score = result['score']
            print(f"{q_id} ({QUESTIONNAIRE.get(q_id, '')[:40]}...): {score}/5")
            total_score += score
            num_questions += 1
            if q_id == "Q5":
                discovered_insights = result.get("discovered_insights")
            elif q_id == "Q7":
                exploration_path = result.get("exploration_path")
                incoherence_reason = result.get("incoherence_reason")

    if discovered_insights:
        print("\n--- Discovered Insights (Q5) ---")
        for i, insight in enumerate(discovered_insights, 1):
            print(f"  - {insight}")
        print("--------------------------------")

    if exploration_path:
        print("\n--- Exploration Path Analysis (Q7) ---")
        for i, step in enumerate(exploration_path, 1):
            print(f"  {i}. {step}")
        print("------------------------------------")

    if incoherence_reason:
        print("\n--- Reason for Incoherence (Q7) ---")
        print(incoherence_reason)
        print("-----------------------------------")

    if num_questions > 0:
        avg_score = total_score / num_questions
        print(f"\nAverage Score: {avg_score:.2f} / 5.00")
    print("--------------------------")


if __name__ == "__main__":
    log_file_to_evaluate = "simulation_log_with_lux_recs_customers_and_addresses.json"

    if os.path.exists(log_file_to_evaluate):
        evaluate_log_file(log_file_to_evaluate)
    else:
        print(
            f"Error: Log file '{log_file_to_evaluate}' not found. Please run the simulation script first to generate the log.")
