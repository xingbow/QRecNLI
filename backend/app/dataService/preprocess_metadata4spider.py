# --- START OF FILE preprocess_metadata4spider.py ---

import json
import os
import re
import logging
from llm_enhance import LLMEnhancer
import globalVariable as GV

# --- CONFIGURATION ---
INPUT_TABLES_FILE = os.path.join(GV.SPIDER_FOLDER, "tables.json")
# This is the target output file. The LLMEnhancer will write to a file
# named based on the db_id we provide it. We will use 'spider' as the ID
OUTPUT_CACHE_FILE = os.path.join(GV.DATA_FOLDER, 'metadata_enrichment_cache4spider.json')
CACHE_ID = "spider"  # The ID used to reference the main Spider cache.
MAX_CONCURRENT_WORKERS = 20

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def clean_name(name: str) -> str:
    """
    Cleans a database/table/column name to be more human-readable.
    - Replaces underscores with spaces.
    - Removes all digits.
    - Converts to lowercase and strips whitespace.
    Example: "flight_company_1" -> "flight company"
    """
    return re.sub(r'[0-9]+', '', name.replace("_", " ")).strip().lower()


def generate_metadata_cache_concurrently():
    """
    Traverses the Spider schema file (tables.json), cleans all metadata names,
    and uses the LLMEnhancer to generate and save natural language descriptions
    for them into the main Spider cache file.
    """
    if not os.path.exists(INPUT_TABLES_FILE):
        logger.error(f"Input file '{INPUT_TABLES_FILE}' not found.")
        return

    # 1. Load the database schema file and extract all unique metadata items
    logger.info(f"Loading database metadata from '{INPUT_TABLES_FILE}'...")
    with open(INPUT_TABLES_FILE, 'r', encoding='utf-8') as f:
        schemas = json.load(f)

    all_metadata_items = set()
    for db_schema in schemas:
        # Clean the database ID (e.g., 'flight_1' -> 'flight')
        db_id = clean_name(db_schema['db_id'])
        all_metadata_items.add(db_id)

        # Use original table names and clean them
        table_names_original = db_schema['table_names_original']
        cleaned_table_names = [clean_name(name) for name in table_names_original]

        column_names_original = db_schema['column_names_original']

        for table_name in cleaned_table_names:
            all_metadata_items.add(table_name)
            # Add a wildcard entry for the table as a whole topic
            all_metadata_items.add(f"{table_name}: *")

        for table_idx, col_name in column_names_original:
            if table_idx >= 0:
                # Get the already cleaned table name
                cleaned_table = cleaned_table_names[table_idx]
                # Clean the column name
                cleaned_column = clean_name(col_name)

                full_col_name = f"{cleaned_table}: {cleaned_column}"
                all_metadata_items.add(full_col_name)

    logger.info(
        f"Successfully extracted and cleaned {len(all_metadata_items)} total unique metadata items from the Spider dataset.")

    # 2. Initialize the LLMEnhancer.
    # By setting db_id=CACHE_ID ('spider'), we instruct the enhancer to use
    logger.info(f"Initializing LLMEnhancer for cache ID: '{CACHE_ID}'")
    enhancer = LLMEnhancer(db_id=CACHE_ID, max_workers=MAX_CONCURRENT_WORKERS)

    # 3. Call the concurrent batch processing method.
    # The enhancer will receive the cleaned names and generate descriptions for them.
    enhancer.enrich_batch(list(all_metadata_items))

    logger.info(f"Processing complete! Enriched metadata cache saved to '{OUTPUT_CACHE_FILE}'.")
    logger.info(f"The cache now contains a total of {len(enhancer.db_cache)} entries.")


if __name__ == "__main__":
    generate_metadata_cache_concurrently()
