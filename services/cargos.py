# services/cargos.py

from supabase import create_client
import streamlit as st

# Configurações de conexão com o Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

supabase = create_client(url, key)

def ocupante_atual(funcao):
    """
    Retorna o militar que ocupa atualmente a função informada.
    Inclui o posto_graduacao para correta exibição nos cards e componentes.
    """
    return supabase.table("historico_redec") \
        .select("id, data_entrada, equipe(nome, posto_graduacao)") \
        .eq("funcao", funcao) \
        .is_("data_saida", "null") \
        .execute().data

def historico(funcao):
    """
    Retorna a lista histórica de todos os militares que já ocuparam a função.
    Ajustado para trazer nome e posto da tabela equipe.
    """
    return supabase.table("historico_redec") \
        .select("id, data_entrada, data_saida, equipe(nome, posto_graduacao)") \
        .eq("funcao", funcao) \
        .order("data_entrada", desc=True) \
        .execute().data

def trocar(novo_id, funcao):
    """
    Encerra a ocupação atual de um cargo e insere um novo militar.
    Utiliza o timestamp do banco (now()) para garantir precisão cronológica.
    """
    # 1. Finaliza o mandato do ocupante anterior
    supabase.table("historico_redec") \
        .update({"data_saida": "now()"}) \
        .eq("funcao", funcao) \
        .is_("data_saida", "null") \
        .execute()

    # 2. Insere o novo ocupante
    return supabase.table("historico_redec").insert({
        "equipe_id": novo_id,
        "funcao": funcao,
        "data_entrada": "now()"
    }).execute()
