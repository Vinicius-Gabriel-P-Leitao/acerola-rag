import os

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")

PROVIDER_LABELS = {
    "openai": "OpenAI",
    "ollama": "Ollama (local)",
    "gemini": "Google Gemini",
    "claude": "Anthropic Claude",
}

PROVIDER_MODELS = {
    "openai": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "o3-mini"],
    "ollama": ["llama3.2", "mistral", "codellama", "qwen2.5"],
    "gemini": [
        "gemini-3-flash-preview",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
    ],
    "claude": ["claude-sonnet-4-6", "claude-haiku-4-5-20251001", "claude-opus-4-7"],
}

_RESPONSIVE_CSS = """
<style>
/* ── Mobile: hide sidebar, add bottom padding ──────────────────── */
@media (max-width: 768px) {
    section[data-testid="stSidebar"] { display: none !important; }
    .main .block-container { padding-bottom: 72px !important; }
}

/* ── Bottom navigation bar ──────────────────────────────────────── */
.bnav {
    display: none;
    position: fixed;
    bottom: 0; left: 0; right: 0;
    height: 56px;
    background: white;
    border-top: 1px solid rgba(49,51,63,.15);
    z-index: 9999;
    box-shadow: 0 -2px 8px rgba(0,0,0,.06);
}
@media (max-width: 768px) { .bnav { display: flex !important; } }
.bnav a {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-decoration: none;
    color: rgba(49,51,63,.5);
    font-size: 11px;
    gap: 2px;
    transition: color .15s;
}
.bnav a .ni { font-size: 20px; line-height: 1; }
.bnav a.active {
    color: var(--primary-color, #ff4b4b);
    font-weight: 600;
}
</style>
"""


def api(method: str, path: str, **kwargs):
    kwargs.setdefault("timeout", 30)
    try:
        return getattr(requests, method)(f"{API_URL}{path}", **kwargs)
    except requests.exceptions.ConnectionError:
        return None


def _apply_settings(provider: str, model: str) -> None:
    response = api("post", "/settings", json={"llm_provider": provider, "llm_model": model})
    if response and response.ok and not response.json().get("configured"):
        st.session_state["_settings_error"] = (
            f"API key para **{PROVIDER_LABELS[provider]}** não encontrada no .env."
        )
        return
    st.session_state.pop("_settings_error", None)


def _on_provider_change() -> None:
    provider = st.session_state["_provider"]
    st.session_state["_model"] = PROVIDER_MODELS[provider][0]
    _apply_settings(provider, PROVIDER_MODELS[provider][0])


def _on_model_change() -> None:
    _apply_settings(st.session_state["_provider"], st.session_state["_model"])


def _init_session_from_api() -> None:
    with st.spinner("Conectando…"):
        settings_response = api("get", "/settings")
    if not (settings_response and settings_response.ok):
        st.session_state.setdefault("_provider", "openai")
        st.session_state.setdefault("_model", PROVIDER_MODELS["openai"][0])
        return
    data = settings_response.json()
    st.session_state.setdefault("_provider", data.get("provider", "openai"))
    st.session_state.setdefault("_model", data.get("model", PROVIDER_MODELS["openai"][0]))


def render_bottom_nav(current: str) -> None:
    chat_class = "active" if current == "chat" else ""
    admin_class = "active" if current == "admin" else ""
    st.markdown(_RESPONSIVE_CSS, unsafe_allow_html=True)
    st.markdown(
        f'<nav class="bnav">'
        f'<a href="/" class="{chat_class}"><span class="ni">💬</span>Chat</a>'
        f'<a href="/admin" class="{admin_class}"><span class="ni">⚙️</span>Admin</a>'
        f"</nav>",
        unsafe_allow_html=True,
    )


def render_model_popover() -> None:
    if "_provider" not in st.session_state or "_model" not in st.session_state:
        _init_session_from_api()

    model_label = st.session_state.get("_model", "modelo")
    with st.popover(f"🤖 {model_label}"):
        st.selectbox(
            "Provider",
            options=list(PROVIDER_MODELS.keys()),
            format_func=lambda p: PROVIDER_LABELS[p],
            key="_provider",
            on_change=_on_provider_change,
        )
        model_options = PROVIDER_MODELS[st.session_state["_provider"]]
        if st.session_state["_model"] not in model_options:
            st.session_state["_model"] = model_options[0]
        st.selectbox(
            "Modelo",
            options=model_options,
            key="_model",
            on_change=_on_model_change,
        )
        if err := st.session_state.get("_settings_error"):
            st.error(f"❌ {err}")


def render_model_sidebar() -> None:
    if "_provider" not in st.session_state or "_model" not in st.session_state:
        _init_session_from_api()

    with st.sidebar:
        st.header("⚙️ Modelo")
        st.selectbox(
            "Provider",
            options=list(PROVIDER_MODELS.keys()),
            format_func=lambda p: PROVIDER_LABELS[p],
            key="_provider",
            on_change=_on_provider_change,
        )

        current_provider = st.session_state["_provider"]
        model_options = PROVIDER_MODELS[current_provider]
        if st.session_state["_model"] not in model_options:
            st.session_state["_model"] = model_options[0]

        st.selectbox(
            "Modelo",
            options=model_options,
            key="_model",
            on_change=_on_model_change,
        )

        if err := st.session_state.get("_settings_error"):
            st.error(f"❌ {err}")
