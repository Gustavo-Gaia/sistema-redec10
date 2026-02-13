# services/historico.py

from supabase import create_client
import streamlit as st

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

supabase = create_client(url, key)

def buscar_historico():
    return supabase.table("historico_redec") \
        .select("*, equipe(nome)") \
        .order("data_entrada", desc=True) \
        .execute().data

def inserir_historico(dados):
    return supabase.table("historico_redec").insert(dados).execute()
