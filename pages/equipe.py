# pages/equipe.py

import streamlit as st
import pandas as pd
from services.supabase import buscar_equipe, inserir_membro
from services.ferias import buscar_ferias, inserir_ferias
from services.historico import buscar_historico, inserir_historico

# ============================================================
# TELA PRINCIPAL EQUIPE
# ============================================================

def tela_equipe():

    st.subheader("👥 Gestão da Equipe - REDEC 10")

    aba1, aba2, aba3, aba4, aba5 = st.tabs([
            "🧭 Painel da Equipe",
            "➕ Cadastro & Gestão",
            "🔁 Substituições",
            "🏖 Férias / Licenças",
            "📊 Relatórios"
    ])


    # ============================================================
    # 1️⃣ PAINEL DA EQUIPE ATUAL
    # ============================================================
    with aba1:
        st.markdown("### 🧭 Composição Atual da REDEC 10")
    
        historico = buscar_historico()
        equipe = buscar_equipe()
    
        if not historico:
            st.info("Nenhuma função ocupada atualmente.")
        else:
            df = pd.DataFrame(historico)
            df = df[df["data_saida"].isna()]
    
            cargos = [
                "Coordenador",
                "Subcoordenador",
                "Oficial Administrativo",
                "Praça Administrativo"
            ]
    
            cols = st.columns(4)
    
            for i, cargo in enumerate(cargos):
                atual = df[df["funcao"] == cargo]
    
                with cols[i]:
                    st.markdown(f"""
                    <div style="background:#1f4c81;padding:15px;border-radius:12px;color:white;text-align:center;">
                        <h5>{cargo}</h5>
                        <h4>{atual.iloc[0]['funcao'] if not atual.empty else 'Vago'}</h4>
                    </div>
                    """, unsafe_allow_html=True)
    
        st.divider()
    
        st.subheader("Histórico Funcional")
    
        if historico:
            st.dataframe(pd.DataFrame(historico), use_container_width=True)
        else:
            st.info("Nenhum registro no histórico ainda.")


    # ============================================================
    # 2️⃣ CADASTRO & GESTÃO
    # ============================================================
    with aba2:
        col1, col2 = st.columns([1,2])

        with col1:
            st.markdown("### Novo Cadastro")

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
            st.markdown("### Lista Geral")

            dados = buscar_equipe()

            if dados:
                df = pd.DataFrame(dados)

                colunas = {
                    "nome": "Nome",
                    "nome_guerra": "Nome de Guerra",
                    "posto_graduacao": "Posto",
                    "quadro_qbmp": "Quadro",
                    "telefone": "Telefone",
                    "ativo": "Ativo"
                }

                df = df[list(colunas.keys())]
                df = df.rename(columns=colunas)

                st.dataframe(df, use_container_width=True)
            else:
                st.info("Nenhum membro cadastrado.")

    # ============================================================
    # 3️⃣ SUBSTITUIÇÕES
    # ============================================================
    with aba3:
        st.markdown("### 🔁 Controle de Substituições Funcionais")
    
        from services.historico import trocar_funcao
    
        equipe = buscar_equipe()
    
        if not equipe:
            st.warning("Cadastre membros antes.")
        else:
            nomes = {m["nome"]: m["id"] for m in equipe}
    
            funcao = st.selectbox("Função", [
                "Coordenador",
                "Subcoordenador",
                "Oficial Administrativo",
                "Praça Administrativo"
            ])
    
            pessoa = st.selectbox("Novo ocupante", nomes.keys())
            data = st.date_input("Data de início")
    
            if st.button("🔁 Registrar Substituição"):
                trocar_funcao(nomes[pessoa], funcao, data)
    
                st.success(f"{funcao} atualizado com sucesso!")
                st.rerun()


    # ============================================================
    # 4️⃣ FÉRIAS / LICENÇAS
    # ============================================================
    with aba4:
        st.markdown("### 🏖 Controle de Férias e Licenças")
    
        equipe = buscar_equipe()
    
        if not equipe:
            st.warning("Cadastre membros antes.")
        else:
            nomes = {m["nome"]: m["id"] for m in equipe}
    
            with st.form("form_ferias"):
                pessoa = st.selectbox("Servidor", nomes.keys())
                tipo = st.selectbox("Tipo", ["Férias", "Licença Médica", "Licença Prêmio", "Outros"])
                inicio = st.date_input("Data de início")
                fim = st.date_input("Data final")
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
    # 5️⃣ RELATÓRIOS
    # ============================================================
    with aba5:
        st.markdown("### 📊 Relatórios Gerenciais")
    
        equipe = buscar_equipe()
        historico = buscar_historico()
    
        if equipe:
            df = pd.DataFrame(equipe)
    
            ativos = df[df["ativo"] == True]
            inativos = df[df["ativo"] == False]
    
            col1, col2, col3 = st.columns(3)
    
            col1.metric("Total", len(df))
            col2.metric("Ativos", len(ativos))
            col3.metric("Inativos", len(inativos))
    
            st.divider()
            st.subheader("Equipe Ativa")
            st.dataframe(ativos, use_container_width=True)
    
        if historico:
            st.divider()
            st.subheader("Histórico de Coordenadores")
    
            dfh = pd.DataFrame(historico)
            coord = dfh[dfh["funcao"] == "Coordenador"]
    
            st.dataframe(coord, use_container_width=True)


