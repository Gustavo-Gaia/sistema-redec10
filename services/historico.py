# services/historico.py

from datetime import date
from services.supabase import supabase

# Apenas o Coordenador exige a lógica de encerrar o anterior na mesma data
# O Subcoordenador agora segue o fluxo normal, conforme sua solicitação
FUNCAO_COM_SUCESSAO_ESTRITA = "Coordenador"

def buscar_historico():
    """Busca todo o histórico de funções com os dados do militar vinculado."""
    return supabase.table("historico_redec") \
        .select("*, equipe(nome, posto_graduacao)") \
        .order("data_entrada", desc=True) \
        .execute().data

def inserir_historico(dados):
    """Insere um novo registro de função no histórico."""
    return supabase.table("historico_redec").insert(dados).execute()

def encerrar_mandato_anterior(funcao, data_saida):
    """
    Localiza o ocupante atual (data_saida nula) da função e define sua saída.
    A data de saída será exatamente a data de entrada do novo sucessor.
    """
    return supabase.table("historico_redec") \
        .update({"data_saida": str(data_saida)}) \
        .eq("funcao", funcao) \
        .is_("data_saida", "null") \
        .execute()

def trocar_funcao(equipe_id, funcao, data_entrada):
    """
    Lógica de troca de função. 
    Se for Coordenador, encerra o anterior automaticamente para não haver vacância.
    """
    # Lógica de continuidade automática apenas para o Coordenador
    if funcao == FUNCAO_COM_SUCESSAO_ESTRITA:
        encerrar_mandato_anterior(funcao, data_entrada)

    # Inserção do novo registro
    # Forçamos data_saida como None para garantir que ele seja o atual "Ativo"
    return inserir_historico({
        "equipe_id": equipe_id,
        "funcao": funcao,
        "data_entrada": str(data_entrada),
        "data_saida": None
    })
