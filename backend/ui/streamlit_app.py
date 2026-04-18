import sys
from pathlib import Path

_root = Path(__file__).parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import streamlit as st

st.set_page_config(page_title="Acerola RAG", page_icon="🍊", layout="wide")
st.title("🍊 Acerola RAG")
st.caption("Chat com sua documentação técnica de programação")

chat_page = st.Page("chat.py", title="Chat", icon="💬", default=True)
admin_page = st.Page("admin.py", title="Admin", icon="⚙️")

pg = st.navigation([chat_page, admin_page])
pg.run()
