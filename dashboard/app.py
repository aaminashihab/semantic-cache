import streamlit as st
import sqlite3
import pandas as pd
import datetime

st.set_page_config(page_title="Semantic Cache Dashboard", layout="wide")

st.title("Semantic Cache Dashboard")
st.markdown("Monitor caching performance, latency, and cost savings.")

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "semantic_cache.db")

def load_data():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            df = pd.read_sql_query("SELECT * FROM request_logs ORDER BY timestamp DESC", conn)
            cache_df = pd.read_sql_query("SELECT * FROM cache_records", conn)
        return df, cache_df
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame()

df, cache_df = load_data()

if df.empty:
    st.warning("No data found. Ensure the cache has processed some requests.")
else:
    # Key Metrics
    total_requests = len(df)
    exact_hits = len(df[df['exact_hit'] == 1])
    semantic_hits = len(df[df['semantic_hit'] == 1])
    total_hits = exact_hits + semantic_hits
    
    hit_rate = total_hits / total_requests * 100 if total_requests > 0 else 0
    exact_hit_rate = exact_hits / total_requests * 100 if total_requests > 0 else 0
    semantic_hit_rate = semantic_hits / total_requests * 100 if total_requests > 0 else 0
    
    api_calls_avoided = total_hits
    
    avg_latency = df['latency_ms'].mean()
    p50_latency = df['latency_ms'].quantile(0.5)
    p95_latency = df['latency_ms'].quantile(0.95)
    
    tokens_saved = df['tokens_saved'].sum()
    cost_saved = df['estimated_cost_saved'].sum()

    st.subheader("Performance Overview")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Overall Hit Rate", f"{hit_rate:.1f}%")
    col2.metric("Exact Hit Rate", f"{exact_hit_rate:.1f}%")
    col3.metric("Semantic Hit Rate", f"{semantic_hit_rate:.1f}%")
    col4.metric("API Calls Avoided", f"{api_calls_avoided}")
    col5.metric("Total Requests", f"{total_requests}")

    st.subheader("Savings & Latency")
    col6, col7, col8, col9, col10 = st.columns(5)
    col6.metric("Total Tokens Saved", f"{tokens_saved:,}")
    
    if tokens_saved > 0 and cost_saved == 0.0:
        col7.metric("Estimated $ Saved", "$0.00 (unconfigured)")
    else:
        col7.metric("Estimated $ Saved", f"${cost_saved:.4f}")
        
    col8.metric("Avg Latency", f"{avg_latency:.1f} ms")
    col9.metric("P50 Latency", f"{p50_latency:.1f} ms")
    col10.metric("P95 Latency", f"{p95_latency:.1f} ms")
    
    st.markdown("---")

    col_charts1, col_charts2 = st.columns(2)
    
    with col_charts1:
        st.subheader("Hit/Miss Timeline")
        timeline_df = df.copy()
        timeline_df['timestamp'] = pd.to_datetime(timeline_df['timestamp'])
        timeline_df.set_index('timestamp', inplace=True)
        # Resample to 1-minute intervals for better viewing (or seconds if few requests)
        # Using string mapping for easier chart building
        chart_data = timeline_df[['response_source']].value_counts().reset_index(name='count')
        st.bar_chart(data=chart_data, x='response_source', y='count')

    with col_charts2:
        st.subheader("Similarity Distribution")
        sim_df = df[df['similarity'].notnull()]
        if not sim_df.empty:
            # We can use a simple histogram
            st.bar_chart(sim_df['similarity'].value_counts(bins=10).sort_index())
        else:
            st.info("No similarity scores recorded yet.")

    st.subheader("Recent Requests")
    st.dataframe(df.drop(columns=['fingerprint'], errors='ignore').head(50), use_container_width=True)

    st.subheader("Cache Records Overview")
    st.dataframe(cache_df[['id', 'faiss_id', 'prompt', 'hit_count', 'provider', 'model', 'timestamp']].sort_values(by='hit_count', ascending=False).head(50), use_container_width=True)
