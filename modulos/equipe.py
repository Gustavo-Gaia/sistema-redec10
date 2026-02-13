# pages/equipe.py

import streamlit as st
import pandas as pd

from services.supabase import (
    buscar_equipe,
    inserir_membro,
    atualizar_membro,
    excluir_membro
)

from services.ferias import buscar_ferias, inserir_ferias
from services.historico import buscar_historico, trocar_funcao


# ============================================================
# TELA PRINCIPAL
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
    # PAINEL DA EQUIPE
    # ============================================================
    with aba1:

        st.markdown("### 🧭 Composição Atual da REDEC 10")

        historico = buscar_historico()

        if not historico:
            st.info("Nenhuma função cadastrada ainda.")
            return

        df = pd.DataFrame(historico)

        df = df[df["data_saida"].isna()]
        df["nome"] = df["equipe"].apply(lambda x: x.get("nome") if isinstance(x, dict) else "")

        cargos = {
            "Coordenador": [],
            "Subcoordenador": [],
            "Oficial Administrativo": [],
            "Praça Administrativo": []
        }

        for _, row in df.iterrows():
            cargos[row["funcao"]].append(row["nome"])

        col1, col2, col3, col4 = st.columns(4)

        def render_card(titulo, nomes):
            nomes = "<br>".join(nomes) if nomes else "Vago"
            st.markdown(f"""
            <div style="background:#1f4c81;
                        padding:18px;
                        border-radius:14px;
                        color:white;
                        text-align:center;
                        min-height:120px">
                <h5>{titulo}</h5>
                <h4>{nomes}</h4>
            </div>
            """, unsafe_allow_html=True)

        with col1:
            render_card("Coordenador", cargos["Coordenador"])
        with col2:
            render_card("Subcoordenador", cargos["Subcoordenador"])
        with col3:
            render_card("Oficial Administrativo", cargos["Oficial Administrativo"])
        with col4:
            render_card("Praça Administrativo", cargos["Praça Administrativo"])

        st.divider()
        st.subheader("📜 Histórico Funcional")

        dfh = pd.DataFrame(historico)
        dfh["Servidor"] = dfh["equipe"].apply(lambda x: x.get("nome") if isinstance(x, dict) else "")

        dfh = dfh[["Servidor", "funcao", "data_entrada", "data_saida"]]
        dfh.columns = ["Servidor", "Função", "Entrada", "Saída"]

        st.dataframe(dfh.sort_values("Entrada", ascending=False),
                     use_container_width=True, hide_index=True)

    # ============================================================
    # CADASTRO & GESTÃO
    # ============================================================
    with aba2:

        st.markdown("### 👤 Cadastro de Novo Servidor")

        with st.form("novo_membro"):
            nome = st.text_input("Nome completo")
            nome_guerra = st.text_input("Nome de guerra")
            rg = st.text_input("RG")
            id_funcional = st.text_input("ID Funcional")
            posto = st.text_input("Posto / Graduação")
            quadro = st.text_input("Quadro / QBMP")
            telefone = st.text_input("Telefone")

            salvar = st.form_submit_button("Cadastrar")

        if salvar:
            inserir_membro({
                "nome": nome,
                "nome_guerra": nome_guerra,
                "rg": rg,
                "id_funcional": id_funcional,
                "posto_graduacao": posto,
                "quadro_qbmp": quadro,
                "telefone": telefone,
                "ativo": True
            })
            st.success("Servidor cadastrado com sucesso!")
            st.rerun()

        st.divider()
        st.markdown("### 📋 Gestão da Equipe")

        equipe = buscar_equipe()

        if not equipe:
            st.info("Nenhum servidor cadastrado.")
        else:
            df = pd.DataFrame(equipe)

            df_view = df[["id", "nome", "posto_graduacao", "quadro_qbmp", "telefone"]]
            df_view.columns = ["ID", "Nome", "Posto", "Quadro", "Telefone"]

            st.dataframe(df_view, hide_index=True, use_container_width=True)

            st.divider()
            st.markdown("### ✏️ Editar / Excluir")

            selecionado = st.selectbox("Selecionar servidor", df["nome"])

            registro = df[df["nome"] == selecionado].iloc[0]

            col1, col2 = st.columns(2)

            with col1:
                nome_edit = st.text_input("Nome", registro["nome"])
                posto_edit = st.text_input("Posto", registro["posto_graduacao"])
                quadro_edit = st.text_input("Quadro", registro["quadro_qbmp"])
                tel_edit = st.text_input("Telefone", registro["telefone"])

                if st.button("Atualizar dados"):
                    atualizar_membro(registro["id"], {
                        "nome": nome_edit,
                        "posto_graduacao": posto_edit,
                        "quadro_qbmp": quadro_edit,
                        "telefone": tel_edit
                    })
                    st.success("Dados atualizados!")
                    st.rerun()

            with col2:
                st.warning("⚠️ Exclusão permanente")

                if st.button("Excluir servidor"):
                    excluir_membro(registro["id"])
                    st.success("Servidor excluído!")
                    st.rerun()

    # ============================================================
    # FUNÇÕES & SUBSTITUIÇÕES
    # ============================================================
    with aba3:

        st.markdown("### 🔁 Registro de Funções")

        equipe = buscar_equipe()

        if not equipe:
            st.warning("Cadastre servidores primeiro.")
        else:
            nomes = {m["nome"]: m["id"] for m in equipe}

            funcao = st.selectbox("Função", [
                "Coordenador",
                "Subcoordenador",
                "Oficial Administrativo",
                "Praça Administrativo"
            ])

            pessoa = st.selectbox("Servidor", nomes.keys())
            data = st.date_input("Data de início")

            st.info("Coordenador e Subcoordenador possuem apenas 1 vaga. As demais permitem múltiplos ocupantes.")

            if st.button("Registrar Função"):
                trocar_funcao(nomes[pessoa], funcao, data)
                st.success("Função registrada com sucesso!")
                st.rerun()

    # ============================================================
    # FÉRIAS / LICENÇAS
    # ============================================================
    with aba4:

        st.markdown("### 🏖 Controle de Férias / Licenças")

        equipe = buscar_equipe()

        if not equipe:
            st.warning("Cadastre servidores primeiro.")
        else:
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
                df_f = pd.DataFrame(registros)
                df_f.columns = ["ID", "Servidor", "Tipo", "Início", "Fim", "Obs"]
                st.dataframe(df_f, use_container_width=True, hide_index=True)

    # ============================================================
    # RELATÓRIOS
    # ============================================================
    with aba5:

        st.markdown("### 📊 Relatórios Gerenciais")

        equipe = buscar_equipe()
        historico = buscar_historico()

        df = pd.DataFrame(equipe)

        ativos = df[df["ativo"] == True]
        inativos = df[df["ativo"] == False]

        col1, col2, col3 = st.columns(3)
        col1.metric("Total", len(df))
        col2.metric("Ativos", len(ativos))
        col3.metric("Inativos", len(inativos))

        st.divider()

        st.subheader("📜 Histórico de Coordenadores")

        dfh = pd.DataFrame(historico)
        dfh["Servidor"] = dfh["equipe"].apply(lambda x: x.get("nome") if isinstance(x, dict) else "")

        coord = dfh[dfh["funcao"] == "Coordenador"]

        coord = coord[["Servidor", "data_entrada", "data_saida"]]
        coord.columns = ["Servidor", "Entrada", "Saída"]

        st.dataframe(coord.sort_values("Entrada", ascending=False),
                     use_container_width=True, hide_index=True)



