"""${{values.artifact_id}}

${{values.description}}
"""
import os
import streamlit as st
import requests

GREETING="Thank you for visiting our store.  How may we help you?"

CAPABILITY="simple" # simple or tool

URL = "http://localhost:8080"
if "AI_PRODUCT_CATALOG_SVC_URL" in os.environ:
    URL = os.environ["AI_PRODUCT_CATALOG_SVC_URL"]

st.title("💬 Let's GOOOOO!!!! Shoe Store")

messages = st.container(height=300)

if "messages" not in st.session_state:
    st.session_state["messages"] = []
messages.chat_message("assistant").write(GREETING)

for msg in st.session_state.messages:
    messages.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    messages.chat_message("user").write(prompt)

    print ("st.session_state.messages", st.session_state.messages)
    chat_url = URL + "/chat"
    print ("chat_url:", chat_url)
    response = requests.post(chat_url,
                        params={"type": CAPABILITY,
                                "userMessage": str(st.session_state.messages)},
                        timeout=30)

    print("response.content:", response.content)
    msg = response.content.decode('UTF-8')
    print("msg", msg)

    st.session_state.messages.append({"role": "assistant", "content": msg})
    messages.chat_message("assistant").write(msg)
