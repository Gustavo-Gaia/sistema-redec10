# services/ferias.py

from supabase import create_client
import streamlit as st

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

supabase = create_client(url, key)

def buscar_ferias():
    return supabase.table("ferias_licencas") \
        .select("*, equipe(nome)") \
        .order("inicio", desc=True) \
        .execute().data

def inserir_ferias(dados):
    return supabase.table("ferias_licencas").insert(dados).execute()
