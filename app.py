"""
app.py — UAE Government Services Assistant
Pure Streamlit UI. All AI/retrieval logic lives in agent.py.
"""
import base64
import streamlit as st
# ── Import everything from the agent layer ──────────────────
from agent import (
    load_knowledge_base,
    build_retrieval_index,
    retrieve_context,
    get_gemini_model,
    start_chat_session,
    generate_greeting,
    generate_grounded_response,
)
# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="UAE Gov Services AI Assistant",
    page_icon="🇦🇪",
    layout="wide",
)
# ─────────────────────────────────────────────
# LOAD BACKEND (DO NOT TOUCH LOGIC)
# ─────────────────────────────────────────────
kb_data = load_knowledge_base()
vectorizer, tfidf_matrix = build_retrieval_index(kb_data)
# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None
# ─────────────────────────────────────────────
# SIDEBAR (CONFIG + SOURCES)
# ─────────────────────────────────────────────
with st.sidebar:
    st.title("🇦🇪 UAE Gov Assistant")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.markdown("---")
    st.markdown("### 🔗 Official Sources")
    st.markdown("- https://u.ae")
    st.markdown("- https://icp.gov.ae")
    st.markdown("- https://gdrfad.gov.ae")
    st.markdown("- https://rta.ae")
    st.markdown("- https://mohre.gov.ae")
    st.markdown("---")
    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.session_state.chat_session = None
        st.rerun()
# ─────────────────────────────────────────────
# INITIALIZE GEMINI SESSION
# ─────────────────────────────────────────────
if api_key and st.session_state.chat_session is None:
    model = get_gemini_model(api_key)
    st.session_state.chat_session = start_chat_session(model)
    greeting = generate_greeting(st.session_state.chat_session)
    st.session_state.messages.append({
        "role": "assistant",
        "content": greeting,
        "sources": []
    })
# ─────────────────────────────────────────────
# HEADER (UAE STYLE)
# ─────────────────────────────────────────────
st.markdown("""
<div style="
    background: linear-gradient(90deg,#0B1F3B,#0F766E);
    padding: 18px;
    border-radius: 14px;
    color: white;
    font-size: 20px;
    font-weight: bold;
">
🇦🇪 UAE Government Services Assistant (Prototype)
</div>
""", unsafe_allow_html=True)
st.warning("⚠️ Prototype only — Not an official UAE government service. Always verify on official portals.")
# ─────────────────────────────────────────────
# QUICK ACTION BUTTONS
# ─────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
if col1.button("🛂 Visa"):
    user_input = "What are UAE visa types and requirements?"
elif col2.button("🚗 License"):
    user_input = "How to get or convert driving license in UAE?"
elif col3.button("🏢 Business"):
    user_input = "How to get a business license in UAE?"
elif col4.button("❓ FAQ"):
    user_input = "General UAE government services help"
else:
    user_input = None
# ─────────────────────────────────────────────
# CHAT DISPLAY (CLEAN UI BUBBLES)
# ─────────────────────────────────────────────
st.markdown("### 💬 Chat Assistant")
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div style="
            text-align:right;
            background:#0B1F3B;
            color:white;
            padding:10px 14px;
            border-radius:12px;
            margin:6px 0;
            display:inline-block;
            float:right;
            clear:both;
            max-width:80%;
        ">
        {msg["content"]}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="
            text-align:left;
            background:#F1F5F9;
            color:#111;
            padding:10px 14px;
            border-radius:12px;
            margin:6px 0;
            display:inline-block;
            float:left;
            clear:both;
            max-width:80%;
        ">
        {msg["content"]}
        </div>
        """, unsafe_allow_html=True)
# ─────────────────────────────────────────────
# INPUT BOX
# ─────────────────────────────────────────────
chat_input = st.chat_input("Ask about UAE visas, licenses, business setup...")
# handle quick buttons OR chat input
final_input = chat_input or user_input
if final_input and api_key:
    # add user message
    st.session_state.messages.append({
        "role": "user",
        "content": final_input
    })
    # retrieve context
    matched_docs, context_string = retrieve_context(
        final_input,
        vectorizer,
        tfidf_matrix,
        kb_data
    )
    # generate AI response
    reply = generate_grounded_response(
        final_input,
        context_string,
        st.session_state.chat_session
    )
    # add assistant message
    st.session_state.messages.append({
        "role": "assistant",
        "content": reply,
        "sources": matched_docs
    })
    st.rerun()
elif final_input and not api_key:
    st.error("Please enter Gemini API key in sidebar first.")
# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
"""
🏛️ UAE Gov Services Assistant Prototype  
Not affiliated with UAE government — Always verify on official portals
"""
)
