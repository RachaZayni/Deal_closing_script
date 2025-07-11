import streamlit as st
import os


st.set_page_config(page_title=" Closing Deal Chatbot", page_icon="🤖", layout="centered")

    # Title and header
st.markdown(
        """
        <h1 style="text-align: center; color: #4B8BBE; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
            🤖 Closing Deal Chatbot
        </h1>
        <hr>
        """,
        unsafe_allow_html=True,
    )

from pydantic_ai import Agent
with open("file.txt", "r", encoding="utf-8") as file:
    script_text = file.read()

with open("info.txt", "r", encoding="utf-8") as file:
      info_text = file.read()


with open("Product_data.txt", "r", encoding="utf-8") as file:
      ProdData = file.read()


with open("customer_data.txt", "r", encoding="utf-8") as file:
      CustData = file.read()

from pydantic import BaseModel
from typing import List, Dict



if "agent" not in st.session_state:
     st.session_state.agent = Agent(
         name="CloseMaster AI",
         model='openai:gpt-4o-mini',
        system_prompt=f"""
        You are a professional sales agent. I will give you:

1. A string containing buyer and product context :
Product information: {ProdData}

Customer information: {CustData}

2. A string containing a deal-closing script (based on a framework like C.L.O.S.E., 4C, or custom branching logic):
{script_text}

Your tasks:
- Read and understand both strings
- Use the script as your conversation logic
- Begin a realistic deal-closing conversation with the buyer, assuming the persona provided
- Handle objections using empathy, ROI justification, and urgency
- Adapt replies dynamically until the deal is either closed successfully or clearly lost
- return your response directly without any initial statement.
- once you feel the client want to close the chat say Goodbye
Be professional, confident, and consultative. Only ask me for clarification if the data is incomplete or contradictory.

"""
        )


if "corrector_agent" not in st.session_state:
    st.session_state.corrector_agent = Agent(
        name="LogicalCorrector",
        model='openai:gpt-4o-mini',#model="google:gemini-pro"
        system_prompt=f"""
        You are a logical deal-closing chat corrector.
        You will receive a conversation between a client and an assistant.
         
        Your task:
        - Evaluate the assistant's latest response in the context of the conversation.
        - If the response is illogical, off-topic, repetitive, or unhelpful, correct it.
        - Avoid repeating questions or statements already made in the conversation.
        - If the response is good and logical, leave it as is.
        
        **Important rules:**
        - NEVER repeat a question or message that has already been said earlier.
        - Use the conversation history to guide the next logical step — avoid loops or resets.
        - Only return the assistant’s improved (or unchanged) response. Do not include any explanations.
        """

    )
    # Initialize chat history in session state
Corrector_Message=""
if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        resp = st.session_state.agent.run_sync("Start the conversation")
        Corrector_Message="Assistant: "+resp.output+"\n"
        st.session_state.chat_history.append({
            "role": "bot",
            "message": resp.output,
        })







class MessageContext(BaseModel):
    messages: List[Dict[str, str]] = []

    def add_message(self, role: str, content: str):
            self.messages.append({"role": role, "content": content})
    def get_context(self) -> List[Dict[str, str]]:
            return self.messages

if 'context' not in st.session_state:
        st.session_state.context = MessageContext()

    # Function to simulate bot response (replace with real logic)
def generate_bot_response(user_message):
        bot_response = st.session_state.agent.run_sync(user_message, context=st.session_state.context.get_context())
        st.session_state.context.add_message("assistant", bot_response.output)
        return bot_response

    # Chat container (scrollable)
chat_container = st.container()

with chat_container:
        for chat in st.session_state.chat_history:
            if chat["role"] == "user":
                st.markdown(
                    f"""
                    <div style="text-align: right; margin: 10px 0;">
                        <span style="background-color:#DCF8C6; padding:8px 12px; border-radius:12px; display: inline-block; max-width: 70%;">
                        <b>You:</b> {chat['message']}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div style="text-align: left; margin: 10px 0;">
                        <span style="background-color:#F1F0F0; padding:8px 12px; border-radius:12px; display: inline-block; max-width: 70%;">
                        <b>Bot:</b> {chat['message']}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # User input form
with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Your message:", placeholder="Type your message here...", key="input")
        submit_button = st.form_submit_button(label="Send")

if submit_button and user_input.strip() != "":
        # Add user message
        user_resp=user_input.strip()
        st.session_state.chat_history.append({"role": "user", "message": user_resp})
        st.session_state.context.add_message("user", user_resp)
        Corrector_Message+="Client: "+user_resp+"\n"
        # Generate bot reply
        bot_reply = generate_bot_response(user_resp).output
        Corrector_Message+="Assistant: "+bot_reply+"\n"
        corrected=st.session_state.corrector_agent.run_sync(Corrector_Message)
        st.session_state.chat_history.append({"role": "bot", "message":corrected.output})




