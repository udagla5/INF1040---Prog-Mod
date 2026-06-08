# =============================================================================
# progresso.py — TAD Progresso
# Responsável: Leonardo Dana Edelsberg
# INF1040 · 2026.1 · Grupo 3WB
# =============================================================================

import math
import economia
from constantes import (
    MARCOS_CATALOGO, LIMIARES_NIVEL, NIVEL_MAXIMO,
    LIMIAR_REVOLUCAO_BASE, FATOR_LIMIAR_REVOLUCAO,
    REVOLUCOES_P_ASCENSAO, PONTO_OMEGA,
    MULT_POR_CRISTAL, EXP_POR_FRAGMENTO, GERADORES_CATALOGO,
)

__all__ = [
    'inicializar_progresso', 'calcular_nivel', 'verificar_progresso',
    'obter_marcos_atingidos', 'obter_proximos_marcos',
    'pode_revolucao', 'executar_revolucao',
    'pode_ascensao', 'executar_ascensao',
    'verificar_vitoria',
]

# ---------------------------------------------------------------------------
# Funções internas
# ---------------------------------------------------------------------------
def _limiar_revolucao(num_revolucoes):
    return LIMIAR_REVOLUCAO_BASE * (FATOR_LIMIAR_REVOLUCAO ** num_revolucoes)

def _cristais_ganhos(pontos_run_max, num_revolucoes):
    limiar = _limiar_revolucao(num_revolucoes)
    if pontos_run_max < limiar:
        return 0
    return max(1, int(math.floor(math.sqrt(pontos_run_max / limiar))))

# ---------------------------------------------------------------------------
# Interface pública
# ---------------------------------------------------------------------------
def inicializar_progresso():
    estado = {
        'nivel':                      1,
        'marcos_atingidos':           [],
        'cristais_revolucao':         0,
        'num_revolucoes':             0,
        'laboratorios_desbloqueados': False,
        'fragmentos_ascensao':        0,
        'num_ascensoes':              0,
        'vitoria':                    False,
    }
    return (0, estado)

def calcular_nivel(estado_eco):
    _, pontos_max = economia.obter_pontos_run_max(estado_eco)
    nivel = 1
    for i, limiar in enumerate(LIMIARES_NIVEL):
        if pontos_max >= limiar:
            nivel = i + 1
    return (0, min(nivel, NIVEL_MAXIMO))

def verificar_progresso(estado_eco, estado_prog):
    _, pontos_max = economia.obter_pontos_run_max(estado_eco)
    atingidos     = list(estado_prog['marcos_atingidos'])
    novos         = []

    for marco in MARCOS_CATALOGO:
        if marco['id'] in atingidos:
            continue
        if marco['tipo'] == 'pontos' and marco['limiar'] is not None:
            if pontos_max >= marco['limiar']:
                atingidos.append(marco['id'])
                novos.append(marco['id'])
        elif marco['tipo'] == 'evento' and marco['id'] == 'marco_laboratorio':
            for id_ger, dados in GERADORES_CATALOGO.items():
                if dados['categoria'] == 'laboratorio':
                    _, qtd = economia.obter_quantidade_gerador(estado_eco, id_ger)
                    if qtd and qtd > 0:
                        atingidos.append(marco['id'])
                        novos.append(marco['id'])
                        break

    _, nivel  = calcular_nivel(estado_eco)
    novo_prog = {**estado_prog, 'marcos_atingidos': atingidos, 'nivel': nivel}
    return (0, novo_prog, novos)

def obter_marcos_atingidos(estado_prog):
    return (0, list(estado_prog['marcos_atingidos']))

def obter_proximos_marcos(estado_prog):
    atingidos = estado_prog['marcos_atingidos']
    proximos  = [m for m in MARCOS_CATALOGO if m['id'] not in atingidos]
    return (0, proximos)

def pode_revolucao(estado_eco, estado_prog):
    _, pontos_max = economia.obter_pontos_run_max(estado_eco)
    limiar        = _limiar_revolucao(estado_prog['num_revolucoes'])
    return (0, pontos_max >= limiar)

def executar_revolucao(estado_eco, estado_prog):
    _, pode = pode_revolucao(estado_eco, estado_prog)
    if not pode:
        return (-2, estado_eco, estado_prog)

    _, pontos_max    = economia.obter_pontos_run_max(estado_eco)
    cristais_ganhos  = _cristais_ganhos(pontos_max, estado_prog['num_revolucoes'])
    novos_cristais   = estado_prog['cristais_revolucao'] + cristais_ganhos
    novo_num_revol   = estado_prog['num_revolucoes'] + 1

    atingidos = list(estado_prog['marcos_atingidos'])
    if 'marco_revolucao' not in atingidos:
        atingidos.append('marco_revolucao')

    novo_prog = {
        **estado_prog,
        'cristais_revolucao':         novos_cristais,
        'num_revolucoes':             novo_num_revol,
        'laboratorios_desbloqueados': True,
        'marcos_atingidos':           atingidos,
    }

    _, eco_novo = economia.aplicar_multiplicador_revolucao(estado_eco, novos_cristais)
    eco_novo    = {**eco_novo, 'laboratorios_desbloqueados': True}
    _, eco_novo = economia.resetar_run(eco_novo)
    eco_novo    = {**eco_novo, 'laboratorios_desbloqueados': True}

    # Após o reset, geradores e pontos voltam a zero. Com taxa_base == 0
    # o multiplicador nunca é aplicado e o jogador fica sem renda.
    # Devolve 2 mineradoras iniciais para garantir produção imediata.
    _, eco_novo = economia.adicionar_gerador(eco_novo, 'mineradora_vermelha')
    _, eco_novo = economia.adicionar_gerador(eco_novo, 'mineradora_vermelha')

    return (0, eco_novo, novo_prog)

def pode_ascensao(estado_prog):
    return (0, estado_prog['num_revolucoes'] >= REVOLUCOES_P_ASCENSAO)

def executar_ascensao(estado_eco, estado_prog):
    _, pode = pode_ascensao(estado_prog)
    if not pode:
        return (-2, estado_eco, estado_prog)

    novos_fragmentos = estado_prog['fragmentos_ascensao'] + 1

    atingidos = list(estado_prog['marcos_atingidos'])
    if 'marco_ascensao' not in atingidos:
        atingidos.append('marco_ascensao')

    novo_prog = {
        **estado_prog,
        'fragmentos_ascensao': novos_fragmentos,
        'num_ascensoes':       estado_prog['num_ascensoes'] + 1,
        'cristais_revolucao':  0,
        'num_revolucoes':      0,
        'marcos_atingidos':    atingidos,
    }

    _, eco_novo = economia.aplicar_expoente_ascensao(estado_eco, novos_fragmentos)
    _, eco_novo = economia.resetar_run(eco_novo)

    # Mesmo motivo da revolução: sem geradores o expoente nunca é aplicado.
    _, eco_novo = economia.adicionar_gerador(eco_novo, 'mineradora_vermelha')
    _, eco_novo = economia.adicionar_gerador(eco_novo, 'mineradora_vermelha')

    return (0, eco_novo, novo_prog)

def verificar_vitoria(estado_eco, estado_prog):
    if estado_prog['vitoria']:
        return (0, estado_prog, True)
    _, pontos = economia.obter_pontos(estado_eco)
    if pontos >= PONTO_OMEGA:
        atingidos = list(estado_prog['marcos_atingidos'])
        if 'marco_omega' not in atingidos:
            atingidos.append('marco_omega')
        novo_prog = {**estado_prog, 'vitoria': True, 'marcos_atingidos': atingidos}
        return (0, novo_prog, True)
    return (0, estado_prog, False)
