"""${{values.artifact_id}}

${{values.description}}
"""
import streamlit as st
from openai import OpenAI

OPENAI_API_URL="http://envision:8000/v1"
OPENAI_MODEL_NAME="meta-llama/Meta-Llama-3.1-8B-Instruct"
OPENAI_TEMPERATURE=0.8
OPENAI_MAX_TOKENS=1000

SYSTEM_PROMPT="You are a helpful sales agent for a shoe store." \
              "Only talk about selling shoes." \
              "Do not participate in hateful or abusive conversations."

GREETING="Thank you for visiting our store.  How may we help you?"

st.title("💬 Nike Shoe Store")

client = OpenAI(base_url=OPENAI_API_URL, api_key="api-key")

messages = st.container(height=300)

if "messages" not in st.session_state:
    st.session_state["messages"] = []
messages.chat_message("assistant").write(GREETING)

for msg in st.session_state.messages:
    messages.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    messages.chat_message("user").write(prompt)

    openai_messages = [{"role": "assistant", "content": SYSTEM_PROMPT}] + st.session_state.messages
    print ("openai_messages", openai_messages)
    print ("st.session_state.messages", st.session_state.messages)

    response = client.chat.completions.create(model=OPENAI_MODEL_NAME,
                                              messages=openai_messages,
                                              max_tokens=OPENAI_MAX_TOKENS,
                                              temperature=OPENAI_TEMPERATURE)
    msg = response.choices[0].message.content

    st.session_state.messages.append({"role": "assistant", "content": msg})
    messages.chat_message("assistant").write(msg)
