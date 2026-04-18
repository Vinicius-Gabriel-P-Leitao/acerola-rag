import streamlit as st

from backend.ui._shared import api, render_bottom_nav, render_model_popover

render_bottom_nav("chat")


@st.fragment(run_every="10s")
def _settings_banner():
    settings_response = api("get", "/settings")
    if not (settings_response and settings_response.ok):
        return
    if settings_response.json().get("configured"):
        return
    st.error(
        "⚠️ **Modelo não configurado.** "
        "A API key do provider selecionado não foi encontrada no `.env`."
    )


def _resolve_answer(response) -> str:
    if response is None:
        return "❌ API indisponível."
    if response.status_code == 422:
        return "⚠️ " + response.json().get("detail", "Modelo não configurado.")
    if response.ok:
        return response.json()["answer"]
    return f"Erro ({response.status_code}): {response.text}"


_settings_banner()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

_, col_model = st.columns([8, 2])
with col_model:
    render_model_popover()

if prompt := st.chat_input("Faça uma pergunta sobre a documentação…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("▌")
        with st.spinner(""):
            query_response = api("post", "/query", json={"question": prompt}, timeout=60)
        answer = _resolve_answer(query_response)
        placeholder.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
