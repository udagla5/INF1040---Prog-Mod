# =============================================================================
# display.py — TAD Display
# Responsável: Carlos Eduardo Pimentel Bernardo
# INF1040 · 2026.1 · Grupo 3WB
# REGRA ABSOLUTA: zero chamadas a print() ou input() neste módulo.
# =============================================================================

import economia
import upgrades
import progresso
from constantes import (
    CATEGORIAS_ORDEM, GERADORES_CATALOGO, NIVEL_MAXIMO,
    LIMIAR_REVOLUCAO_BASE, FATOR_LIMIAR_REVOLUCAO, REVOLUCOES_P_ASCENSAO,
)

__all__ = [
    'renderizar_painel', 'montar_menu_comando', 'renderizar_pontos',
    'renderizar_geradores', 'renderizar_upgrades', 'renderizar_progresso',
    'renderizar_resets', 'formatar_numero',
]

# ---------------------------------------------------------------------------
# Funções internas
# ---------------------------------------------------------------------------
_SUFIXOS = [
    (1e48,'Qd'),(1e45,'Td'),(1e42,'Dd'),(1e39,'Nd'),(1e36,'Od'),
    (1e33,'Sd'),(1e30,'Vi'),(1e27,'Si'),(1e24,'Sp'),(1e21,'Sx'),
    (1e18,'Qi'),(1e15,'Qa'),(1e12,'T'),(1e9,'B'),(1e6,'M'),(1e3,'K'),
]

def _status_upgrade(id_upgrade, estado_upg, estado_eco):
    comprados_ids = [u['id'] for u in upgrades.listar_comprados(estado_upg)[1]]
    if id_upgrade in comprados_ids:
        return 'comprado'
    _, pode = upgrades.pode_comprar(estado_upg, estado_eco, id_upgrade)
    return 'disponivel' if pode else 'inacessivel'

# ---------------------------------------------------------------------------
# Interface pública
# ---------------------------------------------------------------------------
def formatar_numero(valor):
    if not isinstance(valor, (int, float)) or valor < 0:
        return (-1, None)
    for limiar, suf in _SUFIXOS:
        if valor >= limiar:
            return (0, f"{valor / limiar:.1f}{suf}")
    if valor == int(valor):
        return (0, str(int(valor)))
    return (0, f"{valor:.1f}")

def renderizar_pontos(estado_eco):
    _, pontos = economia.obter_pontos(estado_eco)
    _, taxa   = economia.calcular_taxa_total(estado_eco)
    _, mult   = economia.obter_multiplicador_revolucao(estado_eco)
    _, exp    = economia.obter_expoente_ascensao(estado_eco)
    _, ps     = formatar_numero(pontos)
    _, ts     = formatar_numero(taxa)
    sep = "═" * 54
    linhas = [
        f"╔{sep}",
        f"║  PONTOS : {ps:<18}  TAXA: +{ts}/s{'':<8}",
        f"║  Mult   : ×{mult:<8.2f}       Expoente: ^{exp:<8.2f}    ",
        f"╚{sep}",
    ]
    return (0, '\n'.join(linhas))

def renderizar_geradores(estado_eco, estado_upg):
    _, fatores = upgrades.calcular_fatores_por_gerador(estado_upg)
    linhas     = []
    for cat in CATEGORIAS_ORDEM:
        titulo = {'mineradora':'MINERADORAS','fabrica':'FÁBRICAS',
                  'usina':'USINAS','laboratorio':'LABORATÓRIOS'}.get(cat, cat.upper())
        linhas.append(f"\n  ┌─ {titulo} {'─'*(42-len(titulo))}")
        for id_ger, dados in GERADORES_CATALOGO.items():
            if dados['categoria'] != cat:
                continue
            cod_blq, _ = economia.calcular_custo_gerador(estado_eco, id_ger)
            if cod_blq == -4:
                linhas.append(f"  │  {dados['nome']:<28} 🔒 Bloqueado")
                continue
            _, qtd   = economia.obter_quantidade_gerador(estado_eco, id_ger)
            _, custo = economia.calcular_custo_gerador(estado_eco, id_ger)
            prod_unit = dados['prod_base'] * fatores.get(id_ger, 1.0)
            _, cs    = formatar_numero(custo)
            _, ps    = formatar_numero(prod_unit * (qtd or 0))
            linhas.append(
                f"  │  {dados['nome']:<28} qtd:{qtd:<4} "
                f"custo:{cs:<9} prod:{ps}/s"
            )
        linhas.append(f"  └{'─'*46}")
    return (0, '\n'.join(linhas))

def renderizar_upgrades(estado_upg, estado_eco):
    linhas = ["\n  ┌─ UPGRADES " + "─" * 40]
    icones = {'comprado': '$', 'disponivel': 'O', 'inacessivel': 'X'}
    vistos = set()
    for id_upg, dados in estado_upg['catalogo'].items():
        alvo = dados['alvo']
        if alvo not in vistos:
            vistos.add(alvo)
            nome_ger = GERADORES_CATALOGO.get(alvo, {}).get('nome', alvo)
            linhas.append(f"  │  [{nome_ger}]")
        status = _status_upgrade(id_upg, estado_upg, estado_eco)
        icone  = icones[status]
        _, cs  = formatar_numero(dados['custo'])
        fator  = f"×{int(dados['fator'])}"
        linhas.append(
            f"  │    {icone} {dados['nome']:<38} {fator:<5} {cs}"
        )
    linhas.append(f"  └{'─'*52}")
    return (0, '\n'.join(linhas))

def renderizar_progresso(estado_prog):
    nivel     = estado_prog.get('nivel', 1)
    cristais  = estado_prog.get('cristais_revolucao', 0)
    fragmen   = estado_prog.get('fragmentos_ascensao', 0)
    num_rev   = estado_prog.get('num_revolucoes', 0)
    num_asc   = estado_prog.get('num_ascensoes', 0)
    atingidos = estado_prog.get('marcos_atingidos', [])
    vitoria   = estado_prog.get('vitoria', False)

    sep = "─" * 46
    linhas = [
        f"\n  ┌─ PROGRESSO {sep[:38]}",
        f"  │  Nível: {nivel}/{NIVEL_MAXIMO}   "
        f"Revoluções: {num_rev}   Ascensões: {num_asc}",
        f"  │  Cristais: {cristais}   Fragmentos: {fragmen}",
        f"  │",
    ]
    if atingidos:
        linhas.append(f"  │  Marcos atingidos ({len(atingidos)}):")
        for mid in atingidos[-5:]:
            linhas.append(f"  │    $ {mid}")
        if len(atingidos) > 5:
            linhas.append(f"  │    ... e mais {len(atingidos)-5}")
    else:
        linhas.append("  │  Nenhum marco atingido ainda.")
    if vitoria:
        linhas.append("  │")
        linhas.append("  │  $$$ PONTO ÔMEGA ATINGIDO! VITÓRIA! $$$")
    linhas.append(f"  └{'─'*48}")
    return (0, '\n'.join(linhas))

def renderizar_resets(estado_eco, estado_prog):
    _, pontos_max  = economia.obter_pontos_run_max(estado_eco)
    num_rev        = estado_prog.get('num_revolucoes', 0)
    num_frag       = estado_prog.get('fragmentos_ascensao', 0)
    limiar_rev     = LIMIAR_REVOLUCAO_BASE * (FATOR_LIMIAR_REVOLUCAO ** num_rev)
    elegivel_rev   = pontos_max >= limiar_rev
    elegivel_asc   = num_rev >= REVOLUCOES_P_ASCENSAO

    import math
    cristais_est   = max(1, int(math.floor(math.sqrt(pontos_max / limiar_rev)))) if elegivel_rev else 0

    _, pm_str = formatar_numero(pontos_max)
    _, lr_str = formatar_numero(limiar_rev)

    linhas = ["\n  ┌─ RESETS " + "─" * 42]
    if elegivel_rev:
        linhas.append(f"  │  🔁 REVOLUÇÃO disponível! (pontos_max: {pm_str})")
        linhas.append(f"  │     Cristais a ganhar: ~{cristais_est}  │  cmd: revolucao")
    else:
        falta = limiar_rev - pontos_max
        _, f_str = formatar_numero(falta)
        linhas.append(f"  │  🔁 Revolução: faltam {f_str} pontos (limiar: {lr_str})")

    linhas.append("  │")
    if elegivel_asc:
        linhas.append(f"  │  ⬆ ASCENSÃO disponível! ({num_rev} revoluções)  │  cmd: ascensao")
        linhas.append(f"  │     Fragmentos atuais: {num_frag} → ganhar +1 (exp ^{1+num_frag*0.15+0.15:.2f})")
    else:
        falta_rev = REVOLUCOES_P_ASCENSAO - num_rev
        linhas.append(f"  │  ⬆ Ascensão: faltam {falta_rev} revoluções (atual: {num_rev}/{REVOLUCOES_P_ASCENSAO})")

    linhas.append(f"  └{'─'*52}")
    return (0, '\n'.join(linhas))

def montar_menu_comando():
    cmds = [
        "\n  ┌─ COMANDOS " + "─" * 40,
        "  │  comprar gerador <id>    — compra 1 unidade do gerador",
        "  │  comprar upgrade <id>    — compra o upgrade",
        "  │  listar geradores        — exibe todos os geradores",
        "  │  listar upgrades         — exibe todos os upgrades",
        "  │  revolucao               — executa Revolução (se elegível)",
        "  │  ascensao                — executa Ascensão (se elegível)",
        "  │  status                  — exibe painel completo",
        "  │  novo jogo               — apaga o save e reinicia",
        "  │  salvar e sair           — salva e encerra",
        f"  └{'─'*52}",
    ]
    return (0, '\n'.join(cmds))

def renderizar_painel(estado_eco, estado_upg, estado_prog):
    _, s_pontos  = renderizar_pontos(estado_eco)
    _, s_gers    = renderizar_geradores(estado_eco, estado_upg)
    _, s_prog    = renderizar_progresso(estado_prog)
    _, s_resets  = renderizar_resets(estado_eco, estado_prog)
    _, s_menu    = montar_menu_comando()
    painel = '\n'.join([s_pontos, s_gers, s_prog, s_resets, s_menu])
    return (0, painel)
