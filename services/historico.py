# services/historico.py

from datetime import date
from services.supabase import supabase

# Constantes para lógica de negócio
FUNCOES_UNICAS = ["Coordenador", "Subcoordenador"]

def buscar_historico():
    """
    Busca todo o histórico de funções, incluindo dados relacionados do militar.
    """
    return supabase.table("historico_redec") \
        .select("*, equipe(nome, posto_graduacao)") \
        .order("data_entrada", desc=True) \
        .execute().data

def inserir_historico(dados):
    """Insere um novo registro de função no histórico."""
    return supabase.table("historico_redec").insert(dados).execute()

def encerrar_funcao(funcao, data_saida):
    """
    Define a data de saída para o ocupante atual de uma função específica.
    Agora recebe 'data_saida' como parâmetro para garantir a continuidade 
    com o sucessor.
    """
    # Usamos o filtro 'is.null' para garantir que estamos encerrando apenas 
    # o registro que ainda está aberto (ativo)
    return supabase.table("historico_redec") \
        .update({"data_saida": str(data_saida)}) \
        .eq("funcao", funcao) \
        .is_("data_saida", "null") \
        .execute()

def trocar_funcao(equipe_id, funcao, data_entrada):
    """
    Lógica principal para troca de cargos. 
    Garante que cargos únicos tenham sucessão linear de datas.
    """
    # 1. Se a função for única (Coordenador/Sub), encerra o anterior 
    # na exata data em que o novo está entrando.
    if funcao in FUNCOES_UNICAS:
        encerrar_funcao(funcao, data_entrada)

    # 2. Insere o novo ocupante. 
    # Explicitamos 'data_saida': None para garantir que o registro entre aberto.
    return inserir_historico({
        "equipe_id": equipe_id,
        "funcao": funcao,
        "data_entrada": str(data_entrada),
        "data_saida": None
    })
