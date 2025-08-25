import os
import pathlib
from coverage_metrics_llm import CoverageEvaluator
from cohesion_metrics_llm import CohesionEvaluator


def evaluate_user_session(json_filepath: str, schema_folder_name: str, schema_base_dir: str) -> dict:
    """
    Calculates and saves objective evaluation metrics based on a given JSON user session
    log and database schema.

    ---Input:
        json_filepath (str): Path to the user session JSON log.
        schema_folder_name (str): Name of the directory containing the schema.
        schema_base_dir (str): Base directory for the schema folder.

    ---Output: all_metrics (dict): A dictionary of computed metrics.
        Example:
            {
                'Table Coverage': 0.75,
                'Column Coverage': 0.66,
                'Edit Index': 0.55,
                ...
            }
    """
    all_metrics = {}
    schema_filepath = os.path.join(schema_base_dir, schema_folder_name, "schema.sql")

    RESULTS_DIR = "results"
    os.makedirs(RESULTS_DIR, exist_ok=True)
    json_filename_stem = pathlib.Path(json_filepath).stem
    output_txt_filepath = os.path.join(RESULTS_DIR, f"{json_filename_stem}.txt")

    print(f"\n--- Starting evaluation: '{json_filepath}' | Schema: '{schema_filepath}' ---")

    # Calculate coverage metrics
    coverage_evaluator = CoverageEvaluator(json_filepath, schema_filepath)
    all_metrics.update(coverage_evaluator.evaluate())

    # Calculate session cohesion metrics
    cohesion_evaluator = CohesionEvaluator(json_filepath)
    all_metrics.update(cohesion_evaluator.evaluate())

    try:
        with open(output_txt_filepath, 'w', encoding='utf-8') as f:
            if not all_metrics:
                f.write("No evaluation results were generated.\n")
                print(f"\nWarning: No evaluation results generated. File '{output_txt_filepath}' was created but is empty.")
                return all_metrics

            f.write("=" * 60 + "\n")
            f.write(" " * 10 + "Comprehensive Objective Metrics Evaluation Results\n")
            f.write("=" * 60 + "\n\n")

            f.write("--- Coverage Metrics ---\n")
            coverage_keys = ["Table Coverage", "Column Coverage",
                             "Aggregation Coverage", "Clause Coverage"]
            for key in coverage_keys:
                if key in all_metrics: f.write(f"{key:<35}: {all_metrics.get(key, 0):.4f}\n")

            f.write("\n--- Session Cohesion Metrics ---\n")
            cohesion_keys = ["Edit Index", "Jaccard Index", "Cosine Index",
                             "Common Fragments Index", "Common Tables Index"]
            for key in cohesion_keys:
                if key in all_metrics: f.write(f"{key:<35}: {all_metrics.get(key, 0):.4f}\n")

            f.write("=" * 60 + "\n")
            print(f"\nEvaluation results successfully saved to: {output_txt_filepath}")

    except Exception as e:
        print(f"\nError saving results to file '{output_txt_filepath}': {e}")

    return all_metrics


if __name__ == "__main__":
    USER_JSON_DIR = "./test_data"
    # This needs to be configured to specify the database for analysis.
    DEFAULT_SCHEMA_FOLDER = "customers_and_addresses"
    SCHEMA_BASE_DIR = "../../data/dataset/spider/database"
    if not os.path.isdir(USER_JSON_DIR):
        print(f"Error: User JSON file directory '{USER_JSON_DIR}' does not exist. Please check the path.")
    else:
        # Extract all historical JSON files from user records for sequential evaluation
        json_files = [f for f in os.listdir(USER_JSON_DIR) if f.endswith('.json')]
        if not json_files:
            print(f"No JSON files found in the directory '{USER_JSON_DIR}'.")
        else:
            print(f"\n--- Found {len(json_files)} JSON files, starting batch processing ---")
            for i, filename in enumerate(json_files):
                filepath = os.path.join(USER_JSON_DIR, filename)
                print(f"\n[{i + 1}/{len(json_files)}] Processing file: {filename}")

                evaluate_user_session(filepath, DEFAULT_SCHEMA_FOLDER, SCHEMA_BASE_DIR)

            print("\n--- Evaluation of all JSON files completed ---")

    print("\nEvaluation process finished.")