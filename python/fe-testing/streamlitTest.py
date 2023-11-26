import streamlit as st
import requests as re
# import asyncio

st.title("Testing Data Streaming")

url = "https://mercury-jzz5.onrender.com/test"
chat_output = re.get(url)

st.text(chat_output.text)