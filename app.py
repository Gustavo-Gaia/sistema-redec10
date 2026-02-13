import streamlit as st

# ===== CONFIGURAÇÃO GERAL =====
st.set_page_config(
    page_title="Sistema Integrado REDEC 10 - Norte",
    page_icon="🏛️",
    layout="wide"
)

# ===== ESTADO DO MENU =====
if "menu" not in st.session_state:
    st.session_state["menu"] = "🏠 Dashboard"

# ===== SIDEBAR =====
st.sidebar.image("https://i.imgur.com/8nZPp9p.png", width=180)
st.sidebar.title("REDEC 10 - Norte")

menu = st.sidebar.radio(
    "Menu",
    [
        "🏠 Dashboard",
        "👥 Equipe REDEC 10",
        "📄 Boletins",
        "📥 SEI",
        "📅 Agenda de Atividades",
        "🌊 Monitoramento de Rios",
        "📦 Contêiner Humanitário",
        "🚑 Controle de Viaturas",
        "🏛 Municípios COMDECs",
        "🏗 Bens Patrimoniais",
        "⚙️ Configurações"
    ],
    index=[
        "🏠 Dashboard",
        "👥 Equipe REDEC 10",
        "📄 Boletins",
        "📥 SEI",
        "📅 Agenda de Atividades",
        "🌊 Monitoramento de Rios",
        "📦 Contêiner Humanitário",
        "🚑 Controle de Viaturas",
        "🏛 Municípios COMDECs",
        "🏗 Bens Patrimoniais",
        "⚙️ Configurações"
    ].index(st.session_state["menu"])
)

st.session_state["menu"] = menu

# ===== HEADER =====
st.markdown("""
    <div style="background:linear-gradient(90deg,#1f4c81,#1b2e4b);
                padding:15px;
                border-radius:10px;
                color:white;">
        <h2>Sistema Integrado REDEC 10 - Norte</h2>
        <p>Defesa Civil - Governo do Estado</p>
    </div>
""", unsafe_allow_html=True)

st.write("")

# ===== FUNÇÃO CARD =====
def card(titulo, valor, icone, cor, destino):
    st.markdown(f"""
        <div style="background:{cor};
                    padding:20px;
                    border-radius:12px;
                    color:white;
                    box-shadow:0 4px 10px rgba(0,0,0,0.15);
                    margin-bottom:15px;">
            <h4>{icone} {titulo}</h4>
            <h2>{valor}</h2>
        </div>
    """, unsafe_allow_html=True)

    if st.button(f"Abrir {titulo}", key=destino):
        st.session_state["menu"] = destino
        st.rerun()

# ===== DASHBOARD =====
if menu == "🏠 Dashboard":

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        card("Monitoramento dos Rios", "3 em atenção", "🌊", "#2E8B57", "🌊 Monitoramento de Rios")

    with col2:
        card("Boletins", "5 pendentes", "📄", "#1E5AA8", "📄 Boletins")

    with col3:
        card("Equipe REDEC 10", "12 membros", "👥", "#D97925", "👥 Equipe REDEC 10")

    with col4:
        card("Ocorrências", "5 municípios", "⚠️", "#C0392B", "🏛 Municípios COMDECs")

    st.divider()

    col5, col6, col7, col8 = st.columns(4)

    with col5:
        card("Agenda", "8 atividades", "📅", "#34495E", "📅 Agenda de Atividades")

    with col6:
        card("Contêiner", "Estoque OK", "📦", "#5D6D7E", "📦 Contêiner Humanitário")

    with col7:
        card("Viaturas", "12 ativos", "🚑", "#273746", "🚑 Controle de Viaturas")

    with col8:
        card("Patrimônio", "145 itens", "🏗", "#7D3C98", "🏗 Bens Patrimoniais")

# ===== MÓDULOS =====
elif menu == "👥 Equipe REDEC 10":
    from pages.equipe import tela_equipe
    tela_equipe()

elif menu == "📄 Boletins":
    from pages.boletins import tela_boletins
    tela_boletins()

elif menu == "📥 SEI":
    from pages.sei import tela_sei
    tela_sei()

elif menu == "📅 Agenda de Atividades":
    from pages.agenda import tela_agenda
    tela_agenda()

elif menu == "🌊 Monitoramento de Rios":
    from pages.rios import tela_rios
    tela_rios()

elif menu == "📦 Contêiner Humanitário":
    from pages.container import tela_container
    tela_container()

elif menu == "🚑 Controle de Viaturas":
    from pages.viaturas import tela_viaturas
    tela_viaturas()

elif menu == "🏛 Municípios COMDECs":
    from pages.comdecs import tela_comdecs
    tela_comdecs()

elif menu == "🏗 Bens Patrimoniais":
    from pages.patrimonio import tela_patrimonio
    tela_patrimonio()

elif menu == "⚙️ Configurações":
    st.subheader("Configurações")
    st.info("Em desenvolvimento")
