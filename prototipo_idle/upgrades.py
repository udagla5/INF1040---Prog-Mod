# =============================================================================
# upgrades.py — TAD Upgrades
# Responsável: David Pinto Coelho Benech
# INF1040 · 2026.1 · Grupo 3WB
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
    return id_upgrade in estado_upg['catalogo']

def _ja_comprado(estado_upg, id_upgrade):
    return id_upgrade in estado_upg['comprados']

# ---------------------------------------------------------------------------
# Interface pública
# ---------------------------------------------------------------------------
def inicializar_upgrades():
    estado = {
        'catalogo':  dict(UPGRADES_CATALOGO),
        'comprados': [],
    }
    return (0, estado)

def listar_disponiveis(estado_upg):
    comprados  = estado_upg['comprados']
    disponiveis = [
        dados for id_, dados in estado_upg['catalogo'].items()
        if id_ not in comprados
    ]
    return (0, disponiveis)

def listar_comprados(estado_upg):
    catalogo  = estado_upg['catalogo']
    comprados = [
        catalogo[id_] for id_ in estado_upg['comprados']
        if id_ in catalogo
    ]
    return (0, comprados)

def listar_por_gerador(estado_upg, id_gerador):
    if id_gerador not in GERADORES_CATALOGO:
        return (-1, None)
    resultado = [
        dados for dados in estado_upg['catalogo'].values()
        if dados['alvo'] == id_gerador
    ]
    return (0, resultado)

def obter_upgrade(estado_upg, id_upgrade):
    if id_upgrade not in estado_upg['catalogo']:
        return (-1, None)
    return (0, estado_upg['catalogo'][id_upgrade])

def pode_comprar(estado_upg, estado_eco, id_upgrade):
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
    fatores = {id_: 1.0 for id_ in GERADORES_CATALOGO}
    for id_upg in estado_upg['comprados']:
        if id_upg in estado_upg['catalogo']:
            dados = estado_upg['catalogo'][id_upg]
            alvo  = dados['alvo']
            if alvo in fatores:
                fatores[alvo] *= dados['fator']
    return (0, fatores)
