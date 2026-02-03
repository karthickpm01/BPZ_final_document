import os
import sqlite3
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# 1. LOAD ENVIRONMENT & CONFIG
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'bpz_brutal_dev_2026')
DB_PATH = "database.db"


# 2. DATABASE INIT
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS message_store (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                session_id TEXT, 
                message JSON
            )
        ''')


init_db()

# 3. AI ENGINE CONFIGURATION
llm = ChatOpenAI(model="gpt-4o", temperature=0)


def get_bpz_chain():
    # UPDATE ONLY THE SYSTEM SECTION IN get_bpz_chain()
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Role: You are the official Build Planet Zero (BPZ) AI Assistant. 

        STRICT FORMATTING:
        - DOUBLE-SPACING: One empty line between every paragraph.
        - VERTICAL LISTS: Never items on the same line.
        - BOLDING: Names, Titles, and Tech Terms**.

        Knowledge Base - Company Specialties:
        - Sustainable Construction: We replace high-carbon traditional materials with bio-based alternatives like hempcrete to achieve carbon neutrality.

        - Modular Innovation : We develop modular building systems that are scalable, efficient, and significantly reduce construction waste.

        - Digital Transformation : We use advanced data analytics and digital platforms to track carbon metrics and optimize building performance.

        Knowledge Base - The Team:
        - Dr. Xiaohong Chen (Founder & CEO): Visionary leader in Newcastle upon Tyne focusing on bio-based material strategy.

        - Karthick P M (Tech Developer): Architect of the BPZ digital ecosystem and scalable software platforms.

        - Dr. Siliang Yang (Technical Director): Leads R&D for hempcrete modular systems and structural safety.
        "Knowledge Base - Location: Build Planet Zero is proudly based in Newcastle upon Tyne, UK."
        
        Constraint: If a user asks about BPZ specialties, projects, or team, provide a detailed 3-4 sentence response. If unrelated, say: "I am only programmed to discuss Build Planet Zero and sustainable construction." """),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
    ])

    return RunnableWithMessageHistory(
        prompt | llm,
        lambda sid: SQLChatMessageHistory(session_id=sid, connection_string=f"sqlite:///{DB_PATH}"),
        input_messages_key="input",
        history_messages_key="chat_history"
    )


# 4. CHAT API ROUTE (THE MISSING LINK)
@app.route('/chat_api', methods=['POST'])
def chat_api():
    # Ensure a session ID exists to keep track of memory
    if 'chat_sid' not in session:
        import uuid
        session['chat_sid'] = str(uuid.uuid4())

    data = request.json
    user_input = data.get("message", "")

    if not user_input:
        return jsonify({"reply": "I didn't receive a question."}), 400

    try:
        chain = get_bpz_chain()
        config = {"configurable": {"session_id": session['chat_sid']}}

        # Invoke the AI
        response = chain.invoke({"input": user_input}, config=config)

        return jsonify({"reply": response.content})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"reply": "I'm having trouble connecting to my brain right now."}), 500


# 5. MAIN ROUTES
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login(): return render_template('login.html')


@app.route('/project/wallsend')
def project_wallsend(): return render_template('project-wallsend.html')


@app.route('/project/west-end')
def project_west_end(): return render_template('west-end-newcastle.html')


@app.route('/project/rowlands')
def project_rowlands(): return render_template('rowlands-eco-village.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)