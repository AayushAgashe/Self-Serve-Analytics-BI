import ssl
ssl._create_default_https_context = ssl._create_unverified_context
 
from config import get_client
from data.generate_data import generate_payments_data
from pipeline.pipeline import run_pipeline
 
client = get_client()
df = generate_payments_data(15000)
 
queries = [
    "What is total revenue?",
    "Show daily revenue for last 30 days"
]
 
for q in queries:
    run_pipeline(client, q, df)