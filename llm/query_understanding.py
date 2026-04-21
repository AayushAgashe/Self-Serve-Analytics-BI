def understand_query(client, query):
    
    prompt = f"""
    Extract structured information from the query.
 
    Return JSON only:
 
    {{
      "complexity": "simple or complex",
      "metric": "revenue | transactions | avg_value | failures",
      "time_filter": "7d | 30d | monthly | none",
      "comparison": "yes or no"
    }}
 
    Query: {query}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )
    
    import json
    return json.loads(response.choices[0].message.content)