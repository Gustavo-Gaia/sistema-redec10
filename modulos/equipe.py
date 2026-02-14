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

        historico_data = buscar_historico()

        if not historico_data:
            st.info("Nenhuma função registrada no histórico.")
            return

        # 1. Preparação dos Dados
        df_raw = pd.DataFrame(historico_data)
        
        # Converter datas para garantir ordenação correta
        df_raw["data_entrada"] = pd.to_datetime(df_raw["data_entrada"])
        
        # FILTRO DE ATIVOS: data_saida nula ou vazia
        df_atual = df_raw[df_raw["data_saida"].apply(
            lambda x: x is None or str(x).lower() == 'none' or str(x).strip() == ''
        )].copy()

        def extrair_campo(row, campo):
            eq = row.get("equipe", {})
            if isinstance(eq, dict):
                return str(eq.get(campo, "")).strip().upper()
            return ""

        # 2. Processamento para os Cards
        cargos_cards = {
            "Coordenador": [],
            "Subcoordenador": [],
            "Oficial Administrativo": [],
            "Praça Administrativo": []
        }

        for cargo in cargos_cards.keys():
            sub = df_atual[df_atual["funcao"] == cargo].copy()

            if not sub.empty:
                # LÓGICA ESPECIAL PARA COORDENADOR: 
                # Se houver mais de um "ativo" por erro de sistema, prioriza o que entrou por último
                if cargo == "Coordenador":
                    sub = sub.sort_values(by="data_entrada", ascending=False).head(1)
                
                # Normalização e Hierarquia
                sub["posto_c"] = sub.apply(lambda x: extrair_campo(x, "posto_graduacao"), axis=1)
                sub["nome_c"] = sub.apply(lambda x: extrair_campo(x, "nome"), axis=1)
                
                sub["posto_norm"] = sub["posto_c"].apply(
                    lambda t: re.sub(r"\s+", " ", str(t).replace("\u00a0", " ")).strip()
                )
                
                sub["peso"] = sub["posto_norm"].apply(lambda x: HIERARQUIA_MILITAR.get(x, 99))
                sub = sub.sort_values(by=["peso", "nome_c"])

                cargos_cards[cargo] = [
                    f"{row['posto_c']} {row['nome_c']}".strip() 
                    for _, row in sub.iterrows()
                ]

        # 3. Renderização Visual (Cards)
        col1, col2, col3, col4 = st.columns(4)

        def card(titulo, nomes):
            estilo_fonte = "12px" if len(nomes) <= 1 else "11px"
            conteudo = ""
            if nomes:
                for n in nomes:
                    conteudo += f'<div style="margin-bottom: 6px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 4px; line-height: 1.2;">{n}</div>'
            else:
                conteudo = "<span style='opacity:0.5; font-style: italic;'>Vago</span>"
        
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #163c66, #1f5aa6); padding: 15px; border-radius: 10px; color: white; text-align: center; min-height: 160px; display: flex; flex-direction: column; box-shadow: 0 4px 6px rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.1);">
                <div style="font-size: 10px; text-transform: uppercase; opacity: 0.8; font-weight: 700; margin-bottom: 12px; letter-spacing: 0.5px; border-bottom: 1px solid rgba(255,255,255,0.3); padding-bottom: 5px;">{titulo}</div>
                <div style="font-size: {estilo_fonte}; font-weight: 500; flex-grow: 1; display: flex; flex-direction: column; justify-content: center;">{conteudo}</div>
            </div>
            """, unsafe_allow_html=True)

        with col1: card("Coordenador", cargos_cards["Coordenador"])
        with col2: card("Subcoordenador", cargos_cards["Subcoordenador"])
        with col3: card("Oficial Administrativo", cargos_cards["Oficial Administrativo"])
        with col4: card("Praça Administrativo", cargos_cards["Praça Administrativo"])

        st.divider()

        # 4. Tabela de Histórico (Geral)
        st.subheader("📜 Histórico de Ocupação e Trocas")
        if not df_raw.empty:
            df_hist = df_raw.copy()
            
            # Extração de nomes para a listagem
            df_hist["Militar"] = df_hist["equipe"].apply(
                lambda x: f"{x.get('posto_graduacao', '')} {x.get('nome', '')}".strip() if isinstance(x, dict) else "Militar Excluído"
            )
            
            # Formatação para exibição
            df_view = df_hist[["Militar", "funcao", "data_entrada", "data_saida"]].copy()
            df_view["data_entrada"] = df_view["data_entrada"].dt.strftime('%d/%m/%Y')
            df_view["data_saida"] = df_view["data_saida"].apply(
                lambda x: pd.to_datetime(x).strftime('%d/%m/%Y') if pd.notnull(x) and str(x).strip() != '' else "Ativo"
            )
            
            df_view.columns = ["Servidor", "Função", "Início", "Término"]
            
            # Ordenação: Ativos primeiro, depois por data de início mais recente
            st.dataframe(
                df_view.sort_values(by=["Término", "Início"], ascending=[True, False]), 
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
            posto = st.selectbox("Posto / Graduação", list(HIERARQUIA_MILITAR.keys()))
            quadro = st.text_input("Quadro / QBMP", value="Q00/00")
            telefone = st.text_input("Telefone")
            salvar = st.form_submit_button("Cadastrar Servidor")

        if salvar and nome:
            inserir_membro({
                "nome": nome.strip().upper(),
                "nome_guerra": nome_guerra.strip().upper(),
                "rg": rg, "id_funcional": id_funcional, "posto_graduacao": posto,
                "quadro_qbmp": quadro.upper(), "telefone": telefone, "ativo": True
            })
            st.success("Servidor cadastrado!")
            st.rerun()

        st.divider()
        st.markdown("### 📋 Listagem Geral")
        equipe = buscar_equipe()
        if equipe:
            df_lista = pd.DataFrame(equipe)
            df_lista["peso"] = df_lista["posto_graduacao"].apply(lambda x: HIERARQUIA_MILITAR.get(x, 99))
            df_lista = df_lista.sort_values(by=["peso", "nome"])
            
            st.dataframe(df_lista[["posto_graduacao", "nome", "ativo", "telefone"]], use_container_width=True, hide_index=True)

            st.divider()
            st.markdown("### ✏️ Editar / Desativar Servidor")
            opcoes_edicao = {f"{r['posto_graduacao']} {r['nome']} ({'ATIVO' if r['ativo'] else 'INATIVO'})": r for _, r in df_lista.iterrows()}
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
                
                ativo_edit = st.checkbox("Membro Ativo (Aparece em seleções)", value=bool(registro["ativo"]))

                c1, c2 = st.columns(2)
                if c1.button("Salvar Alterações", use_container_width=True):
                    atualizar_membro(registro["id"], {
                        "nome": nome_edit.upper(), "posto_graduacao": posto_edit,
                        "quadro_qbmp": quadro_edit.upper(), "telefone": tel_edit,
                        "ativo": ativo_edit
                    })
                    st.success("Atualizado!")
                    st.rerun()
                
                if c2.button("Excluir Definitivamente", use_container_width=True, type="secondary"):
                    excluir_membro(registro["id"])
                    st.rerun()

# ============================================================
# 3. FUNÇÕES & SUBSTITUIÇÕES (COM HISTÓRICO DE COMANDO)
# ============================================================

def funcoes_substituicoes(aba):
    with aba:
        st.markdown("### 🔁 Registro de Funções")
        
        # Busca dados atualizados
        equipe = buscar_equipe()
        historico_raw = buscar_historico()
        
        if not equipe:
            st.warning("Nenhum servidor cadastrado no sistema.")
            return

        # FILTRO: Apenas membros ativos para novas nomeações
        ativos = [m for m in equipe if m.get("ativo") == True]
        
        if not ativos:
            st.warning("Nenhum servidor ATIVO encontrado para novas funções.")
        else:
            nomes_id = {f"{m['posto_graduacao']} {m['nome']}": m["id"] for m in ativos}
            
            # Formuário de Registro
            col_f1, col_f2, col_f3 = st.columns([1, 1, 0.8])
            with col_f1:
                funcao = st.selectbox("Função", ["Coordenador", "Subcoordenador", "Oficial Administrativo", "Praça Administrativo"])
            with col_f2:
                pessoa_label = st.selectbox("Servidor Ativo", list(nomes_id.keys()))
            with col_f3:
                data = st.date_input("Data de início", help="No caso de Coordenador, esta será a data de saída do anterior.")

            if st.button("Confirmar Alteração de Função", use_container_width=True, type="primary"):
                trocar_funcao(nomes_id[pessoa_label], funcao, data)
                st.success(f"Registro de {funcao} atualizado!")
                st.rerun()

        st.divider()

        # ============================================================
        # SEÇÃO ESPECÍFICA: LINHA DO TEMPO DOS COORDENADORES
        # ============================================================
        st.markdown("### 🏛️ Galeria de Coordenadores (Histórico de Comando)")
        
        if historico_raw:
            df_hist = pd.DataFrame(historico_raw)
            
            # Filtrar apenas Coordenadores
            df_coord = df_hist[df_hist["funcao"] == "Coordenador"].copy()
            
            if not df_coord.empty:
                # Extrair Posto e Nome do dicionário 'equipe'
                df_coord["Coordenador"] = df_coord["equipe"].apply(
                    lambda x: f"{x.get('posto_graduacao', '')} {x.get('nome', '')}".strip() if isinstance(x, dict) else "Desconhecido"
                )
                
                # Converter e formatar datas
                df_coord["data_entrada"] = pd.to_datetime(df_coord["data_entrada"])
                df_coord["Início do Mandato"] = df_coord["data_entrada"].dt.strftime('%d/%m/%Y')
                
                # Tratar data de saída (Término)
                df_coord["Término"] = df_coord["data_saida"].apply(
                    lambda x: pd.to_datetime(x).strftime('%d/%m/%Y') if pd.notnull(x) and str(x).strip() != '' else "🚩 ATUAL"
                )
                
                # Selecionar e ordenar (Mais recente primeiro)
                df_exibicao = df_coord[["Coordenador", "Início do Mandato", "Término"]]
                
                # Estilização visual para destacar o atual
                def destacar_atual(val):
                    color = 'background-color: rgba(28, 131, 225, 0.1)' if val == "🚩 ATUAL" else ''
                    return color

                st.dataframe(
                    df_exibicao.sort_values(by="Início do Mandato", ascending=False),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Nenhum histórico de Coordenador encontrado.")
        else:
            st.info("O histórico está vazio.")

# ============================================================
# 4. FÉRIAS / LICENÇAS
# ============================================================

def ferias_licencas(aba):
    with aba:
        st.markdown("### 🏖 Controle de Férias / Licenças")
        equipe = buscar_equipe()
        if not equipe: return

        ativos = [m for m in equipe if m.get("ativo") == True]
        
        if not ativos:
            st.warning("Nenhum servidor ATIVO encontrado.")
            return

        nomes_id = {f"{m['posto_graduacao']} {m['nome']}": m["id"] for m in ativos}

        with st.form("form_ferias"):
            pessoa_label = st.selectbox("Servidor Ativo", list(nomes_id.keys()))
            tipo = st.selectbox("Tipo", ["Férias", "Licença Médica", "Licença Prêmio", "Outros"])
            inicio = st.date_input("Data início")
            fim = st.date_input("Data fim")
            obs = st.text_area("Observação")
            salvar = st.form_submit_button("Registrar")

        if salvar:
            inserir_ferias({"equipe_id": nomes_id[pessoa_label], "tipo": tipo, "inicio": str(inicio), "fim": str(fim), "observacao": obs})
            st.success("Afastamento salvo!")
            st.rerun()

        st.divider()
        st.markdown("### 📅 Registros Recentes")
        registros = buscar_ferias()
        if registros:
            st.dataframe(pd.DataFrame(registros), use_container_width=True, hide_index=True)


# ============================================================
# 5. RELATÓRIOS
# ============================================================

def relatorios(aba):
    with aba:
        st.markdown("### 📊 Relatórios Gerenciais")
        equipe_raw = buscar_equipe()
        historico_raw = buscar_historico()
        if not equipe_raw: return

        df_equipe = pd.DataFrame(equipe_raw)
        df_hist = pd.DataFrame(historico_raw)

        # Ocupantes atuais seguindo a mesma lógica do painel
        ocupantes_atuais = df_hist[df_hist["data_saida"].isna()]["equipe_id"].nunique()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Cadastrado", len(df_equipe))
        col2.metric("Efetivo em Função", ocupantes_atuais)
        col3.metric("Ativos na Unidade", len(df_equipe[df_equipe["ativo"] == True]))
        
        st.divider()
        st.markdown("### 🖨 Exportar Dados")
        st.download_button(
            label="Baixar Planilha da Equipe (CSV)",
            data=df_equipe.to_csv(index=False).encode('utf-8'),
            file_name='equipe_redec10.csv',
            mime='text/csv',
        )
