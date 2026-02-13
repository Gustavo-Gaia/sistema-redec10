import streamlit as st

st.set_page_config(
    page_title="Sistema Integrado REDEC 10",
    layout="wide",
    initial_sidebar_state="expanded"
)

# SIDEBAR
st.sidebar.image("assets/logo.png", use_column_width=True)

menu = st.sidebar.radio(
    "Menu",
    [
        "🏠 Dashboard",
        "🌊 Rios",
        "🚨 Ocorrências",
        "📥 SEI",
        "📰 Boletins",
        "👥 Equipe",
        "🚗 Viaturas",
        "📦 Patrimônio",
        "🧃 Contêiner",
        "🗓 Agenda",
        "🏛 COMDECs",
        "⚙️ Configurações"
    ]
)

st.title(menu)

if menu == "👥 Equipe":
    from pages.equipe import tela_equipe
    tela_equipe()
else:
    st.info("Módulo em desenvolvimento")
