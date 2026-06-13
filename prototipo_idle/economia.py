# =============================================================================
# economia.py — TAD Economia
# Responsável: Rafael Carvalho Solberg
# INF1040 - 2026.1 - Grupo 2
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
    """
    Retorna a produção base de um gerador pelo seu id.

    Assertiva de entrada:
        id_gerador (str) — qualquer string (inclusive inválida)

    Assertiva de saída:
        float >= 0.0 — produção base se o gerador existir no catálogo;
                       0.0 se id_gerador não for encontrado
    """
    if id_gerador not in GERADORES_CATALOGO:
        return 0.0
    return GERADORES_CATALOGO[id_gerador]['prod_base']

def _gerador_bloqueado(estado, id_gerador):
    """
    Verifica se um gerador está bloqueado para o estado dado.

    Assertiva de entrada:
        estado     (dict) — estado válido retornado por inicializar_estado
        id_gerador (str)  — qualquer string

    Assertiva de saída:
        True  — gerador inexistente, ou categoria laboratório sem desbloqueio
        False — gerador disponível para compra
    """
    if id_gerador not in GERADORES_CATALOGO:
        return True
    if GERADORES_CATALOGO[id_gerador]['bloqueado']:
        return not estado.get('laboratorios_desbloqueados', False)
    return False

def _custo_unitario(id_gerador, unidades_possuidas):
    """
    Calcula o custo de uma única unidade adicional com escala exponencial.

    Assertiva de entrada:
        id_gerador         (str) — deve existir em GERADORES_CATALOGO
        unidades_possuidas (int) — >= 0

    Assertiva de saída:
        float > 0.0 — custo da próxima unidade
    """
    custo_base = GERADORES_CATALOGO[id_gerador]['custo_base']
    return custo_base * (ESCALA_CUSTO_GERADOR ** unidades_possuidas)

# ---------------------------------------------------------------------------
# Interface pública
# ---------------------------------------------------------------------------
def inicializar_estado():
    """
    Cria e retorna um estado econômico inicial zerado.

    Assertiva de entrada:
        (nenhuma)

    Assertiva de saída:
        (0, dict) — estado com pontos=0, geradores todos em 0,
                    multiplicador_revolucao=1.0, expoente_ascensao=1.0
    """
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
    """
    Lê a quantidade atual de pontos do estado.

    Assertiva de entrada:
        estado (dict) — estado válido retornado por inicializar_estado

    Assertiva de saída:
        (0, float >= 0.0) — valor de estado['pontos']
    """
    return (0, estado['pontos'])

def obter_pontos_run_max(estado):
    """
    Lê o máximo de pontos atingido na run atual.

    Assertiva de entrada:
        estado (dict) — estado válido retornado por inicializar_estado

    Assertiva de saída:
        (0, float >= 0.0) — valor de estado['pontos_run_max']
    """
    return (0, estado['pontos_run_max'])

def obter_multiplicador_revolucao(estado):
    """
    Lê o multiplicador global de produção (efeito de cristais da Revolução).

    Assertiva de entrada:
        estado (dict) — estado válido retornado por inicializar_estado

    Assertiva de saída:
        (0, float >= 1.0) — valor de estado['multiplicador_revolucao']
    """
    return (0, estado['multiplicador_revolucao'])

def obter_expoente_ascensao(estado):
    """
    Lê o expoente de produção (efeito de fragmentos da Ascensão).

    Assertiva de entrada:
        estado (dict) — estado válido retornado por inicializar_estado

    Assertiva de saída:
        (0, float >= 1.0) — valor de estado['expoente_ascensao']
    """
    return (0, estado['expoente_ascensao'])

def obter_quantidade_gerador(estado, id_gerador):
    """
    Lê a quantidade possuída de um tipo de gerador.

    Assertiva de entrada:
        estado     (dict) — estado válido retornado por inicializar_estado
        id_gerador (str)  — qualquer string

    Assertiva de saída:
        ( 0, int >= 0) — quantidade atual do gerador
        (-1, None)     — id_gerador não existe em estado['geradores']
    """
    if id_gerador not in estado['geradores']:
        return (-1, None)
    return (0, estado['geradores'][id_gerador])

def pode_gastar(estado, valor):
    """
    Verifica se o jogador possui pontos suficientes para gastar o valor dado.

    Assertiva de entrada:
        estado (dict)         — estado válido retornado por inicializar_estado
        valor  (int ou float) — deve ser > 0

    Assertiva de saída:
        ( 0, True)  — pontos >= valor
        ( 0, False) — pontos < valor
        (-1, None)  — valor inválido (não numérico ou <= 0)
    """
    if not isinstance(valor, (int, float)) or valor <= 0:
        return (-1, None)
    return (0, estado['pontos'] >= valor)

def gastar_pontos(estado, valor):
    """
    Subtrai um valor dos pontos do jogador, retornando novo estado imutável.

    Assertiva de entrada:
        estado (dict)         — estado válido retornado por inicializar_estado
        valor  (int ou float) — deve ser > 0 e <= estado['pontos']

    Assertiva de saída:
        ( 0, novo_estado) — pontos descontados; novo_estado['pontos'] = pontos - valor
        (-1, estado)      — valor inválido (não numérico ou <= 0)
        (-2, estado)      — pontos insuficientes (estado['pontos'] < valor)
    """
    if not isinstance(valor, (int, float)) or valor <= 0:
        return (-1, estado)
    if estado['pontos'] < valor:
        return (-2, estado)
    novo = {**estado, 'pontos': estado['pontos'] - valor}
    return (0, novo)

def adicionar_pontos(estado, valor):
    """
    Acrescenta pontos ao estado, atualizando também pontos_run_max se necessário.

    Assertiva de entrada:
        estado (dict)         — estado válido retornado por inicializar_estado
        valor  (int ou float) — deve ser > 0

    Assertiva de saída:
        ( 0, novo_estado) — pontos e pontos_run_max atualizados
        (-1, estado)      — valor inválido (não numérico ou <= 0)
    """
    if not isinstance(valor, (int, float)) or valor <= 0:
        return (-1, estado)
    novo_pontos = estado['pontos'] + valor
    novo_max    = max(estado['pontos_run_max'], novo_pontos)
    novo = {**estado, 'pontos': novo_pontos, 'pontos_run_max': novo_max}
    return (0, novo)

def adicionar_gerador(estado, id_gerador, quantidade=1):
    """
    Incrementa a quantidade de um gerador no estado sem deduzir pontos.

    Assertiva de entrada:
        estado     (dict) — estado válido retornado por inicializar_estado
        id_gerador (str)  — deve existir em GERADORES_CATALOGO
        quantidade (int)  — >= 1 (padrão 1)

    Assertiva de saída:
        ( 0, novo_estado) — estado['geradores'][id_gerador] += quantidade
        (-1, estado)      — id_gerador não existe no catálogo
        (-4, estado)      — gerador bloqueado (laboratórios sem revolução)
    """
    if id_gerador not in GERADORES_CATALOGO:
        return (-1, estado)
    if _gerador_bloqueado(estado, id_gerador):
        return (-4, estado)
    novo_gers = dict(estado['geradores'])
    novo_gers[id_gerador] = novo_gers[id_gerador] + quantidade
    novo = {**estado, 'geradores': novo_gers}
    return (0, novo)

def calcular_custo_gerador(estado, id_gerador, quantidade=1):
    """
    Calcula o custo total para comprar N unidades de um gerador.

    Assertiva de entrada:
        estado     (dict) — estado válido retornado por inicializar_estado
        id_gerador (str)  — deve existir em GERADORES_CATALOGO
        quantidade (int)  — >= 1 (padrão 1)

    Assertiva de saída:
        ( 0, float > 0) — custo cumulativo considerando escala exponencial
        (-1, None)      — id_gerador não existe no catálogo
        (-4, None)      — gerador bloqueado (laboratórios sem revolução)
    """
    if id_gerador not in GERADORES_CATALOGO:
        return (-1, None)
    if _gerador_bloqueado(estado, id_gerador):
        return (-4, None)
    possuidas    = estado['geradores'][id_gerador]
    custo_total  = sum(_custo_unitario(id_gerador, possuidas + i) for i in range(quantidade))
    return (0, custo_total)

def calcular_taxa_base(estado):
    """
    Soma a produção de todos os geradores sem aplicar multiplicador ou expoente.

    Assertiva de entrada:
        estado (dict) — estado válido retornado por inicializar_estado

    Assertiva de saída:
        (0, float >= 0.0) — taxa base total em pontos/s
    """
    taxa = 0.0
    for id_ger, qtd in estado['geradores'].items():
        if qtd > 0:
            prod   = GERADORES_CATALOGO[id_ger]['prod_base']
            fator  = estado['fatores_upgrades'].get(id_ger, 1.0)
            taxa  += qtd * prod * fator
    return (0, taxa)

def calcular_taxa_total(estado):
    """
    Calcula a taxa de produção final aplicando multiplicador e expoente.

    Fórmula: (taxa_base * multiplicador_revolucao) ^ expoente_ascensao

    Assertiva de entrada:
        estado (dict) — estado válido retornado por inicializar_estado

    Assertiva de saída:
        (0, float >= 0.0) — taxa total em pontos/s;
                            retorna 0.0 se taxa_base <= 0
    """
    _, taxa_base = calcular_taxa_base(estado)
    mult = estado['multiplicador_revolucao']
    exp  = estado['expoente_ascensao']
    if taxa_base <= 0:
        return (0, 0.0)
    taxa_total = (taxa_base * mult) ** exp
    return (0, taxa_total)

def aplicar_geracao(estado, delta_tempo):
    """
    Avança a simulação pelo tempo decorrido, acumulando pontos gerados.

    Assertiva de entrada:
        estado      (dict)        — estado válido retornado por inicializar_estado
        delta_tempo (int ou float) — >= 0; segundos desde o último tick

    Assertiva de saída:
        ( 0, novo_estado) — pontos e pontos_run_max atualizados
        (-1, estado)      — delta_tempo inválido (não numérico ou < 0)
    """
    if not isinstance(delta_tempo, (int, float)) or delta_tempo < 0:
        return (-1, estado)
    _, taxa      = calcular_taxa_total(estado)
    novo_pontos  = estado['pontos'] + taxa * delta_tempo
    novo_max     = max(estado['pontos_run_max'], novo_pontos)
    novo = {**estado, 'pontos': novo_pontos, 'pontos_run_max': novo_max}
    return (0, novo)

def aplicar_multiplicador_revolucao(estado, cristais):
    """
    Recalcula e aplica o multiplicador de produção com base nos cristais acumulados.

    Fórmula: multiplicador = 1.0 + cristais * MULT_POR_CRISTAL

    Assertiva de entrada:
        estado   (dict) — estado válido retornado por inicializar_estado
        cristais (int)  — >= 0; total de cristais acumulados após a revolução

    Assertiva de saída:
        ( 0, novo_estado) — multiplicador_revolucao atualizado
        (-1, estado)      — cristais inválido (não inteiro ou < 0)
    """
    if not isinstance(cristais, int) or cristais < 0:
        return (-1, estado)
    mult = 1.0 + cristais * MULT_POR_CRISTAL
    return (0, {**estado, 'multiplicador_revolucao': mult})

def aplicar_expoente_ascensao(estado, fragmentos):
    """
    Recalcula e aplica o expoente de produção com base nos fragmentos acumulados.

    Fórmula: expoente = 1.0 + fragmentos * EXP_POR_FRAGMENTO

    Assertiva de entrada:
        estado     (dict) — estado válido retornado por inicializar_estado
        fragmentos (int)  — >= 0; total de fragmentos acumulados após a ascensão

    Assertiva de saída:
        ( 0, novo_estado) — expoente_ascensao atualizado
        (-1, estado)      — fragmentos inválido (não inteiro ou < 0)
    """
    if not isinstance(fragmentos, int) or fragmentos < 0:
        return (-1, estado)
    exp = 1.0 + fragmentos * EXP_POR_FRAGMENTO
    return (0, {**estado, 'expoente_ascensao': exp})

def aplicar_efeitos_upgrades(estado, fatores):
    """
    Atualiza os fatores de produção dos geradores conforme upgrades comprados.

    Assertiva de entrada:
        estado  (dict) — estado válido retornado por inicializar_estado
        fatores (dict) — mapeamento {id_gerador: float}; obtido de
                         upgrades.calcular_fatores_por_gerador

    Assertiva de saída:
        ( 0, novo_estado) — fatores_upgrades atualizados para geradores conhecidos
        (-1, estado)      — fatores não é um dict
    """
    if not isinstance(fatores, dict):
        return (-1, estado)
    novo_fatores = dict(estado['fatores_upgrades'])
    for id_ger, fator in fatores.items():
        if id_ger in novo_fatores:
            novo_fatores[id_ger] = fator
    return (0, {**estado, 'fatores_upgrades': novo_fatores})

def resetar_run(estado):
    """
    Zera pontos, pontos_run_max, todos os geradores e fatores de upgrades.

    Chamado ao executar Revolução ou Ascensão. Preserva multiplicador,
    expoente e flag laboratorios_desbloqueados.

    Assertiva de entrada:
        estado (dict) — estado válido retornado por inicializar_estado

    Assertiva de saída:
        (0, novo_estado) — pontos=0.0, geradores todos=0, fatores todos=1.0;
                           multiplicador_revolucao e expoente_ascensao mantidos
    """
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
