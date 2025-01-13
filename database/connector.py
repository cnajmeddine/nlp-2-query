from sqlalchemy import create_engine, text
import pandas as pd

class DatabaseConnector:
    def __init__(self, host, database, user, password):
        self.engine = create_engine(
            f'postgresql://{user}:{password}@{host}/{database}'
        )
        
    def get_table_schema(self):
        query = """
        SELECT 
            table_name, 
            column_name, 
            data_type
        FROM information_schema.columns c
        LEFT JOIN pg_description d ON 
            d.objoid = (select oid from pg_class where relname = c.table_name)
            AND d.objsubid = c.ordinal_position
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position;
        """
        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            return pd.DataFrame(result.fetchall(), 
                             columns=['table', 'column', 'type'])
    
    def execute_query(self, query):
        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            return pd.DataFrame(result.fetchall(), 
                             columns=result.keys())