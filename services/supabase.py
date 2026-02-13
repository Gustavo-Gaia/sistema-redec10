# services/supabase.py

from supabase import create_client
import streamlit as st

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

supabase = create_client(url, key)

def buscar_equipe():
    response = supabase.table("equipe").select("*").order("nome").execute()
    return response.data

def inserir_membro(dados):
    return supabase.table("equipe").insert(dados).execute()

def atualizar_membro(id, dados):
    return supabase.table("equipe").update(dados).eq("id", id).execute()

def excluir_membro(id):
    return supabase.table("equipe").delete().eq("id", id).execute()

