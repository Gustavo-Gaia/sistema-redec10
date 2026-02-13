import streamlit as st
import streamlit as st

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

st.set_page_config(
    page_title="Sistema Integrado REDEC 10 - Norte",
    page_icon="🏛️",
    layout="wide"
)

# ===== SIDEBAR =====
st.sidebar.title("REDEC 10 - Norte")

menu = st.sidebar.radio(
    "Menu",
    [
        "🏠 Dashboard",
        "👥 Equipe",
        "⚙️ Configurações"
    ]
)

# ===== HEADER =====
st.title("Sistema Integrado REDEC 10 - Norte")
st.caption("Defesa Civil - Governo do Estado")

st.divider()

# ===== CONTEÚDO =====
if menu == "🏠 Dashboard":
    st.subheader("Painel Geral")
    st.info("Dashboard em construção")

elif menu == "👥 Equipe":
    from services.supabase import buscar_equipe

    st.subheader("👥 Gestão da Equipe - REDEC 10")

    tab1, tab2 = st.tabs(["📋 Lista", "➕ Novo Cadastro"])

    # ===== LISTA =====
    with tab1:
        dados = buscar_equipe()

        if not dados:
            st.warning("Nenhum membro cadastrado.")
        else:
            st.dataframe(dados, use_container_width=True)

    # ===== CADASTRO =====
    with tab2:
        st.subheader("Novo Membro")

        with st.form("form_novo_membro"):
            nome = st.text_input("Nome completo")
            nome_guerra = st.text_input("Nome de guerra")
            rg = st.text_input("RG")
            id_funcional = st.text_input("ID Funcional")
            posto = st.text_input("Posto / Graduação")
            quadro = st.text_input("Quadro / QBMP")
            telefone = st.text_input("Telefone")

            salvar = st.form_submit_button("Salvar")

        if salvar:
            st.success("Formulário enviado (em breve salvaremos no banco)")


elif menu == "⚙️ Configurações":
    st.subheader("Configurações do Sistema")
    st.info("Em breve")
