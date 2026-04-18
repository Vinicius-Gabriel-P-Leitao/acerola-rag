import streamlit as st

from backend.ui._shared import api, render_bottom_nav

render_bottom_nav("admin")


def _fix_ocr_spacing(text: str) -> str:
    lines = text.split("\n")
    result = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            result.append(line)
            continue
        tokens = stripped.split(" ")
        single_char_tokens = sum(1 for t in tokens if len(t) == 1)
        if len(tokens) > 3 and single_char_tokens / len(tokens) > 0.7:
            result.append("".join(tokens))
        else:
            result.append(line)
    return "\n".join(result)


@st.dialog("Conteúdo do documento", width="large")
def _content_modal(source: str) -> None:
    st.caption(f"**{source}**")
    with st.spinner("Carregando…"):
        content_response = api("get", f"/documents/{source}/content", timeout=15)
    if not content_response or not content_response.ok:
        st.error("Não foi possível carregar o conteúdo.")
        return
    raw = content_response.json()["content"]
    cleaned = _fix_ocr_spacing(raw)
    st.text_area(
        "",
        value=cleaned,
        height=500,
        disabled=True,
        label_visibility="collapsed",
    )

# ── Upload de arquivos ────────────────────────────────────────────────────────
st.subheader("📤 Upload de documentos")

MAX_FILES = 20
st.caption(f"Formatos aceitos: PDF, Word, TXT, Markdown — máximo {MAX_FILES} arquivos")
uploaded_files = st.file_uploader(
    "Selecione os arquivos",
    type=["pdf", "docx", "doc", "txt", "md"],
    accept_multiple_files=True,
    label_visibility="collapsed",
)


def _handle_upload(files: list) -> None:
    if len(files) > MAX_FILES:
        st.error(f"❌ Selecione no máximo {MAX_FILES} arquivos por vez.")
        return
    if not st.button("🚀 Enviar para indexação"):
        return
    files_payload = [("files", (f.name, f.getvalue(), f.type)) for f in files]
    with st.spinner("Enviando arquivos…"):
        upload_response = api("post", "/upload", files=files_payload)
    if not upload_response:
        st.error("API indisponível.")
        return
    if not upload_response.ok:
        st.error(f"Erro: {upload_response.text}")
        return
    for job in upload_response.json()["jobs"]:
        st.info(f"🔄 **{job['filename']}** — job `{job['job_id']}`")


if uploaded_files:
    _handle_upload(uploaded_files)


@st.fragment(run_every="3s")
def _queue_status():
    status_response = api("get", "/upload/status")
    if not (status_response and status_response.ok):
        return
    jobs = status_response.json().get("jobs", [])
    if not jobs:
        return
    st.divider()
    st.caption("**Fila de indexação**")
    icons = {"pending": "⏳", "processing": "⚙️", "done": "✅", "error": "❌"}
    for job in jobs:
        st.caption(
            f"{icons.get(job['status'], '•')} `{job['job_id']}` "
            f"— {job['filename']} ({job['status']})"
        )
        if job["status"] == "error":
            st.caption(f"   ↳ {job['error']}")


_queue_status()

st.divider()

# ── Indexar texto puro ────────────────────────────────────────────────────────
st.subheader("📝 Indexar texto puro")
text_title = st.text_input("Título / nome do documento", placeholder="ex: fastapi-docs")
text_content = st.text_area("Conteúdo", height=150, placeholder="Cole aqui o texto…")


def _handle_index_text(title: str, content: str) -> None:
    if not title.strip():
        st.error("Informe um título.")
        return
    if not content.strip():
        st.error("Informe o conteúdo.")
        return
    with st.spinner("Indexando…"):
        index_response = api(
            "post", "/documents/text", json={"title": title, "content": content}
        )
    if not index_response:
        st.error("API indisponível.")
        return
    if not index_response.ok:
        st.error(f"Erro: {index_response.text}")
        return
    data = index_response.json()
    st.success(f"✅ Job `{data['job_id']}` criado para **{data['filename']}**")


if st.button("📥 Indexar texto"):
    _handle_index_text(text_title, text_content)

st.divider()

# ── Documentos indexados ──────────────────────────────────────────────────────
st.subheader("📚 Documentos indexados")

if "_admin_page" not in st.session_state:
    st.session_state["_admin_page"] = 1
if "_admin_search" not in st.session_state:
    st.session_state["_admin_search"] = ""

search_val = st.text_input(
    "🔍 Buscar por nome",
    value=st.session_state["_admin_search"],
    placeholder="Digite para filtrar…",
)
if search_val != st.session_state["_admin_search"]:
    st.session_state["_admin_search"] = search_val
    st.session_state["_admin_page"] = 1

PAGE_SIZE = 10
page = st.session_state["_admin_page"]

with st.spinner("Carregando documentos…"):
    docs_response = api(
        "get",
        "/documents",
        params={"page": page, "page_size": PAGE_SIZE, "search": st.session_state["_admin_search"]},
    )

if not docs_response or not docs_response.ok:
    st.error("Não foi possível carregar documentos.")
    st.stop()

data = docs_response.json()
total = data["total"]
items = data["items"]
total_pages = max(1, -(-total // PAGE_SIZE))

if total == 0:
    st.info("Nenhum documento indexado ainda.")
    st.stop()

st.caption(f"{total} documento(s) encontrado(s) — página {page}/{total_pages}")


def _render_delete_confirm(source: str) -> None:
    if not st.session_state.get(f"_confirm_{source}"):
        return
    st.warning(f"Confirma deletar **{source}** e todos seus chunks?")
    col_yes, col_no = st.columns(2)
    with col_yes:
        if not st.button("✅ Confirmar", key=f"confirm_yes_{source}"):
            return
        delete_response = api("delete", f"/documents/{source}")
        if not delete_response or not delete_response.ok:
            st.error("Erro ao deletar.")
            return
        chunks = delete_response.json()["deleted_chunks"]
        st.success(f"✅ {chunks} chunks removidos.")
        st.session_state.pop(f"_confirm_{source}", None)
        st.rerun()
    with col_no:
        if st.button("❌ Cancelar", key=f"confirm_no_{source}"):
            st.session_state.pop(f"_confirm_{source}", None)
            st.rerun()


for doc in items:
    source = doc.get("source", "")
    ftype = doc.get("file_type", "—")
    size_kb = round(doc.get("file_size_bytes", 0) / 1024, 1)
    words = doc.get("word_count", 0)
    uploaded = (doc.get("uploaded_at", "") or "")[:19].replace("T", " ")

    col_info, col_view, col_delete = st.columns([5, 1, 1])
    with col_info:
        st.markdown(
            f"**{source}** &nbsp; `{ftype}` &nbsp; {size_kb} KB"
            f" &nbsp; {words} palavras &nbsp; {uploaded}"
        )
    with col_view:
        if st.button("👁 Ver", key=f"view_{source}"):
            _content_modal(source)
    with col_delete:
        if st.button("🗑 Deletar", key=f"del_{source}"):
            st.session_state[f"_confirm_{source}"] = True

    _render_delete_confirm(source)
    st.divider()

col_prev, col_page, col_next = st.columns([1, 2, 1])
with col_prev:
    if page > 1 and st.button("← Anterior"):
        st.session_state["_admin_page"] -= 1
        st.rerun()
with col_page:
    st.caption(f"Página {page} de {total_pages}")
with col_next:
    if page < total_pages and st.button("Próxima →"):
        st.session_state["_admin_page"] += 1
        st.rerun()
