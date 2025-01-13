import requests
import json

class TextToSQL:
    def __init__(self, db_connector, api_key):
        self.db_connector = db_connector
        self.api_key = api_key
        self.schema = self.db_connector.get_table_schema()
        
    def _format_schema_for_prompt(self):
        """Format the database schema into a readable string for the LLM."""
        schema_info = []
        current_table = None
        columns = []
        
        for _, row in self.schema.iterrows():
            if current_table != row['table']:
                if current_table is not None:
                    schema_info.append(f"Table: {current_table}\nColumns: {', '.join(columns)}\n")
                current_table = row['table']
                columns = []
            columns.append(f"{row['column']} ({row['type']})")
        
        if current_table is not None:
            schema_info.append(f"Table: {current_table}\nColumns: {', '.join(columns)}\n")
        
        return "\n".join(schema_info)

    def generate_query(self, text):
        """Generate SQL query from natural language using OpenRouter API."""
        schema_info = self._format_schema_for_prompt()
        
        prompt = f"""Given the following database schema:

{schema_info}

Convert this question to a SQL query: "{text}"

Generate only the SQL query without any explanations or additional text. The query should be valid PostgreSQL syntax."""

        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                data=json.dumps({
                    "model": "meta-llama/llama-3-8b-instruct:extended",
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                })
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract the SQL query from the response
            generated_query = result['choices'][0]['message']['content'].strip()
            
            # Remove any markdown code blocks if present
            generated_query = generated_query.replace('```sql', '').replace('```', '').strip()
            
            return generated_query
            
        except Exception as e:
            raise Exception(f"Failed to generate SQL query: {str(e)}")