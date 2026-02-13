# pages/equipe.py

import streamlit as st
from services.supabase import buscar_equipe, inserir_membro

def tela_equipe():

    st.subheader("👥 Gestão da Equipe - REDEC 10")

    aba1, aba2, aba3, aba4 = st.tabs([
        "📋 Lista Geral",
        "➕ Novo Cadastro",
        "🏖 Férias / Licenças",
        "📊 Relatórios"
    ])

    # =================== LISTA ===================
    with aba1:
        dados = buscar_equipe()

        if not dados:
            st.warning("Nenhum membro cadastrado.")
        else:
            st.dataframe(dados, use_container_width=True)

    # =================== CADASTRO ===================
    with aba2:
        st.markdown("### Novo Membro")

        with st.form("form_membro"):
            nome = st.text_input("Nome completo")
            nome_guerra = st.text_input("Nome de guerra")
            rg = st.text_input("RG")
            id_funcional = st.text_input("ID Funcional")
            posto = st.text_input("Posto / Graduação")
            quadro = st.text_input("Quadro / QBMP")
            telefone = st.text_input("Telefone")

            salvar = st.form_submit_button("Salvar")

        if salvar:
            dados = {
                "nome": nome,
                "nome_guerra": nome_guerra,
                "rg": rg,
                "id_funcional": id_funcional,
                "posto_graduacao": posto,
                "quadro_qbmp": quadro,
                "telefone": telefone
            }

            inserir_membro(dados)

            st.success("Membro cadastrado com sucesso!")
            st.rerun()

    # =================== FERIAS ===================
    with aba3:
        st.info("Controle de férias e licenças — vamos montar no próximo passo")

    # =================== RELATÓRIOS ===================
    with aba4:
        st.info("Relatórios automáticos — vamos montar no próximo passo")

