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
# CONFIGURAÇÕES E CONSTANTES - HIERARQUIA MILITAR
# ============================================================
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

        # 1. Criar DataFrame e filtrar ocupantes atuais
        df_raw = pd.DataFrame(historico)
        df = df_raw[df_raw["data_saida"].isna()].copy()

        # 2. Extração Robusta dos dados da Equipe (JOIN do Supabase)
        def extrair_campo(row, campo):
            eq = row.get("equipe", {})
            if isinstance(eq, dict):
                return str(eq.get(campo, "")).strip().upper()
            return ""

        # Criamos colunas explícitas para evitar erros de renderização
        df["nome_c"] = df.apply(lambda x: extrair_campo(x, "nome"), axis=1)
        df["posto_c"] = df.apply(lambda x: extrair_campo(x, "posto_graduacao"), axis=1)

        # 3. Normalização para ordenação
        def normalize(t):
            return re.sub(r"\s+", " ", t.replace("\u00a0", " ")).strip()

        df["posto_ord"] = df["posto_c"].apply(normalize)

        # 4. Organização por cargos para os Cards
        cargos_cards = {
            "Coordenador": [],
            "Subcoordenador": [],
            "Oficial Administrativo": [],
            "Praça Administrativo": []
        }

        for funcao in cargos_cards.keys():
            sub = df[df["funcao"] == funcao].copy()

            if not sub.empty:
                # Aplicar peso da hierarquia
                sub["peso"] = sub["posto_ord"].apply(lambda x: HIERARQUIA_MILITAR.get(x, 99))
                # Ordenar por Hierarquia e depois Nome
                sub = sub.sort_values(by=["peso", "nome_c"])

                # MONTAGEM DA STRING FINAL: "POSTO NOME"
                cargos_cards[funcao] = [
                    f"{row['posto_c']} {row['nome_c']}".strip() 
                    for _, row in sub.iterrows()
                ]

        # 5. Renderização dos Cards
        col1, col2, col3, col4 = st.columns(4)

        def card(titulo, nomes):
            # Tratamento para nomes longos: reduz fonte se houver muitos nomes ou nomes grandes
            estilo_fonte = "12px" if len(nomes) <= 2 else "11px"
            
            conteudo = ""
            if nomes:
                for n in nomes:
                    conteudo += f'<div style="margin-bottom: 4px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 2px;">{n}</div>'
            else:
                conteudo = "<span style='opacity:0.6 italic'>Vago</span>"
        
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #163c66, #1f5aa6);
                padding: 15px;
                border-radius: 10px;
                color: white;
                text-align: center;
                min-height: 150px;
                display: flex;
                flex-direction: column;
                box-shadow: 0 4px 6px rgba(0,0,0,0.2);
                border: 1px solid rgba(255,255,255,0.1);">
                <div style="font-size: 10px; text-transform: uppercase; opacity: 0.7; font-weight: 700; margin-bottom: 12px; letter-spacing: 0.5px; border-bottom: 1px solid rgba(255,255,255,0.3); padding-bottom: 5px;">
                    {titulo}
                </div>
                <div style="font-size: {estilo_fonte}; font-weight: 500; line-height: 1.2; flex-grow: 1; display: flex; flex-direction: column; justify-content: center;">
                    {conteudo}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col1: card("Coordenador", cargos_cards["Coordenador"])
        with col2: card("Subcoordenador", cargos_cards["Subcoordenador"])
        with col3: card("Oficial Administrativo", cargos_cards["Oficial Administrativo"])
        with col4: card("Praça Administrativo", cargos_cards["Praça Administrativo"])

        st.divider()
        
        # 6. Histórico Funcional corrigido
        st.subheader("📜 Histórico Funcional")
        if not df_raw.empty:
             df_raw["Militar"] = df_raw["equipe"].apply(
                 lambda x: f"{x.get('posto_graduacao', '')} {x.get('nome', '')}".strip() if isinstance(x, dict) else "Desconhecido"
             )
             df_hist = df_raw[["Militar", "funcao", "data_entrada", "data_saida"]].copy()
             df_hist.columns = ["Servidor (Posto + Nome)", "Função", "Início", "Término"]
             st.dataframe(df_hist.sort_values("Início", ascending=False), use_container_width=True, hide_index=True)


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
            posto = st.selectbox("Posto / Graduação", list(HIERARQUIA_MILITAR.keys()))
            quadro = st.text_input("Quadro / QBMP", value="Q00/00")
            telefone = st.text_input("Telefone")

            salvar = st.form_submit_button("Cadastrar Servidor")

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
        st.markdown("### 📋 Listagem Geral")
        equipe = buscar_equipe()
        if equipe:
            df_lista = pd.DataFrame(equipe)
            # Ordenar por hierarquia
            df_lista["peso"] = df_lista["posto_graduacao"].apply(lambda x: HIERARQUIA_MILITAR.get(x, 99))
            df_lista = df_lista.sort_values(by=["peso", "nome"])
            
            # Exibir com posto antes do nome na tabela
            st.dataframe(df_lista[["posto_graduacao", "nome", "quadro_qbmp", "telefone"]], 
                         use_container_width=True, hide_index=True)

            st.divider()
            st.markdown("### ✏️ Editar / Excluir")
            # Label do selectbox agora inclui o posto para clareza
            opcoes_edicao = {f"{r['posto_graduacao']} {r['nome']}": r for _, r in df_lista.iterrows()}
            selecionado_label = st.selectbox("Selecione para editar", list(opcoes_edicao.keys()))
            registro = opcoes_edicao[selecionado_label]

            with st.expander(f"Editar dados de {registro['nome']}"):
                col1, col2 = st.columns(2)
                with col1:
                    nome_edit = st.text_input("Nome", registro["nome"])
                    idx_p = list(HIERARQUIA_MILITAR.keys()).index(registro["posto_graduacao"]) if registro["posto_graduacao"] in HIERARQUIA_MILITAR else 0
                    posto_edit = st.selectbox("Posto", list(HIERARQUIA_MILITAR.keys()), index=idx_p, key="ed_posto")
                with col2:
                    quadro_edit = st.text_input("Quadro", registro["quadro_qbmp"])
                    tel_edit = st.text_input("Telefone", registro["telefone"])

                c1, c2 = st.columns(2)
                if c1.button("Salvar Alterações", use_container_width=True):
                    atualizar_membro(registro["id"], {
                        "nome": nome_edit.upper(),
                        "posto_graduacao": posto_edit,
                        "quadro_qbmp": quadro_edit.upper(),
                        "telefone": tel_edit
                    })
                    st.success("Atualizado!")
                    st.rerun()
                
                if c2.button("Excluir Definitivamente", use_container_width=True, type="secondary"):
                    excluir_membro(registro["id"])
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

        # Dicionário garantindo Posto + Nome no seletor
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
            # Melhorar visualização da tabela de férias com nomes legíveis
            df_ferias = pd.DataFrame(registros)
            st.dataframe(df_ferias, use_container_width=True, hide_index=True)


# ============================================================
# 5. RELATÓRIOS
# ============================================================

def relatorios(aba):
    with aba:
        st.markdown("### 📊 Relatórios Gerenciais")

        # 1. Busca dados atualizados
        equipe_raw = buscar_equipe()
        historico_raw = buscar_historico()
        
        if not equipe_raw:
            st.info("Nenhum dado disponível.")
            return

        df_equipe = pd.DataFrame(equipe_raw)
        df_hist = pd.DataFrame(historico_raw)

        # 2. Filtra quem está REALMENTE em uma função agora (data_saida é nulo)
        ocupantes_atuais = df_hist[df_hist["data_saida"].isna()]["equipe_id"].unique()
        total_real_ativo = len(ocupantes_atuais)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Cadastrado", len(df_equipe))
        col2.metric("Efetivo em Função", total_real_ativo)
        col3.metric("Membros Ativos (DB)", len(df_equipe[df_equipe["ativo"] == True]))
        
        st.divider()
        st.markdown("### 🖨 Exportar Dados")
        st.download_button(
            label="Baixar Planilha da Equipe (CSV)",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name='equipe_redec10.csv',
            mime='text/csv',
        )
