# pages/equipe.py

import streamlit as st
import pandas as pd
from services.supabase import buscar_equipe, inserir_membro
from services.ferias import (
    buscar_ferias,
    inserir_ferias
)
from services.historico import (
    buscar_historico,
    inserir_historico
)

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
            df = pd.DataFrame(dados)

            st.metric("Total de Membros", len(df))

            st.dataframe(df, use_container_width=True)

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
        st.markdown("### Controle de Férias / Licenças")

        membros = buscar_equipe()

        if not membros:
            st.warning("Cadastre membros antes.")
        else:
            nomes = {m["nome"]: m["id"] for m in membros}

            with st.form("form_ferias"):
                pessoa = st.selectbox("Servidor", nomes.keys())
                tipo = st.selectbox("Tipo", ["Férias", "Licença Médica", "Licença Prêmio", "Outros"])
                inicio = st.date_input("Data de início")
                fim = st.date_input("Data final")
                obs = st.text_area("Observação")

                salvar = st.form_submit_button("Registrar")

            if salvar:
                dados = {
                    "equipe_id": nomes[pessoa],
                    "tipo": tipo,
                    "inicio": str(inicio),
                    "fim": str(fim),
                    "observacao": obs
                }

                inserir_ferias(dados)

                st.success("Registro salvo com sucesso!")
                st.rerun()

        ferias = buscar_ferias()

        if ferias:
            st.dataframe(pd.DataFrame(ferias), use_container_width=True)

    # =================== RELATORIOS ===================
    with aba4:
        st.markdown("### Relatórios da Equipe")

        dados = buscar_equipe()

        if not dados:
            st.warning("Sem dados.")
        else:
            df = pd.DataFrame(dados)

            ativos = df[df["ativo"] == True]
            inativos = df[df["ativo"] == False]

            col1, col2, col3 = st.columns(3)

            col1.metric("Total", len(df))
            col2.metric("Ativos", len(ativos))
            col3.metric("Inativos", len(inativos))

            st.divider()

            st.subheader("Lista de Ativos")
            st.dataframe(ativos, use_container_width=True)
