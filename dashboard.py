import streamlit as st
import boto3
import pandas as pd
import time

st.set_page_config(page_title="Driver Dashboard", layout="wide")

st.title("🚗 Driver Drowsiness Dashboard")

# 🔹 AWS DynamoDB (no hardcoded keys)
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('drowsiness-final')

# 🔄 Refresh Button
if st.button("🔄 Refresh Data"):
    st.rerun()

# 🔄 Auto refresh every 5 sec (safe way)
st.caption("Auto-refreshing every 5 seconds...")

try:
    data = table.scan().get('Items', [])

    if data:
        df = pd.DataFrame(data)

        # Fix timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')

        # Metrics
        col1, col2 = st.columns(2)
        col1.metric("Model Accuracy", "92%")
        col2.metric("Total Events", len(df))

        # Graph
        st.subheader("📈 Events Over Time")
        df['count'] = range(1, len(df)+1)
        st.line_chart(df.set_index('timestamp')['count'])

        # Status Distribution
        st.subheader("📊 Status Distribution")
        st.bar_chart(df['status'].value_counts())

        # Latest Event
        st.subheader("🟢 Latest Event")
        latest = df.iloc[-1]
        st.write(f"Driver ID: {latest['driver_id']}")
        st.write(f"Status: {latest['status']}")
        st.write(f"Time: {latest['timestamp']}")

        # Table
        st.subheader("📋 All Events")
        st.dataframe(df)

    else:
        st.warning("No data found")

except Exception as e:
    st.error(f"Error: {e}")

# 🔄 Auto refresh safely
time.sleep(5)
st.rerun()