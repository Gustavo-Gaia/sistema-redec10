# supabase_client.py

from supabase import create_client
import streamlit as st

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

supabase = create_client(url, key)

def buscar_equipe():
    response = supabase.table("equipe").select("*").order("nome").execute()
    return response.data
