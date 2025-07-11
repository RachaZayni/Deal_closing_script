from pydantic import BaseModel
from typing import List
from graphviz import Source
from pydantic_ai import Agent
#from interface import st
import os,re



# Your AI framework_agent setup



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



def create_prompt(industry, buyer_persona,deal_size, buyer_readiness, sales_objective, region_or_culture):
    prompt = f"""
You are a senior sales strategist specialized in deal closing. Given the context below, recommend the most effective closing framework:

- Industry: {industry}
- Buyer Persona: {buyer_persona}
- Deal Size: {deal_size}
- Buyer Readiness Stage: {buyer_readiness}
- Sales Objective: {sales_objective}
- Optional: {region_or_culture}

Return:
- Recommended Closing Framework
- Justification
- Optional: Backup framework(s)

"""
    return prompt






def generate_deal_closing(framework, tone, industry, buyer_persona, Deal_Size, objective):
    prompt = f"""
You are an expert sales closer. Generate a detailed deal closing script with branched logic. Follow this structure:

- Closing Objective
- Opening Statement (to start closing conversation)
- Step-by-step flow with branching:
    - Sales rep’s closing statement or question
    - 3–5 possible buyer responses
    - Tailored rep replies for each buyer response
    - Next step or branch decision
- Final Call to Action (e.g., sign contract, schedule onboarding)
- Closing tips and coaching notes

Inputs:
- Framework: {framework}
- Tone: {tone}
- Industry:{industry} / buyer_persona: {buyer_persona} / deal_size:{Deal_Size} / objective:{objective}
- Output format: branching tree

"""
    return prompt



def convert_to_diagram(script):
    prompt=f"""
    You are a diagram generation assistant.
    Convert the following deal closing script into a Graphviz DOT diagram.

Instructions:
For each step:
Create a node for the sales rep’s question or statement
Use: fillcolor="#D5E8D4", color="#82B366" (green)
For each prospect reply:
Create a child node
Use yellow for positive replies: fillcolor="#FFF2CC", color="#D6B656"
Use red for objections/negative replies: fillcolor="#F8CECC", color="#B85450"
Draw arrows to connect the sales rep’s node to each reply, and from reply to the next step
Use rankdir=TB for vertical flow
Use style=filled for all nodes

Input Structure:
script:{script}
Output:
- just A valid Graphviz DOT graph wrapped in a markdown code block

"""

    return prompt

def render_call_script_graph(dot_code: str, filename: str = "call_script", output_dir: str = "/tmp", format: str = "png") -> str:
    path = f"{output_dir}/{filename}.{format}"
    src = Source(dot_code, filename=filename, directory=output_dir, format=format)
    src.render(cleanup=True)
    return path






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
framework="The 3C Method (Clarify, Collaborate, Commit)"



#print(myprompt)
#resp = agent.run_sync("Start the chat")  # Just the trigger, not the full instruction
#print(resp.output)