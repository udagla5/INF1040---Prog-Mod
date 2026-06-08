# =============================================================================
# interface_pygame/renderizador.py — Toda a renderização pygame do idle game
# INF1040 · 2026.1 · Grupo 3WB
#
# REGRA: zero lógica de jogo aqui. Apenas leitura dos TADs via interface
#        pública e desenho. Não acessa estruturas internas dos estados.
# =============================================================================

import math
import pygame

import economia
import upgrades  as upg_mod
import progresso as prog_mod
import display
from constantes import (
    GERADORES_CATALOGO, UPGRADES_CATALOGO,
    CATEGORIAS_ORDEM, NIVEL_MAXIMO,
    LIMIAR_REVOLUCAO_BASE, FATOR_LIMIAR_REVOLUCAO, REVOLUCOES_P_ASCENSAO,
)
from interface_pygame.ui_estado import registrar_botao, limpar_botoes

__all__ = [
    'inicializar_janela',
    'fechar_janela',
    'renderizar_frame',
]

# ---------------------------------------------------------------------------
# Layout (px)
# ---------------------------------------------------------------------------
W, H        = 1280, 760
HUD_H       = 90
BOTTOM_H    = 36
PANEL_H     = H - HUD_H - BOTTOM_H       # 634

GER_X, GER_W  = 0,    430
UPG_X, UPG_W  = 430,  410
INFO_X, INFO_W = 840, 440

ROW_GER  = 58
ROW_UPG  = 52
ROW_MSG  = 24
PAD      = 8

# ---------------------------------------------------------------------------
# Paleta
# ---------------------------------------------------------------------------
BG         = ( 15,  15,  28)
PANEL_BG   = ( 22,  22,  42)
HDR_BG     = ( 32,  32,  62)
BORDER     = ( 50,  50,  90)

WHITE      = (220, 220, 230)
GREY       = (120, 120, 140)
DARK_GREY  = ( 55,  55,  75)

GOLD       = (255, 200,  55)
GREEN      = ( 60, 200,  90)
GREEN_DIM  = ( 30,  90,  40)
RED        = (220,  70,  70)
BLUE       = ( 80, 140, 255)
PURPLE     = (160,  80, 230)
ORANGE     = (230, 140,  40)
TEAL       = ( 60, 200, 180)

CAT_COLORS = {
    'mineradora':  ( 80, 140, 255),
    'fabrica':     ( 60, 200,  90),
    'usina':       (230, 140,  40),
    'laboratorio': (160,  80, 230),
}

# ---------------------------------------------------------------------------
# Fonts (inicializadas em inicializar_janela)
# ---------------------------------------------------------------------------
_f = {}


def inicializar_janela(titulo='Idle Game — INF1040 · Grupo 3WB'):
    """
    Inicializa pygame e cria a janela.
    Retornos:
        (0, Surface, Clock)
    """
    pygame.init()
    janela = pygame.display.set_mode((W, H))
    pygame.display.set_caption(titulo)
    clock = pygame.time.Clock()

    _f['pts']    = pygame.font.SysFont('consolas', 28, bold=True)
    _f['taxa']   = pygame.font.SysFont('consolas', 17)
    _f['hdr']    = pygame.font.SysFont('consolas', 14, bold=True)
    _f['nome']   = pygame.font.SysFont('consolas', 13, bold=True)
    _f['small']  = pygame.font.SysFont('consolas', 12)
    _f['btn']    = pygame.font.SysFont('consolas', 12, bold=True)
    _f['msg']    = pygame.font.SysFont('consolas', 13)
    _f['titulo'] = pygame.font.SysFont('consolas', 16, bold=True)

    return (0, janela, clock)


def fechar_janela():
    """
    Encerra pygame.
    Retornos:
        (0, None)
    """
    pygame.quit()
    return (0, None)


# ---------------------------------------------------------------------------
# Entry point de renderização
# ---------------------------------------------------------------------------
def renderizar_frame(janela, eco, upg, prog, mensagens):
    """
    Desenha um frame completo do jogo.
    Parâmetros:
        janela    (Surface)
        eco       (dict) — estado de economia
        upg       (dict) — estado de upgrades
        prog      (dict) — estado de progresso
        mensagens (list) — strings de feedback recentes
    Retornos:
        (0, None)
    """
    limpar_botoes()
    janela.fill(BG)

    from interface_pygame.ui_estado import obter_scroll
    _, sc_ger = obter_scroll('geradores')
    _, sc_upg = obter_scroll('upgrades')

    _hud(janela, eco, prog)
    _painel_geradores(janela, eco, upg, sc_ger)
    _painel_upgrades(janela, eco, upg, sc_upg)
    _painel_info(janela, eco, upg, prog, mensagens)
    _bottom_bar(janela)

    pygame.display.flip()
    return (0, None)


# ---------------------------------------------------------------------------
# HUD superior
# ---------------------------------------------------------------------------
def _hud(janela, eco, prog):
    pygame.draw.rect(janela, HDR_BG, (0, 0, W, HUD_H))
    pygame.draw.line(janela, BORDER, (0, HUD_H), (W, HUD_H), 2)

    _, pontos = economia.obter_pontos(eco)
    _, taxa   = economia.calcular_taxa_total(eco)
    _, mult   = economia.obter_multiplicador_revolucao(eco)
    _, exp    = economia.obter_expoente_ascensao(eco)
    nivel     = prog.get('nivel', 1)

    _, ps = display.formatar_numero(pontos)
    _, ts = display.formatar_numero(taxa)

    # Pontos grandes
    surf = _f['pts'].render(f'{ps}  pts', True, GOLD)
    janela.blit(surf, (20, 16))

    # Taxa
    surf = _f['taxa'].render(f'+{ts}/s', True, GREEN)
    janela.blit(surf, (20, 56))

    # Multiplicador e expoente
    surf = _f['taxa'].render(f'×{mult:.2f}  ^{exp:.2f}', True, TEAL)
    janela.blit(surf, (260, 38))

    # Nível
    surf = _f['titulo'].render(f'Nível {nivel} / {NIVEL_MAXIMO}', True, BLUE)
    janela.blit(surf, (470, 16))

    # Barra de progresso de nível
    from constantes import LIMIARES_NIVEL
    _, pontos_max = economia.obter_pontos_run_max(eco)
    lim_atual  = LIMIARES_NIVEL[min(nivel - 1, len(LIMIARES_NIVEL) - 1)]
    lim_prox   = LIMIARES_NIVEL[min(nivel, len(LIMIARES_NIVEL) - 1)]
    if lim_prox > lim_atual:
        pct = min(1.0, (pontos_max - lim_atual) / (lim_prox - lim_atual))
    else:
        pct = 1.0
    bw = 300
    pygame.draw.rect(janela, DARK_GREY, (470, 44, bw, 14), border_radius=7)
    if pct > 0:
        pygame.draw.rect(janela, BLUE, (470, 44, int(bw * pct), 14), border_radius=7)

    # Cristais e fragmentos
    cristais  = prog.get('cristais_revolucao', 0)
    fragmen   = prog.get('fragmentos_ascensao', 0)
    num_rev   = prog.get('num_revolucoes', 0)
    surf = _f['taxa'].render(f'Cristais: {cristais}   Fragmentos: {fragmen}   Revoluções: {num_rev}',
                              True, GREY)
    janela.blit(surf, (470, 64))

    # Dividers verticais
    for x in (GER_W, UPG_X + UPG_W):
        pygame.draw.line(janela, BORDER, (x, 0), (x, HUD_H), 1)


# ---------------------------------------------------------------------------
# Painel esquerdo — GERADORES
# ---------------------------------------------------------------------------
def _painel_geradores(janela, eco, upg, scroll_y):
    x0 = GER_X
    y0 = HUD_H
    w  = GER_W
    h  = PANEL_H

    pygame.draw.rect(janela, PANEL_BG, (x0, y0, w, h))
    pygame.draw.line(janela, BORDER, (x0 + w, y0), (x0 + w, y0 + h), 1)

    # Título
    _titulo_painel(janela, x0, y0, w, 'GERADORES  ( scroll ↕ )', WHITE)
    TITULO_H = 32

    # Clipping na área scrollável
    clip_rect = pygame.Rect(x0, y0 + TITULO_H, w, h - TITULO_H)
    janela.set_clip(clip_rect)

    _, fatores = upg_mod.calcular_fatores_por_gerador(upg)

    y_cur = y0 + TITULO_H - scroll_y   # posição corrente no espaço da tela

    for cat in CATEGORIAS_ORDEM:
        cor_cat = CAT_COLORS[cat]
        label = {'mineradora':'MINERADORAS','fabrica':'FÁBRICAS',
                 'usina':'USINAS','laboratorio':'LABORATÓRIOS'}[cat]

        # Cabeçalho de categoria
        if _visivel(y_cur, y0 + TITULO_H, y0 + h):
            pygame.draw.rect(janela, _escurecer(cor_cat, 0.25), (x0, y_cur, w, 26))
            s = _f['hdr'].render(label, True, cor_cat)
            janela.blit(s, (x0 + PAD, y_cur + 5))
        y_cur += 26

        for id_ger, dados in GERADORES_CATALOGO.items():
            if dados['categoria'] != cat:
                continue

            if _visivel(y_cur, y0 + TITULO_H, y0 + h):
                _linha_gerador(janela, x0, y_cur, w, id_ger, dados,
                               eco, fatores, cor_cat, scroll_y)
            y_cur += ROW_GER

    janela.set_clip(None)



def _linha_gerador(janela, x0, y, w, id_ger, dados, eco, fatores, cor, scroll_y):
    cod_blq, _ = economia.calcular_custo_gerador(eco, id_ger)
    bloqueado  = cod_blq == -4

    bg = (28, 28, 52) if not bloqueado else (22, 22, 35)
    pygame.draw.rect(janela, bg, (x0, y, w, ROW_GER - 1))

    if bloqueado:
        surf = _f['nome'].render(f'🔒 {dados["nome"]}', True, DARK_GREY)
        janela.blit(surf, (x0 + PAD, y + 18))
        return

    _, qtd   = economia.obter_quantidade_gerador(eco, id_ger)
    _, custo = economia.calcular_custo_gerador(eco, id_ger)
    _, pode  = economia.pode_gastar(eco, custo)
    fator    = fatores.get(id_ger, 1.0)
    prod_tot = dados['prod_base'] * fator * (qtd or 0)

    _, cs = display.formatar_numero(custo)
    _, ps = display.formatar_numero(prod_tot)

    # Nome + qtd
    nome_cor = cor if qtd > 0 else GREY
    surf = _f['nome'].render(dados['nome'], True, nome_cor)
    janela.blit(surf, (x0 + PAD, y + 6))
    surf = _f['hdr'].render(f'× {qtd}', True, WHITE)
    janela.blit(surf, (x0 + PAD, y + 26))

    # Prod
    surf = _f['small'].render(f'{ps}/s', True, TEAL)
    janela.blit(surf, (x0 + PAD + 80, y + 28))

    # Botão [+1]
    btn_w, btn_h = 82, 32
    btn_x = x0 + w - btn_w - PAD
    btn_y = y + (ROW_GER - btn_h) // 2
    btn_cor = GREEN if pode else GREEN_DIM
    btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
    pygame.draw.rect(janela, btn_cor, btn_rect, border_radius=5)

    _, cs_s = display.formatar_numero(custo)
    surf = _f['btn'].render(f'+1', True, WHITE)
    janela.blit(surf, (btn_x + 6, btn_y + 5))
    surf = _f['small'].render(cs_s, True, WHITE if pode else GREY)
    janela.blit(surf, (btn_x + 26, btn_y + 6))

    registrar_botao(btn_rect, f'comprar gerador {id_ger}')

    # Linha separadora
    pygame.draw.line(janela, BORDER, (x0, y + ROW_GER - 1), (x0 + w, y + ROW_GER - 1))


# ---------------------------------------------------------------------------
# Painel central — UPGRADES
# ---------------------------------------------------------------------------
def _painel_upgrades(janela, eco, upg, scroll_y):
    x0 = UPG_X
    y0 = HUD_H
    w  = UPG_W
    h  = PANEL_H

    pygame.draw.rect(janela, PANEL_BG, (x0, y0, w, h))
    pygame.draw.line(janela, BORDER, (x0 + w, y0), (x0 + w, y0 + h), 1)
    _titulo_painel(janela, x0, y0, w, 'UPGRADES  ( scroll ↕ )', WHITE)
    TITULO_H = 32

    clip_rect = pygame.Rect(x0, y0 + TITULO_H, w, h - TITULO_H)
    janela.set_clip(clip_rect)

    # Monta lista: agrupa upgrades por gerador, mostrando apenas os dos
    # geradores que o jogador possui (qtd > 0) + os acessíveis gratuitamente.
    itens = _itens_upgrade(eco, upg)

    y_cur = y0 + TITULO_H - scroll_y

    cat_atual = None
    for item in itens:
        cat = GERADORES_CATALOGO.get(item['alvo'], {}).get('categoria', '')
        if cat != cat_atual:
            cat_atual = cat
            cor_cat = CAT_COLORS.get(cat, GREY)
            nome_ger = GERADORES_CATALOGO.get(item['alvo'], {}).get('nome', item['alvo'])
            if _visivel(y_cur, y0 + TITULO_H, y0 + h):
                pygame.draw.rect(janela, _escurecer(cor_cat, 0.20), (x0, y_cur, w, 22))
                s = _f['small'].render(nome_ger, True, cor_cat)
                janela.blit(s, (x0 + PAD, y_cur + 4))
            y_cur += 22

        if _visivel(y_cur, y0 + TITULO_H, y0 + h):
            _linha_upgrade(janela, x0, y_cur, w, item, eco, upg)
        y_cur += ROW_UPG

    janela.set_clip(None)


def _itens_upgrade(eco, upg):
    """Retorna upgrades para exibir, priorizando os comprables e do jogador."""
    _, comprados_dados = upg_mod.listar_comprados(upg)
    ids_comprados = {u['id'] for u in comprados_dados}

    resultado = []
    for id_ger in GERADORES_CATALOGO:
        cod_blq, _ = economia.calcular_custo_gerador(eco, id_ger)
        if cod_blq == -4:
            continue
        _, qtd = economia.obter_quantidade_gerador(eco, id_ger)
        if qtd == 0:
            continue
        # Pega os 3 upgrades desse gerador
        for suf in ('x2', 'x5', 'x10'):
            uid = f'upgrade_{id_ger}_{suf}'
            if uid in UPGRADES_CATALOGO:
                dado = UPGRADES_CATALOGO[uid]
                comprado = uid in ids_comprados
                _, pode = upg_mod.pode_comprar(upg, eco, uid)
                resultado.append({**dado, 'comprado': comprado, 'pode': pode})
    return resultado


def _linha_upgrade(janela, x0, y, w, item, eco, upg):
    comprado = item.get('comprado', False)
    pode     = item.get('pode', False)

    if comprado:
        bg = (22, 22, 38)
    elif pode:
        bg = (22, 50, 32)
    else:
        bg = (26, 26, 48)
    pygame.draw.rect(janela, bg, (x0, y, w, ROW_UPG - 1))

    nome_cor = GREY if comprado else (WHITE if pode else GREY)
    surf = _f['nome'].render(item['nome'], True, nome_cor)
    janela.blit(surf, (x0 + PAD, y + 6))

    fator = int(item['fator'])
    surf  = _f['small'].render(f'× {fator} produção', True, TEAL if not comprado else DARK_GREY)
    janela.blit(surf, (x0 + PAD, y + 26))

    if comprado:
        surf = _f['btn'].render('$ comprado', True, GREEN_DIM)
        janela.blit(surf, (x0 + w - 110, y + 15))
    else:
        _, cs = display.formatar_numero(item['custo'])
        btn_w, btn_h = 100, 28
        btn_x = x0 + w - btn_w - PAD
        btn_y = y + (ROW_UPG - btn_h) // 2
        btn_cor = GREEN if pode else GREEN_DIM
        btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        pygame.draw.rect(janela, btn_cor, btn_rect, border_radius=5)
        surf = _f['btn'].render(cs, True, WHITE)
        janela.blit(surf, (btn_x + 6, btn_y + 7))
        if pode:
            registrar_botao(btn_rect, f'comprar upgrade {item["id"]}')

    pygame.draw.line(janela, BORDER, (x0, y + ROW_UPG - 1), (x0 + w, y + ROW_UPG - 1))


# ---------------------------------------------------------------------------
# Painel direito — INFO + MENSAGENS
# ---------------------------------------------------------------------------
def _painel_info(janela, eco, upg, prog, mensagens):
    x0 = INFO_X
    y0 = HUD_H
    w  = INFO_W
    h  = PANEL_H

    pygame.draw.rect(janela, PANEL_BG, (x0, y0, w, h))

    y = y0 + PAD

    # ── Progresso ──────────────────────────────────────────────────────
    _titulo_painel(janela, x0, y0, w, 'PROGRESSO', WHITE)
    y += 36

    nivel    = prog.get('nivel', 1)
    cristais = prog.get('cristais_revolucao', 0)
    fragmen  = prog.get('fragmentos_ascensao', 0)
    num_rev  = prog.get('num_revolucoes', 0)
    num_asc  = prog.get('num_ascensoes', 0)
    vitoria  = prog.get('vitoria', False)
    marcos   = prog.get('marcos_atingidos', [])

    _label_valor(janela, x0 + PAD, y, w - PAD*2, 'Nível',       f'{nivel} / {NIVEL_MAXIMO}', BLUE)
    y += 24
    _label_valor(janela, x0 + PAD, y, w - PAD*2, 'Revoluções',  str(num_rev),  ORANGE)
    y += 22
    _label_valor(janela, x0 + PAD, y, w - PAD*2, 'Ascensões',   str(num_asc),  PURPLE)
    y += 22
    _label_valor(janela, x0 + PAD, y, w - PAD*2, 'Cristais',    str(cristais), GOLD)
    y += 22
    _label_valor(janela, x0 + PAD, y, w - PAD*2, 'Fragmentos',  str(fragmen),  TEAL)
    y += 28

    # Marcos
    surf = _f['hdr'].render(f'Marcos atingidos: {len(marcos)}', True, GREY)
    janela.blit(surf, (x0 + PAD, y))
    y += 20
    for mid in marcos[-4:]:
        surf = _f['small'].render(f'  $ {mid}', True, GOLD)
        janela.blit(surf, (x0 + PAD, y))
        y += 18
    if len(marcos) > 4:
        surf = _f['small'].render(f'  … +{len(marcos)-4} mais', True, GREY)
        janela.blit(surf, (x0 + PAD, y))
        y += 18

    if vitoria:
        pygame.draw.rect(janela, (60, 40, 10), (x0, y, w, 28))
        surf = _f['titulo'].render('$$$ PONTO ÔMEGA — VITÓRIA! $$$', True, GOLD)
        janela.blit(surf, (x0 + PAD, y + 5))
        y += 34

    # ── Separador ──────────────────────────────────────────────────────
    y += 6
    pygame.draw.line(janela, BORDER, (x0 + PAD, y), (x0 + w - PAD, y))
    y += 10

    # ── Revolução ──────────────────────────────────────────────────────
    _, pode_rev = prog_mod.pode_revolucao(eco, prog)
    _, pontos_max = economia.obter_pontos_run_max(eco)
    limiar_rev = LIMIAR_REVOLUCAO_BASE * (FATOR_LIMIAR_REVOLUCAO ** num_rev)
    _, lim_s   = display.formatar_numero(limiar_rev)
    _, pm_s    = display.formatar_numero(pontos_max)

    surf = _f['titulo'].render('REVOLUÇÃO', True, ORANGE)
    janela.blit(surf, (x0 + PAD, y))
    y += 22

    if pode_rev:
        import math as _math
        crist_est = max(1, int(_math.floor(_math.sqrt(pontos_max / limiar_rev))))
        surf = _f['small'].render(f'Disponível! +{crist_est} cristal(is)', True, GOLD)
        janela.blit(surf, (x0 + PAD, y))
        y += 20
        btn = _botao_acao(janela, x0 + PAD, y, w - PAD*2, 36,
                          '🔁  EXECUTAR REVOLUÇÃO', ORANGE, 'revolucao')
        y += 44
    else:
        falta = max(0, limiar_rev - pontos_max)
        _, falta_s = display.formatar_numero(falta)
        surf = _f['small'].render(f'Faltam {falta_s} pts (limiar: {lim_s})', True, GREY)
        janela.blit(surf, (x0 + PAD, y))
        y += 24

    # ── Ascensão ───────────────────────────────────────────────────────
    y += 4
    pygame.draw.line(janela, BORDER, (x0 + PAD, y), (x0 + w - PAD, y))
    y += 8

    _, pode_asc = prog_mod.pode_ascensao(prog)
    surf = _f['titulo'].render('ASCENSÃO', True, PURPLE)
    janela.blit(surf, (x0 + PAD, y))
    y += 22

    if pode_asc:
        surf = _f['small'].render(f'Disponível! +1 fragmento (exp ^{1+(fragmen+1)*0.15:.2f})', True, TEAL)
        janela.blit(surf, (x0 + PAD, y))
        y += 20
        _botao_acao(janela, x0 + PAD, y, w - PAD*2, 36,
                    '⬆  EXECUTAR ASCENSÃO', PURPLE, 'ascensao')
        y += 44
    else:
        faltam = max(0, REVOLUCOES_P_ASCENSAO - num_rev)
        surf = _f['small'].render(f'Faltam {faltam} rev. ({num_rev}/{REVOLUCOES_P_ASCENSAO})', True, GREY)
        janela.blit(surf, (x0 + PAD, y))
        y += 22

    # ── Mensagens ──────────────────────────────────────────────────────
    y += 4
    pygame.draw.line(janela, BORDER, (x0 + PAD, y), (x0 + w - PAD, y))
    y += 8

    surf = _f['hdr'].render('LOG', True, GREY)
    janela.blit(surf, (x0 + PAD, y))
    y += 20

    for msg in mensagens[:10]:
        if y + ROW_MSG > y0 + h - 10:
            break
        cor = GOLD if msg.startswith('$') else (RED if '[ERRO]' in msg else WHITE)
        # Truncar mensagem se muito longa
        txt = msg[:52] + '…' if len(msg) > 52 else msg
        surf = _f['msg'].render(txt, True, cor)
        janela.blit(surf, (x0 + PAD, y))
        y += ROW_MSG


# ---------------------------------------------------------------------------
# Bottom bar
# ---------------------------------------------------------------------------
def _bottom_bar(janela):
    y0 = H - BOTTOM_H
    pygame.draw.rect(janela, HDR_BG, (0, y0, W, BOTTOM_H))
    pygame.draw.line(janela, BORDER, (0, y0), (W, y0), 1)

    surf = _f['small'].render('Salvo automaticamente ao fechar', True, GREY)
    janela.blit(surf, (PAD, y0 + 10))

    # Botão salvar
    _botao_acao(janela, W - 360, y0 + 4, 100, 28, 'SALVAR', BLUE,  '__salvar__')
    # Botão novo jogo
    _botao_acao(janela, W - 240, y0 + 4, 110, 28, 'NOVO JOGO', RED,   'novo jogo')
    # Botão sair
    _botao_acao(janela, W - 120, y0 + 4,  88, 28, 'SAIR',      GREY,  'sair')


# ---------------------------------------------------------------------------
# Helpers de desenho
# ---------------------------------------------------------------------------
def _titulo_painel(janela, x0, y0, w, txt, cor):
    pygame.draw.rect(janela, HDR_BG, (x0, y0, w, 30))
    pygame.draw.line(janela, BORDER, (x0, y0 + 30), (x0 + w, y0 + 30), 1)
    surf = _f['titulo'].render(txt, True, cor)
    janela.blit(surf, (x0 + PAD, y0 + 7))


def _label_valor(janela, x, y, w, label, valor, cor_valor):
    surf_l = _f['small'].render(label + ':', True, GREY)
    surf_v = _f['hdr'].render(valor, True, cor_valor)
    janela.blit(surf_l, (x, y))
    janela.blit(surf_v, (x + w - surf_v.get_width(), y))


def _botao_acao(janela, x, y, w, h, texto, cor, cmd):
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(janela, _escurecer(cor, 0.45), rect, border_radius=5)
    pygame.draw.rect(janela, cor, rect, width=1, border_radius=5)
    surf = _f['btn'].render(texto, True, cor)
    cx   = x + (w - surf.get_width())  // 2
    cy   = y + (h - surf.get_height()) // 2
    janela.blit(surf, (cx, cy))
    registrar_botao(rect, cmd)
    return rect


def _escurecer(cor, fator):
    return tuple(max(0, int(c * fator)) for c in cor)


def _visivel(y, y_min, y_max):
    return y_min - ROW_GER <= y <= y_max
