# ============================================
# STREAMLIT APP
# ============================================
 
import streamlit as st
from config import get_client
from data.generate_data import generate_payments_data
from pipeline.pipeline import run_pipeline
 
# --------------------------------------------
# PAGE CONFIG
# --------------------------------------------
st.set_page_config(
    page_title="AI Analytics Assistant",
    layout="wide"
)
 
# --------------------------------------------
# INIT
# --------------------------------------------
@st.cache_resource
def init():
    client = get_client()
    df = generate_payments_data(15000)
    return client, df
 
client, df = init()
 
# --------------------------------------------
# UI HEADER
# --------------------------------------------
st.title("AI Analytics Assistant")
st.markdown("Ask business questions and get instant insights + charts")
 
# --------------------------------------------
# INPUT
# --------------------------------------------
query = st.text_input("Enter your question")
 
# --------------------------------------------
# RUN BUTTON
# --------------------------------------------
if st.button("Run Analysis") and query:
    
    with st.spinner("Analyzing..."):
        output = run_pipeline(client, query, df)
    
    # ----------------------------------------
    # DISPLAY RESULTS
    # ----------------------------------------
    st.subheader("Business Insight")
    st.write(output["answer"])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("SQL")
        st.code(output["sql"], language="sql")
    
    with col2:
        st.subheader("Confidence")
        st.metric(label="Confidence Score", value=output["confidence"])
    
    st.subheader("Hypotheses")
    for h in output["hypotheses"]:
        st.write(f"- {h}")
    
    # ----------------------------------------
    # CHART
    # ----------------------------------------
    if output["chart"]:
        st.subheader("Visualization")
        st.altair_chart(output["chart"], use_container_width=True)
 