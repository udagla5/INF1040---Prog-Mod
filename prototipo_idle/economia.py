# =============================================================================
# economia.py — TAD Economia
# Responsável: Rafael Carvalho Solberg
# INF1040 · 2026.1 · Grupo 3WB
# =============================================================================

import math
from constantes import (
    GERADORES_CATALOGO, ESCALA_CUSTO_GERADOR,
    MULT_POR_CRISTAL, EXP_POR_FRAGMENTO
)

__all__ = [
    'inicializar_estado', 'obter_pontos', 'obter_pontos_run_max',
    'obter_multiplicador_revolucao', 'obter_expoente_ascensao',
    'obter_quantidade_gerador', 'pode_gastar', 'gastar_pontos',
    'adicionar_pontos', 'adicionar_gerador', 'calcular_custo_gerador',
    'calcular_taxa_base', 'calcular_taxa_total', 'aplicar_geracao',
    'aplicar_multiplicador_revolucao', 'aplicar_expoente_ascensao',
    'aplicar_efeitos_upgrades', 'resetar_run',
]

# ---------------------------------------------------------------------------
# Funções internas
# ---------------------------------------------------------------------------
def _prod_base_gerador(id_gerador):
    if id_gerador not in GERADORES_CATALOGO:
        return 0.0
    return GERADORES_CATALOGO[id_gerador]['prod_base']

def _gerador_bloqueado(estado, id_gerador):
    if id_gerador not in GERADORES_CATALOGO:
        return True
    if GERADORES_CATALOGO[id_gerador]['bloqueado']:
        return not estado.get('laboratorios_desbloqueados', False)
    return False

def _custo_unitario(id_gerador, unidades_possuidas):
    custo_base = GERADORES_CATALOGO[id_gerador]['custo_base']
    return custo_base * (ESCALA_CUSTO_GERADOR ** unidades_possuidas)

# ---------------------------------------------------------------------------
# Interface pública
# ---------------------------------------------------------------------------
def inicializar_estado():
    geradores         = {id_: 0   for id_ in GERADORES_CATALOGO}
    fatores_upgrades  = {id_: 1.0 for id_ in GERADORES_CATALOGO}
    estado = {
        'pontos':                    0.0,
        'pontos_run_max':            0.0,
        'multiplicador_revolucao':   1.0,
        'expoente_ascensao':         1.0,
        'laboratorios_desbloqueados': False,
        'geradores':                 geradores,
        'fatores_upgrades':          fatores_upgrades,
    }
    return (0, estado)

def obter_pontos(estado):
    return (0, estado['pontos'])

def obter_pontos_run_max(estado):
    return (0, estado['pontos_run_max'])

def obter_multiplicador_revolucao(estado):
    return (0, estado['multiplicador_revolucao'])

def obter_expoente_ascensao(estado):
    return (0, estado['expoente_ascensao'])

def obter_quantidade_gerador(estado, id_gerador):
    if id_gerador not in estado['geradores']:
        return (-1, None)
    return (0, estado['geradores'][id_gerador])

def pode_gastar(estado, valor):
    if not isinstance(valor, (int, float)) or valor <= 0:
        return (-1, None)
    return (0, estado['pontos'] >= valor)

def gastar_pontos(estado, valor):
    if not isinstance(valor, (int, float)) or valor <= 0:
        return (-1, estado)
    if estado['pontos'] < valor:
        return (-2, estado)
    novo = {**estado, 'pontos': estado['pontos'] - valor}
    return (0, novo)

def adicionar_pontos(estado, valor):
    if not isinstance(valor, (int, float)) or valor <= 0:
        return (-1, estado)
    novo_pontos = estado['pontos'] + valor
    novo_max    = max(estado['pontos_run_max'], novo_pontos)
    novo = {**estado, 'pontos': novo_pontos, 'pontos_run_max': novo_max}
    return (0, novo)

def adicionar_gerador(estado, id_gerador, quantidade=1):
    if id_gerador not in GERADORES_CATALOGO:
        return (-1, estado)
    if _gerador_bloqueado(estado, id_gerador):
        return (-4, estado)
    novo_gers = dict(estado['geradores'])
    novo_gers[id_gerador] = novo_gers[id_gerador] + quantidade
    novo = {**estado, 'geradores': novo_gers}
    return (0, novo)

def calcular_custo_gerador(estado, id_gerador, quantidade=1):
    if id_gerador not in GERADORES_CATALOGO:
        return (-1, None)
    if _gerador_bloqueado(estado, id_gerador):
        return (-4, None)
    possuidas    = estado['geradores'][id_gerador]
    custo_total  = sum(_custo_unitario(id_gerador, possuidas + i) for i in range(quantidade))
    return (0, custo_total)

def calcular_taxa_base(estado):
    taxa = 0.0
    for id_ger, qtd in estado['geradores'].items():
        if qtd > 0:
            prod   = GERADORES_CATALOGO[id_ger]['prod_base']
            fator  = estado['fatores_upgrades'].get(id_ger, 1.0)
            taxa  += qtd * prod * fator
    return (0, taxa)

def calcular_taxa_total(estado):
    _, taxa_base = calcular_taxa_base(estado)
    mult = estado['multiplicador_revolucao']
    exp  = estado['expoente_ascensao']
    if taxa_base <= 0:
        return (0, 0.0)
    taxa_total = (taxa_base * mult) ** exp
    return (0, taxa_total)

def aplicar_geracao(estado, delta_tempo):
    if not isinstance(delta_tempo, (int, float)) or delta_tempo < 0:
        return (-1, estado)
    _, taxa      = calcular_taxa_total(estado)
    novo_pontos  = estado['pontos'] + taxa * delta_tempo
    novo_max     = max(estado['pontos_run_max'], novo_pontos)
    novo = {**estado, 'pontos': novo_pontos, 'pontos_run_max': novo_max}
    return (0, novo)

def aplicar_multiplicador_revolucao(estado, cristais):
    if not isinstance(cristais, int) or cristais < 0:
        return (-1, estado)
    mult = 1.0 + cristais * MULT_POR_CRISTAL
    return (0, {**estado, 'multiplicador_revolucao': mult})

def aplicar_expoente_ascensao(estado, fragmentos):
    if not isinstance(fragmentos, int) or fragmentos < 0:
        return (-1, estado)
    exp = 1.0 + fragmentos * EXP_POR_FRAGMENTO
    return (0, {**estado, 'expoente_ascensao': exp})

def aplicar_efeitos_upgrades(estado, fatores):
    if not isinstance(fatores, dict):
        return (-1, estado)
    novo_fatores = dict(estado['fatores_upgrades'])
    for id_ger, fator in fatores.items():
        if id_ger in novo_fatores:
            novo_fatores[id_ger] = fator
    return (0, {**estado, 'fatores_upgrades': novo_fatores})

def resetar_run(estado):
    geradores_zerados = {id_: 0   for id_ in estado['geradores']}
    fatores_reset     = {id_: 1.0 for id_ in estado['fatores_upgrades']}
    novo = {
        **estado,
        'pontos':           0.0,
        'pontos_run_max':   0.0,
        'geradores':        geradores_zerados,
        'fatores_upgrades': fatores_reset,
    }
    return (0, novo)
