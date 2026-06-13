# =============================================================================
# upgrades.py — TAD Upgrades
# Responsável: David Pinto Coelho Benech
# INF1040 - 2026.1 - Grupo 2
# =============================================================================

import economia
from constantes import UPGRADES_CATALOGO, GERADORES_CATALOGO

__all__ = [
    'inicializar_upgrades', 'listar_disponiveis', 'listar_comprados',
    'listar_por_gerador', 'obter_upgrade', 'pode_comprar',
    'comprar_upgrade', 'calcular_fatores_por_gerador',
]

# ---------------------------------------------------------------------------
# Funções internas
# ---------------------------------------------------------------------------
def _upgrade_existe(estado_upg, id_upgrade):
    """
    Verifica se um upgrade existe no catálogo do estado.

    Assertiva de entrada:
        estado_upg (dict) — estado válido retornado por inicializar_upgrades
        id_upgrade (str)  — qualquer string

    Assertiva de saída:
        True  — id_upgrade está em estado_upg['catalogo']
        False — id_upgrade não encontrado
    """
    return id_upgrade in estado_upg['catalogo']

def _ja_comprado(estado_upg, id_upgrade):
    """
    Verifica se um upgrade já foi comprado nesta run.

    Assertiva de entrada:
        estado_upg (dict) — estado válido retornado por inicializar_upgrades
        id_upgrade (str)  — qualquer string

    Assertiva de saída:
        True  — id_upgrade está na lista estado_upg['comprados']
        False — upgrade ainda não comprado
    """
    return id_upgrade in estado_upg['comprados']

# ---------------------------------------------------------------------------
# Interface pública
# ---------------------------------------------------------------------------
def inicializar_upgrades():
    """
    Cria e retorna um estado de upgrades inicial com catálogo completo e sem compras.

    Assertiva de entrada:
        (nenhuma)

    Assertiva de saída:
        (0, dict) — estado com catalogo=cópia de UPGRADES_CATALOGO e comprados=[]
    """
    estado = {
        'catalogo':  dict(UPGRADES_CATALOGO),
        'comprados': [],
    }
    return (0, estado)

def listar_disponiveis(estado_upg):
    """
    Retorna todos os upgrades ainda não comprados.

    Assertiva de entrada:
        estado_upg (dict) — estado válido retornado por inicializar_upgrades

    Assertiva de saída:
        (0, list[dict]) — lista de dicts de upgrade não comprados;
                          pode ser lista vazia se todos foram comprados
    """
    comprados  = estado_upg['comprados']
    disponiveis = [
        dados for id_, dados in estado_upg['catalogo'].items()
        if id_ not in comprados
    ]
    return (0, disponiveis)

def listar_comprados(estado_upg):
    """
    Retorna os dados completos de todos os upgrades já comprados.

    Assertiva de entrada:
        estado_upg (dict) — estado válido retornado por inicializar_upgrades

    Assertiva de saída:
        (0, list[dict]) — lista de dicts de upgrade na ordem de compra;
                          pode ser lista vazia se nenhum foi comprado
    """
    catalogo  = estado_upg['catalogo']
    comprados = [
        catalogo[id_] for id_ in estado_upg['comprados']
        if id_ in catalogo
    ]
    return (0, comprados)

def listar_por_gerador(estado_upg, id_gerador):
    """
    Retorna todos os upgrades (comprados ou não) que afetam um gerador específico.

    Assertiva de entrada:
        estado_upg (dict) — estado válido retornado por inicializar_upgrades
        id_gerador (str)  — deve existir em GERADORES_CATALOGO

    Assertiva de saída:
        ( 0, list[dict]) — lista de upgrades cujo campo 'alvo' == id_gerador
        (-1, None)       — id_gerador não existe em GERADORES_CATALOGO
    """
    if id_gerador not in GERADORES_CATALOGO:
        return (-1, None)
    resultado = [
        dados for dados in estado_upg['catalogo'].values()
        if dados['alvo'] == id_gerador
    ]
    return (0, resultado)

def obter_upgrade(estado_upg, id_upgrade):
    """
    Retorna os dados de um upgrade pelo seu id.

    Assertiva de entrada:
        estado_upg (dict) — estado válido retornado por inicializar_upgrades
        id_upgrade (str)  — qualquer string

    Assertiva de saída:
        ( 0, dict) — dados do upgrade (id, nome, custo, fator, alvo)
        (-1, None) — id_upgrade não existe no catálogo
    """
    if id_upgrade not in estado_upg['catalogo']:
        return (-1, None)
    return (0, estado_upg['catalogo'][id_upgrade])

def pode_comprar(estado_upg, estado_eco, id_upgrade):
    """
    Verifica se o jogador pode comprar um upgrade (existência, não comprado, pontos).

    Assertiva de entrada:
        estado_upg (dict) — estado válido retornado por inicializar_upgrades
        estado_eco (dict) — estado válido retornado por economia.inicializar_estado
        id_upgrade (str)  — qualquer string

    Assertiva de saída:
        ( 0, True)  — upgrade existe, não foi comprado e há pontos suficientes
        ( 0, False) — upgrade já comprado ou pontos insuficientes
        (-1, None)  — id_upgrade não existe no catálogo
    """
    if not _upgrade_existe(estado_upg, id_upgrade):
        return (-1, None)
    if _ja_comprado(estado_upg, id_upgrade):
        return (0, False)
    custo = estado_upg['catalogo'][id_upgrade]['custo']
    _, pode = economia.pode_gastar(estado_eco, custo)
    if pode is None:
        return (0, False)
    return (0, pode)

def comprar_upgrade(estado_upg, estado_eco, id_upgrade):
    """
    Compra um upgrade: desconta pontos e registra o upgrade como comprado.

    Assertiva de entrada:
        estado_upg (dict) — estado válido retornado por inicializar_upgrades
        estado_eco (dict) — estado válido retornado por economia.inicializar_estado
        id_upgrade (str)  — deve existir no catálogo e não ter sido comprado

    Assertiva de saída:
        ( 0, novo_upg, novo_eco) — upgrade adicionado a comprados; pontos deduzidos
        (-1, estado_upg, estado_eco) — id_upgrade não existe no catálogo
        (-2, estado_upg, estado_eco) — pontos insuficientes
        (-3, estado_upg, estado_eco) — upgrade já foi comprado anteriormente
    """
    if not _upgrade_existe(estado_upg, id_upgrade):
        return (-1, estado_upg, estado_eco)
    if _ja_comprado(estado_upg, id_upgrade):
        return (-3, estado_upg, estado_eco)
    custo    = estado_upg['catalogo'][id_upgrade]['custo']
    _, pode  = economia.pode_gastar(estado_eco, custo)
    if not pode:
        return (-2, estado_upg, estado_eco)
    _, eco_novo       = economia.gastar_pontos(estado_eco, custo)
    novos_comprados   = list(estado_upg['comprados']) + [id_upgrade]
    upg_novo          = {**estado_upg, 'comprados': novos_comprados}
    return (0, upg_novo, eco_novo)

def calcular_fatores_por_gerador(estado_upg):
    """
    Calcula o fator multiplicador acumulado de produção para cada gerador.

    Multiplica os fatores de todos os upgrades comprados que afetam cada gerador.

    Assertiva de entrada:
        estado_upg (dict) — estado válido retornado por inicializar_upgrades

    Assertiva de saída:
        (0, dict) — mapeamento {id_gerador: float >= 1.0} para todos os geradores;
                    geradores sem upgrades comprados têm fator 1.0
    """
    fatores = {id_: 1.0 for id_ in GERADORES_CATALOGO}
    for id_upg in estado_upg['comprados']:
        if id_upg in estado_upg['catalogo']:
            dados = estado_upg['catalogo'][id_upg]
            alvo  = dados['alvo']
            if alvo in fatores:
                fatores[alvo] *= dados['fator']
    return (0, fatores)
