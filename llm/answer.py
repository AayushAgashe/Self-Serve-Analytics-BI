def synthesize_answer(client, query, df, best_hypothesis=None):
    
    if df is None or df.empty:
        return "No data available."
    
    # Extract structured info
    data_str = df.to_string(index=False)
    
    hypothesis_text = ""
    
    if best_hypothesis:
        hypothesis_text = f"""
        Best Hypothesis:
        {best_hypothesis['hypothesis']}
        
        Change: {best_hypothesis['change_pct']}%
        """
    
    prompt = f"""
    You are a business analyst.
 
    Generate a clear, concise insight.
 
    Rules:
    - Answer the question directly
    - Use the data provided
    - If hypothesis exists, explain WHY using it
    - Mention % change if available
    - No generic statements
    - 1-2 sentences max
 
    Query:
    {query}
 
    Data:
    {data_str}
 
    {hypothesis_text}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content.strip()
 