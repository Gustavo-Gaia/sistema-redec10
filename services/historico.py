# services/historico.py

from services.supabase import supabase


def buscar_historico():
    return supabase.table("historico_redec") \
        .select("*, equipe(nome)") \
        .order("data_entrada", desc=True) \
        .execute().data


def inserir_historico(dados):
    return supabase.table("historico_redec").insert(dados).execute()


def encerrar_funcao(funcao):
    supabase.table("historico_redec") \
        .update({"data_saida": "now()"}) \
        .eq("funcao", funcao) \
        .is_("data_saida", None) \
        .execute()


def trocar_funcao(equipe_id, funcao, data_entrada):
    # Fecha quem estava antes
    encerrar_funcao(funcao)

    # Insere novo ocupante
    inserir_historico({
        "equipe_id": equipe_id,
        "funcao": funcao,
        "data_entrada": str(data_entrada)
    })
