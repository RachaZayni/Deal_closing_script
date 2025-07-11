import streamlit as st
from pydantic import BaseModel
import os,re
from typing import List, Dict
from main import create_prompt,generate_deal_closing
from pydantic_ai import Agent





class MessageContext(BaseModel):
    messages: List[Dict[str, str]] = []

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})

    def get_context(self) -> List[Dict[str, str]]:
        return self.messages



def extract_chosen_framework(response_text):
    # Use regex to find the line starting with Recommended Framework and get the text after colon
    pattern = r"^\**\s*Recommended Framework\s*:\s*(.+?)\**$"
    lines = response_text.splitlines()
    for line in lines:
        line_clean = line.strip()
        match = re.match(pattern, line_clean)
        if match:
            # Extracted framework name
            return match.group(1).strip()
    return None





prompt_to_choose_framework = create_prompt(
    "Final Agreement on Terms",
    "Slight hesitation on pricing",
    "Medium-sized enterprise deal with 2 decision-makers",
    "Overcome objections and secure verbal commitment",
    "Pricing and contract length concerns",
    "we meet previous week"
)







if 'framework' not in st.session_state:
    st.session_state.framework = ""


context = MessageContext()


# Your AI framework_agent setup
framework_agent = Agent(
    name="CloseMaster AI",
    model='openai:gpt-4o-mini',
)




tone_agent=Agent(
    name="psychologue",
    model='openai:gpt-4o-mini',
    system_prompt="""
        You are a professional psychologist specializing in buyer psychology and emotional intelligence in sales.

Based on the client's response or emotional state, recommend the most effective tone the sales representative should use next.

Possible tone outputs include:
- Friendly
- Assertive
- Consultative
- Empathetic
- Reassuring
- Urgent
- Calm
- Encouraging
- Neutral

Input:
Client's statement: "{client_text}"

Output:
- Recommended tone
- Brief psychological rationale
    """
)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = "info"
if 'client_info' not in st.session_state:
    st.session_state.client_info = ""
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'input' not in st.session_state:
    st.session_state.input = ""
if 'closing_style_label' not in st.session_state:
    st.session_state.closing_style_label = "🔁 Auto (Recommended)"

# Framework mappings
framework_options = {
    "🔁 Auto (Recommended)": "AI-decides",
    "🎯 Assumptive Close": "Assumptive Closing",
    "🤝 Summary Close": "Summary Closing",
    "📅 Urgency Close": "Urgency / Scarcity",
    "💬 Alternative Close": "Alternative Choice",
    "💼 Consultative Close": "Consultative / MEDDIC",
    "📋 Checklist Close": "Simple Checklist",
}

framework_explanations = {
    "🔁 Auto (Recommended)": "Let the AI decide the best closing method. Ideal for most users.",
    "🎯 Assumptive Close": "Act as if the deal is already done. Confident and persuasive.",
    "🤝 Summary Close": "Summarize key benefits and confirm agreement.",
    "📅 Urgency Close": "Create FOMO with deadlines or scarcity.",
    "💬 Alternative Close": "Offer choices to guide decision-making.",
    "💼 Consultative Close": "Value-focused approach. Ideal for B2B and complex sales.",
    "📋 Checklist Close": "Simple checklist of needs. Great for smaller deals.",
}

if 'context' not in st.session_state:
    st.session_state.context = MessageContext()

def send_message():
    user_input = st.session_state.input.strip()
    if user_input:
        # Add user message to context
        st.session_state.context.add_message("user", user_input)
        # Also add to chat_history for display
        st.session_state.chat_history.append(("User", user_input))

        # Get full context messages list
        messages = st.session_state.context.get_context()

        # Pass full context to agent (assuming your agent supports this)
        bot_response = st.session_state.main_agent.run_sync(user_input, user_context=messages)

        # Add bot response to context and chat_history
        st.session_state.context.add_message("assistant", bot_response.output)
        st.session_state.chat_history.append(("Bot", bot_response.output))

        # Clear input box
        st.session_state.input = ""
def info_page():
    global framework
    st.title("Client Information")

    st.session_state.client_info = st.text_area(
        "Enter client background, objections, goals, or deal context:",
        value=st.session_state.client_info,
        height=150
    )

    st.markdown("### 🧠 Select Closing Framework")
    st.session_state.closing_style_label = st.selectbox(
        "Choose your closing style:",
        options=list(framework_options.keys()),
        help="Pick a closing method that best fits the client situation.",
        index=list(framework_options.keys()).index(st.session_state.closing_style_label)
    )

    st.caption(f"💡 **Tip:** {framework_explanations[st.session_state.closing_style_label]}")

    with st.expander("ℹ️ Learn about each style"):
        for label, explanation in framework_explanations.items():
            st.markdown(f"**{label}** – {explanation}")

    if st.button("Proceed to Chatbot"):
        if st.session_state.client_info.strip() == "":
            st.warning("Please enter some information before proceeding.")
        else:
            selected_framework = framework_options[st.session_state.closing_style_label]
            if selected_framework == "AI-decides":
                bot_response = framework_agent.run_sync(prompt_to_choose_framework)
                print("bot response"+bot_response.output)
                st.session_state.framework = extract_chosen_framework(bot_response.output)
                print(st.session_state.framework)

            st.session_state.page = "chat"
            st.rerun()


tone = "Consultative"
industry = "Fintech"
buyer_profile = "CTO, mid-sized SaaS company, budget approved"
offer_details = "Enterprise API integration platform"
objective = "Secure signed contract and confirm onboarding date"
client_context = """
- Name: Sarah
- Company: FinLogix
- Deal Stage: Awaiting contract signature
- Last Objection: Concerned about integration time
- Preferred onboarding date: June 1
- Decision-maker: Sarah (CTO)
"""


if st.session_state.framework != "" and 'main_agent' not in st.session_state:
    myprompt = generate_deal_closing(
        st.session_state.framework, tone, industry, buyer_profile,
        offer_details, objective)
    st.session_state.main_agent = Agent(
        name="CloseMaster AI",
        model='openai:gpt-4o',
        system_prompt=myprompt
    )




def chat_page():
    st.title("🤖 Closing Deal Chatbot")
    st.markdown(f"### Client Information:\n{st.session_state.client_info}")
    st.markdown(f"📌 **Selected Closing Style:** {st.session_state.closing_style_label}")
    st.markdown("---")

    for sender, message in st.session_state.chat_history:
        if sender == "User":
            st.markdown(f"**You:** {message}")
        else:
            st.markdown(f"**Bot:** {message}")

    st.text_input("You:", key="input", on_change=send_message)
    resp = st.session_state.main_agent.run_sync("Start the chat")
    st.session_state.chat_history.append(("Bot", resp.output))

    if st.button("Back to Info Page"):
        st.session_state.page = "info"
        st.rerun()

# Navigation
if st.session_state.page == "info":
    info_page()
elif st.session_state.page == "chat":
    chat_page()

