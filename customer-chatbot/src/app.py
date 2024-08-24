"""customer-chatbot

Chatbot emulating the customer experience for intereacting with a virtual
retail store.
"""
import os
import json
import streamlit as st
import requests

ENV_AI_BACKEND_ENDPOINT = "AI_BACKEND_ENDPOINT"

GREETING="Thank you for visiting our store.  How may we help you?"

URL = "http://localhost:8080"
if ENV_AI_BACKEND_ENDPOINT in os.environ:
    URL = os.environ[ENV_AI_BACKEND_ENDPOINT]

st.title("💬 Let's GOOOOO!!!! Shoe Store")

st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)

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
    chat_params = {"user_message": str(st.session_state.messages)}

    print ("chat_url:", chat_url, "chat_params:", chat_params)
    response = requests.post(chat_url,
                        params=chat_params,
                        timeout=30)

    print("response.content:", response.content)
    msg = response.content.decode('UTF-8')
    print("msg", msg)

    msgJson = json.loads(msg)
    print()
    print ("DATA:::::")
    print()
    print (msgJson)
    print()

    ai_response = msgJson["most_recent_ai_response"]["content"]
    ai_response_json = json.loads(ai_response)
    ai_response_str = ai_response_json["Response"]

    st.session_state.messages.append({"role": "assistant",
                                      "content": ai_response_str})
    messages.chat_message("assistant").write(ai_response_str)
