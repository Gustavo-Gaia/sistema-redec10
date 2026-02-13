# modulos/equipe.py

import streamlit as st
import pandas as pd
import re

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

    abas = st.tabs([
        "🧭 Painel da Equipe",
        "➕ Cadastro & Gestão",
        "🔁 Funções & Substituições",
        "🏖 Férias / Licenças",
        "📊 Relatórios"
    ])

    painel_equipe(abas[0])
    cadastro_gestao(abas[1])
    funcoes_substituicoes(abas[2])
    ferias_licencas(abas[3])
    relatorios(abas[4])


# ============================================================
# PAINEL PRINCIPAL
# ============================================================

def painel_equipe(aba):

    with aba:

        st.markdown("### 🧭 Composição Atual da REDEC 10")

        historico = buscar_historico()

        if not historico:
            st.info("Nenhuma função registrada.")
            return

        df = pd.DataFrame(historico)
        df = df[df["data_saida"].isna()]

        df["nome"] = df["equipe"].apply(lambda x: x.get("nome", "") if isinstance(x, dict) else "")
        df["posto_raw"] = df["equipe"].apply(lambda x: x.get("posto_graduacao", "") if isinstance(x, dict) else "")

        # =================== NORMALIZAÇÃO DO POSTO ===================
        def normalizar_posto(p):
            p = str(p).upper()
            p = p.replace("\u00a0", " ")   # remove espaço invisível
            p = re.sub(r"\s+", " ", p)     # remove espaços duplicados
            return p.strip()

        df["posto"] = df["posto_raw"].apply(normalizar_posto)
        df["nome"] = df["nome"].astype(str).str.strip().str.upper()


        # =================== HIERARQUIA MILITAR ===================
        hierarquia = {
            "CEL BM": 1,
            "TEN CEL BM": 2,
            "MAJ BM": 3,
            "CAP BM": 4,
            "1º TEN BM": 5,
            "2º TEN BM": 6,
            "ASPIRANTE BM": 7,
            "SUBTEN BM": 8,
            "1º SGT BM": 9,
            "2º SGT BM": 10,
            "3º SGT BM": 11,
            "CB BM": 12,
            "SD BM": 13
        }

        cargos = {
            "Coordenador": [],
            "Subcoordenador": [],
            "Oficial Administrativo": [],
            "Praça Administrativo": []
        }

        for funcao in cargos.keys():

            sub = df[df["funcao"] == funcao].copy()

            if sub.empty:
                continue

            sub["peso"] = sub["posto"].apply(lambda x: hierarquia.get(x, 99))
            sub = sub.sort_values("peso")

            lista = [
                f"{p} {n}".strip()
                for p, n in zip(sub["posto"], sub["nome"])
            ]

            cargos[funcao] = lista

        col1, col2, col3, col4 = st.columns(4)

        def card(titulo, nomes):
            conteudo = "<br>".join(nomes) if nomes else "<span style='opacity:0.6'>Vago</span>"
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #163c66, #1f5aa6);
                padding:18px;
                border-radius:14px;
                color:white;
                text-align:center;
                min-height:130px;
                box-shadow:0 6px 12px rgba(0,0,0,.18);
                display:flex;
                flex-direction:column;
                justify-content:center;">
                <div style="font-size:12px; opacity:.8; margin-bottom:8px;">
                    {titulo.upper()}
                </div>
                <div style="font-size:15px; font-weight:600; line-height:1.55;">
                    {conteudo}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col1: card("Coordenador", cargos["Coordenador"])
        with col2: card("Subcoordenador", cargos["Subcoordenador"])
        with col3: card("Oficial Administrativo", cargos["Oficial Administrativo"])
        with col4: card("Praça Administrativo", cargos["Praça Administrativo"])

        st.divider()

        st.subheader("📜 Histórico Funcional")

        dfh = pd.DataFrame(historico)
        dfh["Servidor"] = dfh["equipe"].apply(lambda x: x.get("nome") if isinstance(x, dict) else "")

        dfh = dfh[["Servidor", "funcao", "data_entrada", "data_saida"]]
        dfh.columns = ["Servidor", "Função", "Entrada", "Saída"]

        st.dataframe(
            dfh.sort_values("Entrada", ascending=False),
            use_container_width=True,
            hide_index=True
        )



# ============================================================
# CADASTRO & GESTÃO
# ============================================================

def cadastro_gestao(aba):

    with aba:

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

        if salvar and nome:
            inserir_membro({
                "nome": nome,
                "nome_guerra": nome_guerra,
                "rg": rg,
                "id_funcional": id_funcional,
                "posto_graduacao": posto.upper(),
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
            return

        df = pd.DataFrame(equipe)

        st.dataframe(df[["id","nome","posto_graduacao","quadro_qbmp","telefone"]],
                     use_container_width=True, hide_index=True)

        st.divider()
        st.markdown("### ✏️ Editar / Excluir")

        selecionado = st.selectbox("Selecionar servidor", df["nome"].tolist())
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
                    "posto_graduacao": posto_edit.upper(),
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

def funcoes_substituicoes(aba):

    with aba:

        st.markdown("### 🔁 Registro de Funções")

        equipe = buscar_equipe()
        if not equipe:
            st.warning("Cadastre servidores primeiro.")
            return

        nomes = {m["nome"]: m["id"] for m in equipe}

        funcao = st.selectbox("Função", [
            "Coordenador",
            "Subcoordenador",
            "Oficial Administrativo",
            "Praça Administrativo"
        ])

        pessoa = st.selectbox("Servidor", list(nomes.keys()))
        data = st.date_input("Data de início")

        st.info("Coordenador e Subcoordenador possuem apenas 1 vaga. As demais permitem múltiplos ocupantes.")

        if st.button("Registrar Função"):
            trocar_funcao(nomes[pessoa], funcao, data)
            st.success("Função registrada com sucesso!")
            st.rerun()


# ============================================================
# FÉRIAS / LICENÇAS
# ============================================================

def ferias_licencas(aba):

    with aba:

        st.markdown("### 🏖 Controle de Férias / Licenças")

        equipe = buscar_equipe()
        if not equipe:
            st.warning("Cadastre servidores primeiro.")
            return

        nomes = {m["nome"]: m["id"] for m in equipe}

        with st.form("form_ferias"):
            pessoa = st.selectbox("Servidor", list(nomes.keys()))
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
            st.dataframe(pd.DataFrame(registros),
                         use_container_width=True, hide_index=True)


# ============================================================
# RELATÓRIOS
# ============================================================

def relatorios(aba):

    with aba:

        st.markdown("### 📊 Relatórios Gerenciais")

        equipe = buscar_equipe()
        historico = buscar_historico()

        if not equipe:
            st.info("Nenhum dado disponível.")
            return

        df = pd.DataFrame(equipe)

        ativos = df[df["ativo"] == True]
        inativos = df[df["ativo"] == False]

        col1, col2, col3 = st.columns(3)
        col1.metric("Total", len(df))
        col2.metric("Ativos", len(ativos))
        col3.metric("Inativos", len(inativos))

        if historico:
            st.divider()
            st.subheader("📜 Histórico de Coordenadores")

            dfh = pd.DataFrame(historico)
            dfh["Servidor"] = dfh["equipe"].apply(lambda x: x.get("nome") if isinstance(x, dict) else "")

            coord = dfh[dfh["funcao"] == "Coordenador"]
            coord = coord[["Servidor", "data_entrada", "data_saida"]]
            coord.columns = ["Servidor", "Entrada", "Saída"]

            st.dataframe(coord.sort_values("Entrada", ascending=False),
                         use_container_width=True, hide_index=True)


