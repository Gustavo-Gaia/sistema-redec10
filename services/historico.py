# services/historico.py

from datetime import date
from services.supabase import supabase

# Constantes para lógica de negócio
FUNCOES_UNICAS = ["Coordenador", "Subcoordenador"]

def buscar_historico():
    """
    Busca todo o histórico de funções, incluindo dados relacionados do militar.
    Ajustado para incluir 'posto_graduacao' no select da tabela equipe.
    """
    # O segredo está em equipe(nome, posto_graduacao)
    return supabase.table("historico_redec") \
        .select("*, equipe(nome, posto_graduacao)") \
        .order("data_entrada", desc=True) \
        .execute().data

def inserir_historico(dados):
    """Insere um novo registro de função no histórico."""
    return supabase.table("historico_redec").insert(dados).execute()

def encerrar_funcao(funcao):
    """
    Define a data de saída como 'hoje' para o ocupante atual de uma função específica.
    Utilizado para garantir que Coordenadores e Subcoordenadores sejam substituídos corretamente.
    """
    hoje = date.today().isoformat()

    return supabase.table("historico_redec") \
        .update({"data_saida": hoje}) \
        .eq("funcao", funcao) \
        .is_("data_saida", None) \
        .execute()

def trocar_funcao(equipe_id, funcao, data_entrada):
    """
    Lógica principal para troca de cargos. 
    Se a função for única, encerra o mandato anterior antes de inserir o novo.
    """
    # Apenas cargos únicos encerram o ocupante anterior automaticamente
    if funcao in FUNCOES_UNICAS:
        encerrar_funcao(funcao)

    return inserir_historico({
        "equipe_id": equipe_id,
        "funcao": funcao,
        "data_entrada": str(data_entrada)
    })
