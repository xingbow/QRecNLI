from sqlalchemy import create_engine
from langchain.sql_database import SQLDatabase
import os, json, re
from langchain_experimental.sql import SQLDatabaseChain
from langchain_core.runnables import RunnablePassthrough
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from sqlalchemy.sql import text
import numpy as np
import pandas as pd

import warnings
# Suppress specific deprecation warnings from Pydantic
warnings.simplefilter('ignore', DeprecationWarning)



try:
    import globalVariable as GV
except ImportError:
    import app.dataService.globalVariable as GV

def remove_sql_clause(sql_str, clause_name):
    """
    Removes the specified clause from the SQL string.

    Parameters:
    sql_str (str): The original SQL string.
    clause_name (str): The name of the clause to remove.

    Returns:
    str: The SQL string with the clause removed.
    """
    # Define a regex pattern to match the clause and any following characters up to the next clause or the end of the string
    pattern = re.compile(r"(?i)\s*{}\s+.*?(?=(?:\s+\w+\s+|$))".format(re.escape(clause_name)))
    
    # Use the pattern to remove the clause from the SQL string
    return pattern.sub("", sql_str)

### from langchain_experimental.sql
PROMPT_SUFFIX = """Only use the following tables:
{table_info}

Question: {input}"""

_DEFAULT_TEMPLATE = """Given an input question, first create a syntactically correct SQL query to run, then look at the results of the query and return the answer. You can order the results by a relevant column to return the most interesting examples in the database.

Never query for all the columns from a specific table, only ask for a the few relevant columns given the question.

Pay attention to avoid SQL aliases (e.g., renaming columns, MIN/MAX/SUM/AVG/COUNT, table names) in SQL Query, e.g., 
1. Instead of SELECT SUM(order_quantity) AS total_quantity, please use SELECT SUM(order_quantity) (without "AS" for aliases).
2. Instead of SELECT c.customer_name, ca.address_type
 FROM Customers c
 JOIN Customer_Addresses ca ON c.customer_id = ca.customer_id, 
 please use SELECT Customers.customer_name, Customer_Addresses.address_type 
 FROM Customers JOIN Customer_Addresses ON Customers.customer_id = Customer_Addresses.customer_id (without table name aliases)
3. Instead of SELECT MAX(active_from_date) AS last_active_date, please use SELECT MAX(active_from_date) (without "AS" for aliases).


Pay attention to use only the column names that you can see in the schema description. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.


Use the following format:

Question: Question here
SQLQuery: SQL Query to run
SQLResult: Result of the SQLQuery
Answer: Final answer here

"""

PROMPT = PromptTemplate(
    input_variables=["input", "table_info"],
    template=_DEFAULT_TEMPLATE + PROMPT_SUFFIX,
)

class sqlModel(object):
    def __init__(self):
        self.model = ChatOpenAI(model_name="gpt-3.5-turbo-1106", temperature=0, openai_api_key = GV.openai_key)
                                # , model_kwargs={"seed": 42})
        self.spider_dataset_dir = GV.SPIDER_FOLDER

    def predict(self, q, db_id):
        database_path = os.path.join(self.spider_dataset_dir, f'database/{db_id}/{db_id}.sqlite')  # Update this with the actual path
        # Create the SQLite URI for the database
        database_uri = f'sqlite:///{database_path}'
        engine = create_engine(database_uri)
        db = SQLDatabase(engine)
        db_chain = SQLDatabaseChain.from_llm(self.model, 
                          db,
                          use_query_checker=True,
                          return_sql = True,
                          verbose = False,
                          prompt=PROMPT
                         )
        res = db_chain.run(q)
        # remove limit clause
        res_ = remove_sql_clause(res, "LIMIT")
        return res_

    def sql2text(self, sql: str = "SELECT name ,  country ,  age FROM singer ORDER BY age DESC"):
        sql2text_prompt = """
        Please translate the following sql query into natural language to users who do not have sql knowledge and keep it simple. Please only output the natural language result.

        {sql}

        Natural language:
        """
        prompt = PromptTemplate.from_template(sql2text_prompt)
        sql2text_chain = prompt | self.model
        res =sql2text_chain.invoke({
            "sql": sql
        })
        return res.content


if __name__ == '__main__':
    # Define the path to your SQLite database file
    db_name = "customers_and_addresses"
    q = "Show me the total quantity of each product that has been ordered."
    # nl 2 sql
    sqlmodel = sqlModel()
    res = sqlmodel.predict(q, db_name)
    print(f"result for the {q}: \n {res}")
    # sql 2 text
    nl = sqlmodel.sql2text()
    print(f"{nl}")