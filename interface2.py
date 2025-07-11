import streamlit as st
import io
from PIL import Image
from main import create_prompt,generate_deal_closing,extract_chosen_framework,convert_to_diagram
from pydantic_ai import Agent
import re
from graphviz import Source
import graphviz
import os

from pdf import generate_branded_pdf
import zipfile


os.environ["PATH"] += os.pathsep + r"C:\Users\dell\Downloads\Graphviz-12.2.1-win64\bin"

st.set_page_config(page_title="AI Deal Closing Script Generator", layout="centered")

st.title("🤖 AI-Powered Deal Closing Script Generator")
st.markdown("Design closing conversations tailored to your buyer and deal stage, powered by AI and backed by proven frameworks.")

# --- Framework Selector UI ---
framework_options = {
    "🔁 Auto (Recommended)": {
        "value": "Auto",
        "description": "Let the AI choose the best framework based on deal context."
    },
    "🎯 Assumptive Close": {
        "value": "Assumptive",
        "description": "Ideal when you're confident the buyer is ready to move forward."
    },
    "🤝 Summary Close": {
        "value": "Summary",
        "description": "Useful to recap benefits and reinforce alignment with buyer needs."
    },
    "📅 Urgency Close": {
        "value": "Urgency",
        "description": "Creates urgency or FOMO to push for timely decisions."
    },
    "💬 Alternative Close": {
        "value": "Alternative",
        "description": "Presents multiple win-win choices to move the deal forward."
    },
    "💼 Consultative Close": {
        "value": "Consultative",
        "description": "Perfect for B2B sales and complex solutions where value must be explored."
    },
    "📋 Checklist Close": {
        "value": "Checklist",
        "description": "Simple and effective when you want to confirm all buyer requirements are met."
    }
}

st.subheader("🎛️ Choose Closing Style")

framework_label = st.selectbox(
    "Select Framework:",
    options=list(framework_options.keys()),
    help="Pick a style or let AI choose based on your inputs."
)

framework = framework_options[framework_label]["value"]
st.caption(f"💡 **Best For:** {framework_options[framework_label]['description']}")

# --- Core Deal Context (always required) ---
st.markdown("### 📌 Core Deal Details")

industry = st.text_input("Industry", placeholder="e.g. SaaS, Healthcare, Real Estate")
buyer_persona = st.text_input("Buyer Persona", placeholder="e.g. Procurement Manager, Startup Founder")
deal_size = st.text_input(
    "Deal Size",
    placeholder="e.g. $5,000/month, $50K annually"
)

buyer_readiness = st.selectbox(
    "Buyer Readiness Stage",
    options=["Early", "Mid", "Late"],
    help="Select the buyer's current level of readiness in the decision process."
)

sales_objective = st.text_input("Sales Objective",value="Close the deal", placeholder="e.g. Get contract signed, Schedule onboarding")


# --- Tone Selection ---
tone = st.selectbox(
    "Preferred Tone",
    [
        "Assertive",
        "Consultative",
        "Friendly",
        "Professional",
        "Reassuring",
        "Warm",
        "Empathetic",
        "Neutral"
    ],
    help="Match the tone to your brand, buyer's mood, and deal stage."
)

# --- Conditional Inputs if "Auto" is selected ---
if framework == "Auto":
    st.markdown("### 🎯 Additional Info for AI Framework Selection")

    call_type = st.selectbox("Call Type", ["Cold", "Warm", "Referral"])
    region = st.text_input(
        "Regional or Cultural Considerations (Optional)",
        placeholder="e.g. Middle East business etiquette, US enterprise expectations"
    )
    more_info = st.text_area(
        "📎 Additional Deal Context (Optional)",
        placeholder="Anything else the AI should know? e.g. specific objections, buyer behavior, internal pressures, etc."
    )

else:
    call_type = region = ""

agent = Agent(
            name="CloseMaster AI",
            model='openai:gpt-4o',
        )
# --- Placeholder functions to simulate content generation ---
def generate_script_text():
    if framework == "Auto":
        prompt=create_prompt(industry, buyer_persona, deal_size, buyer_readiness, sales_objective, region)

        response=agent.run_sync(prompt)
        framework_text=extract_chosen_framework(response.output)
    else :
        framework_text=framework
    script_prompt=generate_deal_closing(framework_text,tone,industry,buyer_persona,deal_size,sales_objective)
    script=agent.run_sync(script_prompt).output
    with open("file.txt", "w", encoding="utf-8") as file:
        file.write(script)
    return script

def generate_txt_info():
    text=f"industry name:{ industry},\n" \
         f"buyer_persona:{buyer_persona},\n " \
         f"deal size:{deal_size}\n," \
         f"buyer_readiness:{buyer_readiness},\n" \
         f"sales_objective:{sales_objective},\n" \
         f"region{region},\n" \
         f"tone{tone},\n" \
         f"Call type:{call_type},\n" \
         f"Region:{region},\n" \
         f"More information:{more_info},\n"
    with open("info.txt", "w", encoding="utf-8") as file:
        file.write(text)



def render_call_script_graph(dot_code: str, format: str = "png") -> bytes:
    import tempfile
    import subprocess

    with tempfile.NamedTemporaryFile(suffix='.dot', delete=False) as tmp:
        tmp.write(dot_code.encode('utf-8'))
        tmp_path = tmp.name

    output_path = tmp_path + '.' + format

    # Use graphviz command line with explicit settings
    subprocess.run([
        'dot',
        '-T' + format,
        '-Gdpi=300',
        '-Nfontsize=12',
        '-Efontsize=10',
        tmp_path,
        '-o', output_path
    ], check=True)

    with open(output_path, 'rb') as f:
        image_bytes = f.read()

    # Clean up temporary files
    import os
    os.unlink(tmp_path)
    os.unlink(output_path)

    return image_bytes


def generate_diagram_image():
    script_text = generate_script_text()
    if not script_text or not script_text.strip():
        raise ValueError("Generated script text is empty.")

    img_prompt = convert_to_diagram(script_text)
    if not img_prompt or not img_prompt.strip():
        raise ValueError("Image prompt is empty after conversion.")

    print(f"Using image prompt: {img_prompt}")
    resp = agent.run_sync(img_prompt).output

    # Clean up the response
    if resp.startswith("```dot"):
        resp = resp[len("```dot"):].lstrip()
    if resp.endswith("```"):
        resp = resp[:-len("```")].rstrip()

    # Ensure proper graph attributes exist
    if 'graph [' not in resp:
        if resp.startswith('digraph'):
            resp = re.sub(r'digraph\s+\w*\s*\{', '''digraph {
              graph [dpi=300, size="12,8", ratio="fill"];
              node [fontsize=12, width=1.5, height=0.8];
              edge [fontsize=10];''', resp, count=1)

    image = render_call_script_graph(resp, "png")
    return image





# --- Generate Script Button ---
if st.button("🚀 Generate Deal Closing Script"):
    st.success("✅ Script input received. Now processing...")


    script_text = generate_script_text()
    generate_txt_info()
    diagram_img = generate_diagram_image()

    ##pdf_bytes = generate_pdf_bytes(script_text, diagram_img)


    st.markdown("### 📄 Script Content Preview")
    st.text_area("Generated Script", script_text, height=200)

    st.markdown("### 🖼️ Diagram Preview")
    st.image(diagram_img,
             caption="Graphviz Diagram",
             use_container_width=False,)
    # --- Download buttons ---
    st.markdown("---")
    st.subheader("📥 Download Options")

    # Download script only (text)
    st.download_button(
        label="Download Script Only (Text)",
        data=script_text,
        file_name="deal_closing_script.txt",
        mime="text/plain"
    )

    # Download diagram only (PNG)
    buf = io.BytesIO(diagram_img)
    buf.seek(0)  # rewind to start
    st.download_button(
        label="Download Diagram (PNG)",
        data=buf,
        file_name="diagram.png",
        mime="image/png"
    )

    pdf_bytes = generate_branded_pdf(
       customer_logo_path=r"C:\Users\dell\Downloads\customer.png",
        customer_name="Sarah",
        silni_logo_path=r"C:\Users\dell\Downloads\silni.png",
        title="Deal Closing Call Script",
        metadata={"objective": "Build trust and finalize deal", "framework": "L.O.C.K. Method"},
        call_script_text=script_text,
        flowchart_img=io.BytesIO(diagram_img)   # or PIL image object
    )
    #pdf_bytes=generate_pdf_bytes(script_text,diagram_img)

    st.download_button(
        label="Download Full PDF (Script + Flow Diagram)",
        data=pdf_bytes,
        file_name="deal_closing_script_full.pdf",
        mime="application/pdf"
    )

    st.markdown("You can now try a Bot!")



@st.cache_data
def get_script():
    return script_text


