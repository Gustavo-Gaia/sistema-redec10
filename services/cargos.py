# services/cargos.py

from supabase import create_client
import streamlit as st

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

supabase = create_client(url, key)

def ocupante_atual(funcao):
    return supabase.table("historico_redec") \
        .select("id, data_entrada, equipe(nome)") \
        .eq("funcao", funcao) \
        .is_("data_saida", "null") \
        .execute().data

def historico(funcao):
    return supabase.table("historico_redec") \
        .select("id, data_entrada, data_saida, equipe(nome)") \
        .eq("funcao", funcao) \
        .order("data_entrada", desc=True) \
        .execute().data

def trocar(novo_id, funcao):
    supabase.table("historico_redec") \
        .update({"data_saida": "now()"}) \
        .eq("funcao", funcao) \
        .is_("data_saida", "null") \
        .execute()

    supabase.table("historico_redec").insert({
        "equipe_id": novo_id,
        "funcao": funcao,
        "data_entrada": "now()"
    }).execute()
