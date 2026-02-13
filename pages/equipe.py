import streamlit as st
from services.supabase_client import supabase
import pandas as pd

def tela_equipe():
    st.header("👥 Gestão da Equipe REDEC 10")

    with st.form("cadastro"):
        col1, col2, col3 = st.columns(3)

        nome = col1.text_input("Nome completo")
        nome_guerra = col2.text_input("Nome de guerra")
        rg = col3.text_input("RG")

        col4, col5, col6 = st.columns(3)

        id_funcional = col4.text_input("ID Funcional")
        posto = col5.text_input("Posto / Graduação")
        quadro = col6.text_input("Quadro / QBMP")

        telefone = st.text_input("Telefone")

        entrada = st.date_input("Data de entrada na REDEC")
        saida = st.date_input("Data de saída da REDEC")

        salvar = st.form_submit_button("Salvar")

        if salvar:
            supabase.table("equipe").insert({
                "nome": nome,
                "nome_guerra": nome_guerra,
                "rg": rg,
                "id_funcional": id_funcional,
                "posto": posto,
                "quadro": quadro,
                "telefone": telefone,
                "entrada_redec": str(entrada),
                "saida_redec": str(saida)
            }).execute()

            st.success("Membro cadastrado com sucesso!")

    st.divider()

    dados = supabase.table("equipe").select("*").execute().data
    if dados:
        df = pd.DataFrame(dados)
        st.dataframe(df, use_container_width=True)
