# services/historico.py

from datetime import date
from services.supabase import supabase


# ===============================
# BUSCAR HISTÓRICO COMPLETO
# ===============================
def buscar_historico():
    return supabase.table("historico_redec") \
        .select("*, equipe(nome)") \
        .order("data_entrada", desc=True) \
        .execute().data


# ===============================
# INSERIR NOVO REGISTRO
# ===============================
def inserir_historico(dados):
    return supabase.table("historico_redec").insert(dados).execute()


# ===============================
# ENCERRAR FUNÇÃO ATUAL
# ===============================
def encerrar_funcao(funcao):
    hoje = date.today().isoformat()

    supabase.table("historico_redec") \
        .update({"data_saida": hoje}) \
        .eq("funcao", funcao) \
        .is_("data_saida", None) \
        .execute()


# ===============================
# TROCAR FUNÇÃO (SUBSTITUIÇÃO)
# ===============================
def trocar_funcao(equipe_id, funcao, data_entrada):
    # Fecha quem estava antes
    encerrar_funcao(funcao)

    # Insere novo ocupante
    inserir_historico({
        "equipe_id": equipe_id,
        "funcao": funcao,
        "data_entrada": str(data_entrada)
    })
