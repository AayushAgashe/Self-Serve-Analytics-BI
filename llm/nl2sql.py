def generate_sql(client, query, schema):
    
    prompt = f"""
    You are an expert SQL generator.
 
    Rules:
    - Use DuckDB SQL
    - Table name is: df
    - Columns: txn_id, amount, status, created_at
    - Revenue = SUM(amount) WHERE status='SUCCESS'
    
    IMPORTANT:
    - If query asks for comparison (e.g. "this month vs last month", "increase", "decrease"):
    → ALWAYS return BOTH values (current and previous)
    
    - Use DATE_TRUNC for monthly comparisons
    - Use CURRENT_DATE
    
    Return ONLY SQL.
    
    Query:
    {query}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content