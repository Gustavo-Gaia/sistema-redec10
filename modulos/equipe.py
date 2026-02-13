# pages/equipe.py

import streamlit as st
import pandas as pd
from services.supabase import buscar_equipe, inserir_membro
from services.ferias import buscar_ferias, inserir_ferias
from services.historico import buscar_historico, trocar_funcao

# ============================================================
# TELA PRINCIPAL EQUIPE
# ============================================================

def tela_equipe():

    st.subheader("👥 Gestão da Equipe - REDEC 10")

    aba1, aba2, aba3, aba4, aba5 = st.tabs([
        "🧭 Painel da Equipe",
        "➕ Cadastro & Gestão",
        "🔁 Funções & Substituições",
        "🏖 Férias / Licenças",
        "📊 Relatórios"
    ])

    # ============================================================
    # PAINEL ATUAL
    # ============================================================
    with aba1:
        st.markdown("### 🧭 Composição Atual da REDEC 10")

        historico = buscar_historico()

        if not historico:
            st.warning("Nenhuma função cadastrada ainda.")
            return

        df = pd.DataFrame(historico)
        df = df[df["data_saida"].isna()]

        cargos_unicos = ["Coordenador", "Subcoordenador"]
        cargos_multiplos = ["Oficial Administrativo", "Praça Administrativo"]

        col1, col2, col3, col4 = st.columns(4)

        for i, cargo in enumerate(cargos_unicos + cargos_multiplos):
            ocupantes = df[df["funcao"] == cargo]

            nomes = ", ".join(ocupantes["equipe"]["nome"]) if not ocupantes.empty else "Vago"

            with [col1, col2, col3, col4][i]:
                st.markdown(f"""
                <div style="background:#1f4c81;padding:18px;border-radius:14px;color:white;text-align:center;">
                    <h5>{cargo}</h5>
                    <h4>{nomes}</h4>
                </div>
                """, unsafe_allow_html=True)

    # ============================================================
    # CADASTRO
    # ============================================================
    with aba2:
        col1, col2 = st.columns([1,2])

        with col1:
            st.markdown("### ➕ Novo Membro")

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
                inserir_membro({
                    "nome": nome,
                    "nome_guerra": nome_guerra,
                    "rg": rg,
                    "id_funcional": id_funcional,
                    "posto_graduacao": posto,
                    "quadro_qbmp": quadro,
                    "telefone": telefone
                })
                st.success("Membro cadastrado com sucesso!")
                st.rerun()

        with col2:
            st.markdown("### 📋 Lista Geral")

            dados = buscar_equipe()
            if dados:
                st.dataframe(pd.DataFrame(dados), use_container_width=True)

    # ============================================================
    # FUNÇÕES
    # ============================================================
    with aba3:
        st.markdown("### 🔁 Registro de Funções")

        equipe = buscar_equipe()
        nomes = {m["nome"]: m["id"] for m in equipe}

        funcao = st.selectbox("Função", [
            "Coordenador",
            "Subcoordenador",
            "Oficial Administrativo",
            "Praça Administrativo"
        ])

        pessoa = st.selectbox("Servidor", nomes.keys())
        data = st.date_input("Data de entrada")

        st.info("Coordenador e Subcoordenador possuem apenas 1 vaga. As demais funções permitem múltiplos ocupantes.")

        if st.button("Registrar Função"):
            trocar_funcao(nomes[pessoa], funcao, data)
            st.success("Função registrada com sucesso!")
            st.rerun()

    # ============================================================
    # FÉRIAS
    # ============================================================
    with aba4:
        st.markdown("### 🏖 Controle de Férias / Licenças")

        equipe = buscar_equipe()
        nomes = {m["nome"]: m["id"] for m in equipe}

        with st.form("form_ferias"):
            pessoa = st.selectbox("Servidor", nomes.keys())
            tipo = st.selectbox("Tipo", ["Férias", "Licença Médica", "Licença Prêmio", "Outros"])
            inicio = st.date_input("Data início")
            fim = st.date_input("Data fim")
            obs = st.text_area("Observação")

            salvar = st.form_submit_button("Registrar")

        if salvar:
            inserir_ferias({
                "equipe_id": nomes[pessoa],
                "tipo": tipo,
                "inicio": str(inicio),
                "fim": str(fim),
                "observacao": obs
            })
            st.success("Registro salvo!")
            st.rerun()

        registros = buscar_ferias()
        if registros:
            st.dataframe(pd.DataFrame(registros), use_container_width=True)

    # ============================================================
    # RELATÓRIOS
    # ============================================================
    with aba5:
        st.markdown("### 📊 Relatórios Gerenciais")

        equipe = buscar_equipe()
        historico = buscar_historico()

        df = pd.DataFrame(equipe)
        ativos = df[df["ativo"] == True]

        col1, col2 = st.columns(2)
        col1.metric("Total", len(df))
        col2.metric("Ativos", len(ativos))

        st.divider()

        st.subheader("Histórico de Coordenadores")

        dfh = pd.DataFrame(historico)
        coord = dfh[dfh["funcao"] == "Coordenador"]

        st.dataframe(coord, use_container_width=True)



