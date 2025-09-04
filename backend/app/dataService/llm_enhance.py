# llm_enhance.py

import json
import os
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import globalVariable as GV


class LLMEnhancer:
    def __init__(self, db_id, max_workers=20):
        self.db_id = db_id
        self.max_workers = max_workers
        self.logger = logging.getLogger(__name__)

        # --- Cache path configuration ---
        # 1. static, read-only Spider reference cache
        self.spider_cache_path = os.path.join(GV.SPIDER_FOLDER, 'metadata_enrichment_cache4spider.json')
        # 2. dynamic, writable cache for the current db_id
        self.db_cache_path = os.path.join(GV.SPIDER_FOLDER, f'metadata_enrichment_cache4{self.db_id}.json')

        # --- Load cache ---
        self.spider_cache = self._load_cache(self.spider_cache_path)
        self.db_cache = self._load_cache(self.db_cache_path)

        self.logger.info(f"Loaded {len(self.spider_cache)} items from Spider cache.")
        self.logger.info(f"Loaded {len(self.db_cache)} items from DB cache for '{self.db_id}'.")

        # --- LLM model initialization ---
        try:
            self.model = ChatOpenAI(model_name="gpt-4o", temperature=0, openai_api_key = GV.openai_key, model_kwargs={"seed": 42})
            self.logger.info("LLM Enhancer initialized with LLM model.")
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM model. Error: {e}")
            self.model = None

    def _clean_llm_output(self, text):
        """A safety net to clean up potential unwanted notes or prefixes from the LLM response."""
        text = text.split('(Note:')[0].strip()
        text = text.split('Note:')[0].strip()
        text = text.split('*(Note:')[0].strip()
        if text.startswith('Output:'):
            text = text.replace('Output:', '', 1).strip()
        return text

    def _load_cache(self, cache_path):
        """Loads a specific metadata knowledge cache from a local file."""
        try:
            if os.path.exists(cache_path):
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            self.logger.warning(f"Could not load cache from {cache_path}. Will start with an empty cache. Error: {e}")
        return {}

    def _save_db_cache(self):
        """Saves ONLY the dynamic db-specific cache to a local file."""
        try:
            os.makedirs(os.path.dirname(self.db_cache_path), exist_ok=True)
            with open(self.db_cache_path, 'w', encoding='utf-8') as f:
                json.dump(self.db_cache, f, indent=4, ensure_ascii=False)
        except IOError as e:
            self.logger.error(f"Error: Could not save DB cache to {self.db_cache_path}. Error: {e}")

    def _fetch_description_from_llm(self, full_name):
        """This method only performs the LLM request and returns the result."""
        if not self.model:
            self.logger.error("LLM model is not available. Returning original name.")
            return full_name, None

        parts = full_name.split(':', 1)
        table_name = parts[0].strip()
        column_name = parts[1].strip() if len(parts) > 1 else table_name

        if len(parts) > 1:
            prompt_text = f'''Your task is to provide a concise, direct business definition phrase for a database column. Do not add any notes, explanations, or prefixes.
            Example 1: Input: Table="orders", Column="order_date", Output: The date an order was placed, used for sales trend analysis.
            Example 2: Input: Table="customers", Column="customer_name", Output: Full name of the customer for identification.
            Your task: Input: Table="{table_name}", Column="{column_name}", Output:'''
        else:
            prompt_text = f'''Your task is to provide a concise, direct business summary phrase for a database or data topic. Do not add any notes, explanations, or prefixes.
            Example 1: Input: Topic="customers_and_addresses", Output: Personal customer information and their associated residential addresses.
            Example 2: Input: Topic="flight_company", Output: Operational data for airline companies and their flights.
            Your task: Input: Topic="{table_name}", Output:'''

        try:
            messages = [
                SystemMessage(
                    content="You are a professional data analyst who is an expert in data warehousing and business scenarios. You only provide direct answers as requested."),
                HumanMessage(content=prompt_text)
            ]
            response = self.model.invoke(messages)
            description = self._clean_llm_output(response.content.strip())
            return full_name, description
        except Exception as e:
            self.logger.error(f"LLM call failed for '{full_name}'. Error: {e}")
            return full_name, None

    def get_enriched_description(self, full_name):
        """
        Gets a single description by checking both caches. If not found, calls LLM and saves to the DB-specific cache.
        """
        # 1. Prioritize checking dynamic DB caches
        if full_name in self.db_cache:
            return self.db_cache[full_name]

        # 2. Secondly, check the static Spider cache.
        if full_name in self.spider_cache:
            return self.spider_cache[full_name]

        # 3. If none can be found, call LLM to automatically generate a description
        self.logger.info(f"Cache miss for '{full_name}' in both caches. Calling LLM...")
        _, description = self._fetch_description_from_llm(full_name)

        if description:
            self.logger.info(f"LLM generated description: '{description}'")
        # 4. deposit and save the newly generated results into the dynamic DB cache
            self.db_cache[full_name] = description
            self._save_db_cache()
            return description
        else:
            return full_name  # LLM call fails, return original name

    def enrich_batch(self, all_items):
        """
        Processes a batch of items concurrently. It only calls the LLM for items not found in ANY cache.
        New items are saved ONLY to the DB-specific cache.
        """
        # 1. Filter out items that already exist in any of the caches
        items_to_process = sorted([
            item for item in all_items
            if item not in self.db_cache and item not in self.spider_cache
        ])

        if not items_to_process:
            # self.logger.info("All provided items are already in one of the caches. No new items to process.")
            return

        results = {}
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_item = {executor.submit(self._fetch_description_from_llm, item): item for item in
                              items_to_process}
            for future in tqdm(as_completed(future_to_item), total=len(items_to_process), desc="Processing Batch"):
                item_name, description = future.result()
                if description:
                    results[item_name] = description

        if results:
            self.logger.info(f"Successfully processed {len(results)} new items. Updating DB-specific cache...")
        # 2. Update new results to dynamic DB cache
            self.db_cache.update(results)
            self._save_db_cache()
            self.logger.info("DB-specific cache updated and saved successfully.")
        else:

            self.logger.warning("No items were successfully processed in this batch.")
