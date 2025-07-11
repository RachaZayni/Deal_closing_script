# 🤖 AI Deal Closing Assistant Suite

This project is a modular, AI-powered sales assistant suite built with **Streamlit** and **Pydantic AI**. It enables users to generate persuasive deal-closing scripts, visualize sales conversations, and interact with a smart chatbot trained to follow proven sales frameworks.

---

## 📁 Project Structure

### `interface2.py` – Script Generator + Diagram Exporter
- Collects deal details (industry, persona, readiness, tone, etc.)
- Uses OpenAI to auto-select or apply a user-chosen closing framework
- Generates personalized deal-closing scripts
- Converts the script into a Graphviz diagram
- Allows downloading:
  - 📄 Text script (`.txt`)
  - 🖼️ Diagram image (`.png`)
  - 📘 Branded PDF (script + flow diagram)

### `interface.py` – Client Info & Smart Chat Launcher
- Collects client information and objections
- Offers AI-guided framework selection or manual selection
- Starts a chat interface based on the generated script and context

### `chat.py` – Live Sales Chatbot
- Loads generated script and customer/product data
- Simulates a real-time sales conversation
- Follows provided script logic
- Includes a Corrector Agent that refines AI responses dynamically

---

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run an app**
   ```bash
   streamlit run interface2.py
   ```
   or
   ```bash
   streamlit run chat.py
   ```

---

## 📦 Required Files for Chatbot

Before running `chat.py`, ensure these files exist in the project directory:

- `file.txt` – Generated deal-closing script (created by `interface2.py`)
- `info.txt` – Deal metadata (industry, buyer persona, tone, etc.)
- `Product_data.txt` – Product-related information
- `customer_data.txt` – Customer background information

---

## 🔍 Features

- ✅ **Framework Selector**: Choose from methods like Assumptive, Consultative, Urgency, etc.
- 🧠 **AI-Driven Script Generator**: Personalized scripts using GPT-4o
- 📊 **Flowchart Visualizer**: Converts conversation logic into a downloadable diagram
- 🤖 **Sales Chatbot**: Live, realistic conversation simulation with objection handling and correction
- 📎 **PDF Export**: Branded PDF including the script and visual flow

---

## 💡 Technologies Used

- [Streamlit](https://streamlit.io/)
- [OpenAI API](https://openai.com/)
- [Pydantic AI](https://github.com/)
- [Graphviz](https://graphviz.org/)
- [Pillow (PIL)](https://python-pillow.org/)
- [ReportLab](https://www.reportlab.com/)

---

## 🧑‍💻 Author

**Racha Zayni**  
Electrical and Technology Engineering Student  
Passionate about AI, automation, and human-centered sales enablement.

---

## 📜 License

This project is for academic and internal use only.  
For commercial licensing or customization, please contact the author.
