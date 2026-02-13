# services/historico.py

from datetime import date
from services.supabase import supabase


FUNCOES_UNICAS = ["Coordenador", "Subcoordenador"]


def buscar_historico():
    return supabase.table("historico_redec") \
        .select("*, equipe(nome)") \
        .order("data_entrada", desc=True) \
        .execute().data


def inserir_historico(dados):
    return supabase.table("historico_redec").insert(dados).execute()


def encerrar_funcao(funcao):
    hoje = date.today().isoformat()

    supabase.table("historico_redec") \
        .update({"data_saida": hoje}) \
        .eq("funcao", funcao) \
        .is_("data_saida", None) \
        .execute()


def trocar_funcao(equipe_id, funcao, data_entrada):

    # Apenas cargos únicos encerram o anterior
    if funcao in FUNCOES_UNICAS:
        encerrar_funcao(funcao)

    inserir_historico({
        "equipe_id": equipe_id,
        "funcao": funcao,
        "data_entrada": str(data_entrada)
    })
