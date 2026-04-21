# ============================================
# PIPELINE
# ============================================
 
from rag.retriever import retrieve_schema
from llm.query_understanding import understand_query
from llm.hypothesis import generate_hypotheses
from llm.nl2sql import generate_sql
from llm.answer import synthesize_answer
 
from sql.cleaner import clean_sql
from sql.validator import validate_and_fix_sql
from sql.executor import execute_sql
 
from utils.time_utils import fix_time_filters
from utils.chart import generate_chart, decide_chart_type
from utils.confidence import compute_confidence
 
from analytics.hypotesting import test_hypotheses, select_best_hypothesis
from sql.validator import validate_and_fix_sql

  
def run_pipeline(client, query, df):
 
    # ----------------------------------------
    # 1. RAG
    # ----------------------------------------
    schema = retrieve_schema(query)
 
    # ----------------------------------------
    # 2. Query Understanding
    # ----------------------------------------
    parsed = understand_query(client, query)
    metric = parsed.get("metric")
    time_filter = parsed.get("time_filter")
    comparison = parsed.get("comparison")
    complexity = parsed.get("complexity", "simple")
 
    if "why" in query.lower():
        complexity = "complex"
 
    # ----------------------------------------
    # 3. Hypotheses
    # ----------------------------------------
    hypotheses = generate_hypotheses(client, query, complexity)
 
    # ----------------------------------------
    # 4. SQL Generation
    # ----------------------------------------
    raw_sql = generate_sql(client, query, schema) 
    sql = fix_time_filters(clean_sql(raw_sql))
 
    # ----------------------------------------
    # 5. Execution 
    # ----------------------------------------
    try:
        sql = validate_and_fix_sql(sql, query)
        result, success = execute_sql(sql, df)
    except:
        result, success = None, False
 
    # ----------------------------------------
    # 6. Hypothesis Testing
    # ----------------------------------------
    hypothesis_results = test_hypotheses(
        hypotheses,
        df,
        metric,
        time_filter,
        client
    )
    best_hypothesis = select_best_hypothesis(hypothesis_results)
 
    # ----------------------------------------
    # 7. Chart (DRIVEN BY BEST HYPOTHESIS)
    # ----------------------------------------
    chart = None
 
    # Prefer hypothesis-driven data
    chart_df = None
 
    if best_hypothesis:
        metric = best_hypothesis["metric"]
    
        if metric == "transactions":
            chart_sql = """
            SELECT DATE(created_at) as date, COUNT(*) as value
            FROM df
            GROUP BY date
            ORDER BY date
            """
    
        elif metric == "revenue":
            chart_sql = """
            SELECT DATE(created_at) as date, SUM(amount) as value
            FROM df
            WHERE status='SUCCESS'
            GROUP BY date
            ORDER BY date
            """

        elif metric == "failures":
            chart_sql = """
            SELECT DATE(created_at) as date, COUNT(*) as value
            FROM df
            WHERE status='FAILED'
            GROUP BY date
            ORDER BY date
            """
    
        else:
            chart_sql = None
    
        if chart_sql:
            chart_sql = fix_time_filters(chart_sql)
            chart_df, ok = execute_sql(chart_sql, df)
        
            if not ok:
                chart_df = None
 
    # Fallback to main result
    if chart_df is None:
        chart_df = result
 
    # LLM decides chart
    chart_type = decide_chart_type(client, query, chart_df)
 
    chart = generate_chart(chart_df, chart_type)
 
 
    # ----------------------------------------
    # 8. Answer
    # ----------------------------------------
    if success:
        answer = synthesize_answer(client, query, result, best_hypothesis)
    else:
        answer = "Could not retrieve reliable results."
 
    # ----------------------------------------
    # 9. Confidence
    # ----------------------------------------
    variance = None
    if result is not None and result.shape[1] >= 2:
        try:
            variance = result.iloc[:, 1].var()
        except:
            pass
 
    confidence, confidence_reason = compute_confidence(
        success,
        len(result) if result is not None else 0,
        hypothesis_results,
        query
    )
 
    # ----------------------------------------
    # 10. Output
    # ----------------------------------------
    return {
        "answer": answer,
        "sql": sql,
        "hypotheses": hypotheses,
        "hypothesis_results": hypothesis_results,
        "best_hypothesis": best_hypothesis,
        "confidence": confidence,
        "confidence_reason": confidence_reason,
        "chart": chart
    }