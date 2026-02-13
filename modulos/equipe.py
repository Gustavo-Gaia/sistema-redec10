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
# CONFIGURAÇÕES E CONSTANTES
# ============================================================

# Dicionário global para garantir ordenação e padronização
HIERARQUIA_MILITAR = {
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
# 1. PAINEL PRINCIPAL (CARDS COM HIERARQUIA)
# ============================================================

def painel_equipe(aba):
    with aba:
        st.markdown("### 🧭 Composição Atual da REDEC 10")

        historico = buscar_historico()

        if not historico:
            st.info("Nenhuma função registrada.")
            return

        # Filtragem de ocupantes atuais
        df = pd.DataFrame(historico)
        df = df[df["data_saida"].isna()].copy()

        # Extração e Limpeza de dados
        df["nome"] = df["equipe"].apply(lambda x: x.get("nome", "").strip().upper() if isinstance(x, dict) else "")
        df["posto_raw"] = df["equipe"].apply(lambda x: x.get("posto_graduacao", "").strip().upper() if isinstance(x, dict) else "")

        def normalizar_posto(p):
            p = re.sub(r"\s+", " ", str(p)) # Remove espaços duplos ou invisíveis
            return p.strip()

        df["posto_limpo"] = df["posto_raw"].apply(normalizar_posto)

        # Preparação dos cargos para os cards
        cargos_cards = {
            "Coordenador": [],
            "Subcoordenador": [],
            "Oficial Administrativo": [],
            "Praça Administrativo": []
        }

        for funcao in cargos_cards.keys():
            sub = df[df["funcao"] == funcao].copy()

            if sub.empty:
                continue

            # Aplica o peso da hierarquia para ordenação
            sub["peso"] = sub["posto_limpo"].apply(lambda x: HIERARQUIA_MILITAR.get(x, 99))
            
            # Ordena por Hierarquia (peso) e depois por Nome (alfabético)
            sub = sub.sort_values(by=["peso", "nome"])

            # Gera a lista final de strings "Posto Nome"
            lista_formatada = [
                f"{row['posto_raw']} {row['nome']}".strip() 
                for _, row in sub.iterrows()
            ]

            cargos_cards[funcao] = lista_formatada

        # Interface de Cards
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
                <div style="font-size:11px; opacity:.8; margin-bottom:8px; font-weight:bold;">
                    {titulo.upper()}
                </div>
                <div style="font-size:14px; font-weight:600; line-height:1.4;">
                    {conteudo}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col1: card("Coordenador", cargos_cards["Coordenador"])
        with col2: card("Subcoordenador", cargos_cards["Subcoordenador"])
        with col3: card("Oficial Administrativo", cargos_cards["Oficial Administrativo"])
        with col4: card("Praça Administrativo", cargos_cards["Praça Administrativo"])

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
# 2. CADASTRO & GESTÃO
# ============================================================

def cadastro_gestao(aba):
    with aba:
        st.markdown("### 👤 Cadastro de Novo Servidor")

        with st.form("novo_membro"):
            nome = st.text_input("Nome completo")
            nome_guerra = st.text_input("Nome de guerra")
            rg = st.text_input("RG")
            id_funcional = st.text_input("ID Funcional")
            
            # Selectbox para evitar erros de digitação na hierarquia
            posto = st.selectbox("Posto / Graduação", list(HIERARQUIA_MILITAR.keys()))
            
            quadro = st.text_input("Quadro / QBMP", value="QBMP/0")
            telefone = st.text_input("Telefone")

            salvar = st.form_submit_button("Cadastrar")

        if salvar and nome:
            inserir_membro({
                "nome": nome.strip().upper(),
                "nome_guerra": nome_guerra.strip().upper(),
                "rg": rg,
                "id_funcional": id_funcional,
                "posto_graduacao": posto,
                "quadro_qbmp": quadro.upper(),
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

        df_equipe = pd.DataFrame(equipe)
        st.dataframe(df_equipe[["id","nome","posto_graduacao","quadro_qbmp","telefone"]],
                     use_container_width=True, hide_index=True)

        st.divider()
        st.markdown("### ✏️ Editar / Excluir")

        selecionado = st.selectbox("Selecionar servidor para editar", df_equipe["nome"].tolist())
        registro = df_equipe[df_equipe["nome"] == selecionado].iloc[0]

        col1, col2 = st.columns(2)

        with col1:
            nome_edit = st.text_input("Nome", registro["nome"])
            
            # Busca índice do posto atual para o selectbox
            idx_posto = list(HIERARQUIA_MILITAR.keys()).index(registro["posto_graduacao"]) if registro["posto_graduacao"] in HIERARQUIA_MILITAR else 0
            posto_edit = st.selectbox("Posto", list(HIERARQUIA_MILITAR.keys()), index=idx_posto)
            
            quadro_edit = st.text_input("Quadro", registro["quadro_qbmp"])
            tel_edit = st.text_input("Telefone", registro["telefone"])

            if st.button("Atualizar dados"):
                atualizar_membro(registro["id"], {
                    "nome": nome_edit.upper(),
                    "posto_graduacao": posto_edit,
                    "quadro_qbmp": quadro_edit.upper(),
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
# 3. FUNÇÕES & SUBSTITUIÇÕES
# ============================================================

def funcoes_substituicoes(aba):
    with aba:
        st.markdown("### 🔁 Registro de Funções")

        equipe = buscar_equipe()
        if not equipe:
            st.warning("Cadastre servidores primeiro.")
            return

        nomes_id = {f"{m['posto_graduacao']} {m['nome']}": m["id"] for m in equipe}

        funcao = st.selectbox("Função", [
            "Coordenador",
            "Subcoordenador",
            "Oficial Administrativo",
            "Praça Administrativo"
        ])

        pessoa_label = st.selectbox("Servidor", list(nomes_id.keys()))
        data = st.date_input("Data de início")

        st.info("Nota: Coordenador e Subcoordenador permitem apenas 1 ocupante ativo por vez.")

        if st.button("Registrar Função"):
            trocar_funcao(nomes_id[pessoa_label], funcao, data)
            st.success(f"Função {funcao} registrada com sucesso!")
            st.rerun()


# ============================================================
# 4. FÉRIAS / LICENÇAS
# ============================================================

def ferias_licencas(aba):
    with aba:
        st.markdown("### 🏖 Controle de Férias / Licenças")

        equipe = buscar_equipe()
        if not equipe:
            st.warning("Cadastre servidores primeiro.")
            return

        nomes_id = {f"{m['posto_graduacao']} {m['nome']}": m["id"] for m in equipe}

        with st.form("form_ferias"):
            pessoa_label = st.selectbox("Servidor", list(nomes_id.keys()))
            tipo = st.selectbox("Tipo", ["Férias", "Licença Médica", "Licença Prêmio", "Outros"])
            inicio = st.date_input("Data início")
            fim = st.date_input("Data fim")
            obs = st.text_area("Observação")

            salvar = st.form_submit_button("Registrar")

        if salvar:
            inserir_ferias({
                "equipe_id": nomes_id[pessoa_label],
                "tipo": tipo,
                "inicio": str(inicio),
                "fim": str(fim),
                "observacao": obs
            })
            st.success("Registro de ausência salvo!")
            st.rerun()

        st.divider()
        st.markdown("### 📅 Registros Recentes")
        registros = buscar_ferias()
        if registros:
            df_ferias = pd.DataFrame(registros)
            st.dataframe(df_ferias, use_container_width=True, hide_index=True)


# ============================================================
# 5. RELATÓRIOS
# ============================================================

def relatorios(aba):
    with aba:
        st.markdown("### 📊 Relatórios Gerenciais")

        equipe = buscar_equipe()
        if not equipe:
            st.info("Nenhum dado disponível.")
            return

        df = pd.DataFrame(equipe)
        ativos = df[df["ativo"] == True]

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Cadastrado", len(df))
        col2.metric("Efetivo Ativo", len(ativos))
        col3.metric("Afastados (Férias/Lic)", "Ver Painel") # Logica futura para cruzamento

        st.divider()
        st.markdown("### 🖨 Exportar Dados")
        st.download_button(
            label="Baixar Planilha da Equipe (CSV)",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name='equipe_redec10.csv',
            mime='text/csv',
        )
