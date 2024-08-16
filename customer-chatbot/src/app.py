"""customer-chatbot

Chatbot emulating the customer experience for intereacting with a virtual
retail store.
"""
import os
import streamlit as st
import requests

GREETING="Thank you for visiting our store.  How may we help you?"

CAPABILITY="simple" # simple, tool, or rag

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
    if CAPABILITY == "rag":
        chat_url = URL + "/ragchat"
        chat_params = {"userMessage": str(st.session_state.messages)}
    else:
        chat_url = URL + "/chat"
        chat_params = {"type": CAPABILITY,
                       "userMessage": str(st.session_state.messages)}

    print ("chat_url:", chat_url, "chat_params:", chat_params)
    response = requests.post(chat_url,
                        params=chat_params,
                        timeout=30)

    print("response.content:", response.content)
    msg = response.content.decode('UTF-8')
    print("msg", msg)

    st.session_state.messages.append({"role": "assistant", "content": msg})
    messages.chat_message("assistant").write(msg)
