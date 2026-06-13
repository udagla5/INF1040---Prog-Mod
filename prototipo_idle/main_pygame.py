# =============================================================================
# main_pygame.py — Front-end pygame do idle game (arquivo único)
# INF1040 - 2026.1 - Grupo 2
#
# Uso: python main_pygame.py
# =============================================================================

import math
import random
import time
import sys
import pygame

import economia
import upgrades  as upg_mod
import progresso as prog_mod
import persistencia
import display
from constantes import (
    GERADORES_CATALOGO, UPGRADES_CATALOGO,
    CATEGORIAS_ORDEM, NIVEL_MAXIMO,
    LIMIAR_REVOLUCAO_BASE, FATOR_LIMIAR_REVOLUCAO, REVOLUCOES_P_ASCENSAO,
    LIMIARES_NIVEL,
)
from main_console import processar_comando


# =============================================================================
# ui_estado — estado da interface (scroll, botões, partículas, flash)
# =============================================================================

_ui = {
    'scroll_geradores': 0,
    'scroll_upgrades':  0,
    'botoes':     [],
    'particulas': [],
    'flash':      None,
    'drag':       None,   # {'painel': str, 'offset_y': int} | None
    'sb_info':    {},     # painel -> {track_x, track_y, track_h, thumb_y, thumb_h, conteudo_h}
}

_SCROLL_PX = 28

_FLASH_CORES = {
    'revolucao': (230, 140,  40),
    'ascensao':  (160,  80, 230),
    'compra':    ( 60, 200,  90),
    'marco':     (255, 200,  55),
}


def inicializar_ui():
    """
    Reinicia todo o estado da interface para os valores iniciais.

    Assertiva de entrada:
        (nenhuma)

    Assertiva de saída:
        (0, None) — _ui zerado: scrolls=0, botoes=[], particulas=[],
                    flash=None, drag=None, sb_info={}
    """
    _ui['scroll_geradores'] = 0
    _ui['scroll_upgrades']  = 0
    _ui['botoes']           = []
    _ui['particulas']       = []
    _ui['flash']            = None
    _ui['drag']             = None
    _ui['sb_info']          = {}
    return (0, None)


def obter_scroll(painel):
    """
    Retorna a posição atual de scroll de um painel.

    Assertiva de entrada:
        painel (str) — 'geradores' ou 'upgrades'

    Assertiva de saída:
        (0, int >= 0) — posição atual em pixels
        (1, 0)        — painel desconhecido
    """
    chave = f'scroll_{painel}'
    if chave not in _ui:
        return (1, 0)
    return (0, _ui[chave])


def atualizar_scroll(painel, delta_ticks, altura_conteudo, altura_visivel):
    """
    Aplica delta de scroll ao painel, respeitando os limites 0..max_scroll.

    Assertiva de entrada:
        painel          (str) — 'geradores' ou 'upgrades'
        delta_ticks     (int) — unidades de scroll do evento MOUSEWHEEL
                                (positivo = scroll up, negativo = scroll down)
        altura_conteudo (int) — altura total do conteúdo em pixels
        altura_visivel  (int) — altura da área visível em pixels

    Assertiva de saída:
        (0, int >= 0) — nova posição de scroll, clampada em [0, max_scroll]
        (1, 0)        — painel desconhecido
    """
    chave = f'scroll_{painel}'
    if chave not in _ui:
        return (1, 0)
    max_scroll = max(0, altura_conteudo - altura_visivel)
    novo = _ui[chave] - delta_ticks * _SCROLL_PX
    novo = max(0, min(novo, max_scroll))
    _ui[chave] = novo
    return (0, novo)


def limpar_botoes():
    """
    Remove todos os botões registrados no frame atual.

    Assertiva de entrada:
        (nenhuma)

    Assertiva de saída:
        (0, None) — _ui['botoes'] = []
    """
    _ui['botoes'] = []
    return (0, None)


def registrar_botao(rect, comando):
    """
    Associa um retângulo clicável a um comando de jogo.

    Assertiva de entrada:
        rect    (pygame.Rect) — área clicável na tela
        comando (str)         — comando a ser executado ao clicar

    Assertiva de saída:
        (0, None) — (rect, comando) adicionado a _ui['botoes']
    """
    _ui['botoes'].append((rect, comando))
    return (0, None)


def botao_em(pos):
    """
    Encontra o primeiro botão cujo retângulo contém a posição dada.

    Assertiva de entrada:
        pos (tuple[int, int]) — coordenadas (x, y) do clique do mouse

    Assertiva de saída:
        (0, str)  — comando do primeiro botão que colide com pos
        (0, None) — nenhum botão cobre a posição
    """
    for rect, cmd in _ui['botoes']:
        if rect.collidepoint(pos):
            return (0, cmd)
    return (0, None)


def adicionar_particula(x, y, texto, cor=(255, 200, 55)):
    """
    Cria uma partícula de texto flutuante na posição dada.

    Assertiva de entrada:
        x     (int ou float) — coordenada x inicial (pixels)
        y     (int ou float) — coordenada y inicial (pixels)
        texto (str)          — texto exibido pela partícula
        cor   (tuple[int,int,int]) — cor RGB (padrão dourado)

    Assertiva de saída:
        (0, None) — partícula adicionada a _ui['particulas'] com posição
                    aleatória ±10px em x, velocidade inicial e vida=1.4s
    """
    _ui['particulas'].append({
        'x':        float(x) + random.uniform(-10, 10),
        'y':        float(y),
        'vx':       random.uniform(-18, 18),
        'vy':       -75.0,
        'texto':    texto,
        'cor':      cor,
        'vida':     1.4,
        'vida_max': 1.4,
    })
    return (0, None)


def atualizar_particulas(delta):
    """
    Avança a simulação de todas as partículas ativas pelo tempo decorrido.

    Assertiva de entrada:
        delta (float) — tempo em segundos desde o último frame; >= 0

    Assertiva de saída:
        (0, None) — partículas mortas (vida <= 0) removidas de _ui['particulas'];
                    posição e velocidade das vivas atualizadas
    """
    vivas = []
    for p in _ui['particulas']:
        p['vida'] -= delta
        p['x'] += p['vx'] * delta
        p['y'] += p['vy'] * delta
        p['vy'] += 30 * delta
        if p['vida'] > 0:
            vivas.append(p)
    _ui['particulas'] = vivas
    return (0, None)


def obter_particulas():
    """
    Retorna cópia da lista de partículas ativas.

    Assertiva de entrada:
        (nenhuma)

    Assertiva de saída:
        (0, list[dict]) — cópia de _ui['particulas']; pode ser lista vazia
    """
    return (0, list(_ui['particulas']))


def registrar_flash(tipo):
    """
    Inicia um efeito de flash colorido na tela inteira.

    Assertiva de entrada:
        tipo (str) — chave em _FLASH_CORES: 'revolucao', 'ascensao',
                     'compra' ou 'marco'; valor desconhecido usa branco

    Assertiva de saída:
        (0, None) — _ui['flash'] definido com cor, alpha inicial e taxa de decay
    """
    cor = _FLASH_CORES.get(tipo, (255, 255, 255))
    alpha_inicial = 160 if tipo in ('revolucao', 'ascensao') else 80
    _ui['flash'] = {'cor': cor, 'alpha': float(alpha_inicial), 'decay': 280.0}
    return (0, None)


def atualizar_flash(delta):
    """
    Decrementa o alpha do flash ativo; remove-o quando chegar a zero.

    Assertiva de entrada:
        delta (float) — tempo em segundos desde o último frame; >= 0

    Assertiva de saída:
        (0, None) — _ui['flash'] atualizado; definido como None se esgotado
    """
    f = _ui['flash']
    if f is not None:
        f['alpha'] -= f['decay'] * delta
        if f['alpha'] <= 0:
            _ui['flash'] = None
    return (0, None)


def obter_flash():
    """
    Retorna o estado atual do flash de tela.

    Assertiva de entrada:
        (nenhuma)

    Assertiva de saída:
        (0, dict) — dict com 'cor', 'alpha' e 'decay' se flash ativo
        (0, None) — nenhum flash em andamento
    """
    return (0, _ui['flash'])


# =============================================================================
# renderizador — layout, paleta, fontes e funções de desenho
# =============================================================================

W, H        = 1280, 760
HUD_H       = 100
BOTTOM_H    = 32
PANEL_H     = H - HUD_H - BOTTOM_H

GER_X, GER_W   = 0,   430
UPG_X, UPG_W   = 430, 410
INFO_X, INFO_W = 840, 440

ROW_GER = 62
ROW_UPG = 50
ROW_MSG = 22
PAD     = 10

# Paleta — dark RPG/strategy
BG        = (  7,   6,  15)
PANEL_BG  = ( 11,  10,  22)
CARD_BG   = ( 17,  15,  32)
CARD_BG2  = ( 22,  20,  40)
HDR_BG    = ( 20,  16,  38)
BORDER    = ( 55,  45,  85)
BORDER_HL = (100,  80, 145)

WHITE     = (235, 228, 245)
GREY      = (105,  98, 128)
DARK_GREY = ( 42,  38,  60)
MID_GREY  = ( 68,  62,  92)

GOLD      = (255, 198,  42)
GOLD_DIM  = ( 90,  68,  12)
GREEN     = ( 48, 215,  88)
GREEN_DIM = ( 18,  72,  34)
RED       = (230,  55,  65)
BLUE      = ( 72, 148, 255)
PURPLE    = (172,  72, 248)
ORANGE    = (248, 138,  24)
TEAL      = ( 42, 218, 175)
CRIMSON   = (200,  30,  60)

CAT_COLORS = {
    'mineradora':  ( 72, 148, 255),
    'fabrica':     ( 48, 215,  88),
    'usina':       (248, 138,  24),
    'laboratorio': (172,  72, 248),
}
CAT_LABEL = {
    'mineradora':  'MINERADORAS',
    'fabrica':     'FÁBRICAS',
    'usina':       'USINAS',
    'laboratorio': 'LABORATÓRIOS',
}

_f = {}
_bg_cache = None   # Surface com a textura de fundo pré-renderizada


def inicializar_janela(titulo='Revolution Idle — INF1040 - 2026.1 - Grupo 2'):
    """
    Inicializa o pygame, cria a janela, carrega as fontes e pré-renderiza o fundo.

    Assertiva de entrada:
        titulo (str) — título exibido na barra da janela

    Assertiva de saída:
        (0, pygame.Surface, pygame.time.Clock) — janela e clock prontos para uso;
                                                  _f preenchido, _bg_cache renderizado
    """
    global _bg_cache
    pygame.init()
    janela = pygame.display.set_mode((W, H))
    pygame.display.set_caption(titulo)
    clock = pygame.time.Clock()

    tah = 'tahoma'
    treb = 'trebuchetms'
    _f['big']    = pygame.font.SysFont(tah,  36, bold=True)
    _f['pts']    = pygame.font.SysFont(tah,  30, bold=True)
    _f['titulo'] = pygame.font.SysFont(tah,  15, bold=True)
    _f['hdr']    = pygame.font.SysFont(tah,  13, bold=True)
    _f['nome']   = pygame.font.SysFont(tah,  13, bold=True)
    _f['small']  = pygame.font.SysFont(tah,  12)
    _f['tiny']   = pygame.font.SysFont(tah,  11)
    _f['btn']    = pygame.font.SysFont(tah,  12, bold=True)
    _f['msg']    = pygame.font.SysFont(tah,  12)
    _f['taxa']   = pygame.font.SysFont(tah,  13)
    _f['game']   = pygame.font.SysFont(treb, 22, bold=True)

    # Pré-renderiza grade de fundo
    _bg_cache = pygame.Surface((W, H))
    _bg_cache.fill(BG)
    for gx in range(0, W, 40):
        pygame.draw.line(_bg_cache, (14, 12, 26), (gx, 0), (gx, H))
    for gy in range(0, H, 40):
        pygame.draw.line(_bg_cache, (14, 12, 26), (0, gy), (W, gy))
    # pontos nos cruzamentos
    dot_surf = pygame.Surface((3, 3), pygame.SRCALPHA)
    dot_surf.fill((40, 35, 65, 120))
    for gx in range(0, W, 40):
        for gy in range(0, H, 40):
            _bg_cache.blit(dot_surf, (gx - 1, gy - 1))

    return (0, janela, clock)


def fechar_janela():
    """
    Encerra o subsistema pygame.

    Assertiva de entrada:
        (nenhuma) — pygame deve estar inicializado

    Assertiva de saída:
        (0, None) — pygame.quit() chamado
    """
    pygame.quit()
    return (0, None)


def renderizar_frame(janela, eco, upg, prog, mensagens, mouse_pos=(0, 0)):
    """
    Desenha um frame completo do jogo na janela e chama pygame.display.flip().

    Assertiva de entrada:
        janela    (pygame.Surface)   — superfície principal retornada por inicializar_janela
        eco       (dict)             — estado válido retornado por economia.inicializar_estado
        upg       (dict)             — estado válido retornado por upgrades.inicializar_upgrades
        prog      (dict)             — estado válido retornado por progresso.inicializar_progresso
        mensagens (list[str])        — mensagens de log a exibir (mais recente primeiro)
        mouse_pos (tuple[int, int])  — posição atual do mouse para efeitos de hover

    Assertiva de saída:
        (0, None) — frame renderizado; botões do frame recriados em _ui['botoes']
    """
    limpar_botoes()
    janela.blit(_bg_cache, (0, 0))

    _, sc_ger = obter_scroll('geradores')
    _, sc_upg = obter_scroll('upgrades')

    _hud(janela, eco, prog)
    _painel_geradores(janela, eco, upg, sc_ger, mouse_pos)
    _painel_upgrades(janela, eco, upg, sc_upg, mouse_pos)
    _painel_info(janela, eco, upg, prog, mensagens, mouse_pos)
    _bottom_bar(janela, mouse_pos)

    # Divisores verticais sobre tudo
    for x in (GER_W, UPG_X + UPG_W):
        pygame.draw.line(janela, BORDER_HL, (x, HUD_H), (x, H - BOTTOM_H), 1)

    _desenhar_flash(janela)
    _desenhar_particulas(janela)
    pygame.display.flip()
    return (0, None)


# ---------------------------------------------------------------------------
# HUD
# ---------------------------------------------------------------------------
def _hud(janela, eco, prog):
    # Fundo com gradiente simulado (duas faixas)
    pygame.draw.rect(janela, (16, 13, 32), (0, 0, W, HUD_H // 2))
    pygame.draw.rect(janela, (13, 10, 26), (0, HUD_H // 2, W, HUD_H // 2))
    pygame.draw.line(janela, BORDER_HL, (0, HUD_H), (W, HUD_H), 2)

    _, pontos = economia.obter_pontos(eco)
    _, taxa   = economia.calcular_taxa_total(eco)
    _, mult   = economia.obter_multiplicador_revolucao(eco)
    _, exp    = economia.obter_expoente_ascensao(eco)
    nivel     = prog.get('nivel', 1)
    cristais  = prog.get('cristais_revolucao', 0)
    fragmen   = prog.get('fragmentos_ascensao', 0)
    num_rev   = prog.get('num_revolucoes', 0)

    _, ps = display.formatar_numero(pontos)
    _, ts = display.formatar_numero(taxa)

    # Título do jogo
    surf = _f['game'].render('REVOLUTION IDLE', True, _pulsar(CRIMSON, ORANGE, 1.2))
    janela.blit(surf, (14, 10))
    surf = _f['tiny'].render('INF1040 - 2026.1 - Grupo 2', True, MID_GREY)
    janela.blit(surf, (16, 46))

    # Separador vertical após título
    pygame.draw.line(janela, BORDER, (230, 8), (230, HUD_H - 8), 1)

    # Pontos — centro-esquerda
    t = time.time()
    pulse = 0.5 + 0.5 * math.sin(t * 2.2)
    pts_cor = (255, int(185 + 13 * pulse), int(20 + 22 * pulse))
    surf = _f['pts'].render(ps, True, pts_cor)
    janela.blit(surf, (244, 8))

    surf = _f['taxa'].render(f'+ {ts} / s', True, GREEN)
    janela.blit(surf, (246, 52))

    # ×mult  ^exp
    surf = _f['small'].render(f'× {mult:.2f}   ^ {exp:.2f}', True, TEAL)
    janela.blit(surf, (246, 74))

    pygame.draw.line(janela, BORDER, (490, 8), (490, HUD_H - 8), 1)

    # Nível + barra
    surf = _f['hdr'].render(f'NÍVEL  {nivel} / {NIVEL_MAXIMO}', True, BLUE)
    janela.blit(surf, (504, 10))

    _, pontos_max = economia.obter_pontos_run_max(eco)
    lim_atual = LIMIARES_NIVEL[min(nivel - 1, len(LIMIARES_NIVEL) - 1)]
    lim_prox  = LIMIARES_NIVEL[min(nivel,     len(LIMIARES_NIVEL) - 1)]
    pct = min(1.0, (pontos_max - lim_atual) / (lim_prox - lim_atual)) if lim_prox > lim_atual else 1.0
    _barra(janela, 504, 34, 310, 12, pct, BLUE, (18, 24, 48))

    # Cristais / fragmentos / revoluções como "chips" — posição encadeada
    cx = 504
    cx = _chip(janela, cx, 58, f'{cristais}', GOLD,   'Cristais')   + 6
    cx = _chip(janela, cx, 58, f'{fragmen}',  PURPLE, 'Fragmentos') + 6
    _chip(janela, cx, 58, f'{num_rev}',  ORANGE, 'Revolucoes')


def _chip(janela, x, y, texto, cor, tooltip):
    surf_t = _f['tiny'].render(tooltip, True, _escurecer(cor, 0.7))
    surf_v = _f['hdr'].render(texto, True, cor)
    w = max(surf_t.get_width(), surf_v.get_width()) + 16
    pygame.draw.rect(janela, _escurecer(cor, 0.12), (x, y, w, 34), border_radius=4)
    pygame.draw.rect(janela, _escurecer(cor, 0.40), (x, y, w, 34), width=1, border_radius=4)
    janela.blit(surf_t, (x + 8, y + 3))
    janela.blit(surf_v, (x + 8, y + 16))
    return x + w


def _barra(janela, x, y, w, h, pct, cor_fill, cor_bg, border_radius=4):
    pygame.draw.rect(janela, cor_bg, (x, y, w, h), border_radius=border_radius)
    if pct > 0:
        fill_w = max(border_radius * 2, int(w * pct))
        pygame.draw.rect(janela, cor_fill, (x, y, fill_w, h), border_radius=border_radius)
    pygame.draw.rect(janela, _escurecer(cor_fill, 0.5), (x, y, w, h), width=1, border_radius=border_radius)


# ---------------------------------------------------------------------------
# Painel esquerdo — GERADORES
# ---------------------------------------------------------------------------
def _painel_geradores(janela, eco, upg, scroll_y, mouse_pos=(0, 0)):
    x0, y0, w, h = GER_X, HUD_H, GER_W, PANEL_H
    pygame.draw.rect(janela, PANEL_BG, (x0, y0, w, h))
    TITULO_H = 34
    _cabecalho_painel(janela, x0, y0, w, TITULO_H, 'GERADORES', WHITE)

    clip_rect = pygame.Rect(x0, y0 + TITULO_H, w, h - TITULO_H)
    janela.set_clip(clip_rect)

    _, fatores = upg_mod.calcular_fatores_por_gerador(upg)
    y_cur = y0 + TITULO_H - scroll_y

    for cat in CATEGORIAS_ORDEM:
        cor_cat = CAT_COLORS[cat]
        if _visivel(y_cur, y0 + TITULO_H, y0 + h):
            _separador_categoria(janela, x0, y_cur, w, CAT_LABEL[cat], cor_cat)
        y_cur += 28

        for id_ger, dados in GERADORES_CATALOGO.items():
            if dados['categoria'] != cat:
                continue
            if _visivel(y_cur, y0 + TITULO_H, y0 + h):
                _linha_gerador(janela, x0, y_cur, w, id_ger, dados,
                               eco, fatores, cor_cat, mouse_pos)
            y_cur += ROW_GER

    janela.set_clip(None)
    conteudo_h = 40 * ROW_GER + 4 * 28 + TITULO_H + 20
    _scrollbar(janela, 'geradores', x0, y0, w, h, TITULO_H, scroll_y, conteudo_h)


def _separador_categoria(janela, x0, y, w, label, cor):
    pygame.draw.rect(janela, _escurecer(cor, 0.18), (x0, y, w, 28))
    # barra colorida na esquerda
    pygame.draw.rect(janela, cor, (x0, y, 4, 28))
    s = _f['hdr'].render(label, True, _clarear(cor, 1.1))
    janela.blit(s, (x0 + 12, y + 7))


def _linha_gerador(janela, x0, y, w, id_ger, dados, eco, fatores, cor, mouse_pos=(0, 0)):
    cod_blq, _ = economia.calcular_custo_gerador(eco, id_ger)
    bloqueado  = cod_blq == -4

    # Card base
    bg = CARD_BG if not bloqueado else (10, 9, 20)
    pygame.draw.rect(janela, bg, (x0, y, w, ROW_GER - 1))
    # Linha colorida à esquerda (4 px)
    stripe_cor = cor if not bloqueado else DARK_GREY
    pygame.draw.rect(janela, stripe_cor, (x0, y, 4, ROW_GER - 1))

    if bloqueado:
        surf = _f['nome'].render(f'{dados["nome"]}', True, DARK_GREY)
        janela.blit(surf, (x0 + 14, y + (ROW_GER - surf.get_height()) // 2))
        pygame.draw.line(janela, (20, 18, 36), (x0, y + ROW_GER - 1), (x0 + w, y + ROW_GER - 1))
        return

    _, qtd   = economia.obter_quantidade_gerador(eco, id_ger)
    _, custo = economia.calcular_custo_gerador(eco, id_ger)
    _, pode  = economia.pode_gastar(eco, custo)
    fator     = fatores.get(id_ger, 1.0)
    prod_unit = dados['prod_base'] * fator
    prod_tot  = prod_unit * (qtd or 0)

    _, cs  = display.formatar_numero(custo)
    _, ps  = display.formatar_numero(prod_tot)
    _, pus = display.formatar_numero(prod_unit)

    # Nome
    nome_cor = _clarear(cor, 1.05) if qtd > 0 else GREY
    surf = _f['nome'].render(dados['nome'], True, nome_cor)
    janela.blit(surf, (x0 + 14, y + 7))

    # Produção
    if qtd > 0:
        info = f'{ps}/s  (+{pus} cada)'
        surf = _f['tiny'].render(info, True, TEAL)
    else:
        surf = _f['tiny'].render(f'+{pus}/s por unidade', True, MID_GREY)
    janela.blit(surf, (x0 + 14, y + 28))

    # Badge de quantidade
    qtd_str = str(qtd)
    bw_qtd  = max(32, _f['hdr'].size(qtd_str)[0] + 14)
    bx_qtd  = x0 + w - 180
    by_qtd  = y + 7
    qtd_bg  = _escurecer(cor, 0.22) if qtd > 0 else DARK_GREY
    pygame.draw.rect(janela, qtd_bg, (bx_qtd, by_qtd, bw_qtd, 22), border_radius=3)
    surf = _f['hdr'].render(qtd_str, True, cor if qtd > 0 else MID_GREY)
    janela.blit(surf, (bx_qtd + (bw_qtd - surf.get_width()) // 2, by_qtd + 4))

    # Botão comprar
    btn_w, btn_h = 98, 36
    btn_x = x0 + w - btn_w - PAD
    btn_y = y + (ROW_GER - btn_h) // 2
    btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
    _botao_comprar(janela, btn_rect, cs, pode, mouse_pos)
    registrar_botao(btn_rect, f'comprar gerador {id_ger}')

    pygame.draw.line(janela, (22, 20, 38), (x0, y + ROW_GER - 1), (x0 + w, y + ROW_GER - 1))


def _botao_comprar(janela, rect, custo_str, pode, mouse_pos):
    hover = rect.collidepoint(mouse_pos)
    t     = time.time()
    if pode:
        pulse  = 0.5 + 0.5 * math.sin(t * 3.8)
        base   = (int(30 + 18 * pulse), int(160 + 55 * pulse), int(50 + 38 * pulse))
        border = _clarear(base, 1.5) if hover else _clarear(base, 1.2)
    else:
        base   = (18, 48, 28)
        border = (28, 60, 38)

    pygame.draw.rect(janela, base, rect, border_radius=4)
    pygame.draw.rect(janela, border, rect, width=1, border_radius=4)

    # Glow se hover e pode comprar
    if hover and pode:
        g = pygame.Surface((rect.w + 8, rect.h + 8), pygame.SRCALPHA)
        pygame.draw.rect(g, (48, 215, 88, 40), g.get_rect(), border_radius=6)
        janela.blit(g, (rect.x - 4, rect.y - 4))

    surf1 = _f['btn'].render('+1', True, WHITE if pode else MID_GREY)
    surf2 = _f['tiny'].render(custo_str, True, (200, 240, 210) if pode else DARK_GREY)
    janela.blit(surf1, (rect.x + 6, rect.y + 4))
    janela.blit(surf2, (rect.x + 6, rect.y + 20))


# ---------------------------------------------------------------------------
# Painel central — UPGRADES
# ---------------------------------------------------------------------------
def _painel_upgrades(janela, eco, upg, scroll_y, mouse_pos=(0, 0)):
    x0, y0, w, h = UPG_X, HUD_H, UPG_W, PANEL_H
    pygame.draw.rect(janela, PANEL_BG, (x0, y0, w, h))
    TITULO_H = 34
    _cabecalho_painel(janela, x0, y0, w, TITULO_H, 'MELHORIAS', WHITE)

    janela.set_clip(pygame.Rect(x0, y0 + TITULO_H, w, h - TITULO_H))

    itens   = _itens_upgrade(eco, upg)
    y_cur   = y0 + TITULO_H - scroll_y
    cat_ant = None
    num_geradores_visiveis = 0

    for item in itens:
        alvo    = item['alvo']
        cat     = GERADORES_CATALOGO.get(alvo, {}).get('categoria', '')
        cor_cat = CAT_COLORS.get(cat, GREY)

        if alvo != cat_ant:
            cat_ant  = alvo
            nome_ger = GERADORES_CATALOGO.get(alvo, {}).get('nome', alvo)
            if _visivel(y_cur, y0 + TITULO_H, y0 + h):
                _separador_categoria(janela, x0, y_cur, w, nome_ger, cor_cat)
            y_cur += 28
            num_geradores_visiveis += 1

        if _visivel(y_cur, y0 + TITULO_H, y0 + h):
            _linha_upgrade(janela, x0, y_cur, w, item, cor_cat, mouse_pos)
        y_cur += ROW_UPG

    janela.set_clip(None)
    num_grupos = len({item['alvo'] for item in itens})
    conteudo_h = len(itens) * ROW_UPG + num_grupos * 28 + TITULO_H + 20
    _scrollbar(janela, 'upgrades', x0, y0, w, h, TITULO_H, scroll_y, conteudo_h)


def _itens_upgrade(eco, upg):
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
        for suf in ('x2', 'x5', 'x10'):
            uid = f'upgrade_{id_ger}_{suf}'
            if uid in UPGRADES_CATALOGO:
                dado = UPGRADES_CATALOGO[uid]
                comprado = uid in ids_comprados
                _, pode  = upg_mod.pode_comprar(upg, eco, uid)
                resultado.append({**dado, 'comprado': comprado, 'pode': pode})
    return resultado


def _linha_upgrade(janela, x0, y, w, item, cor_cat, mouse_pos=(0, 0)):
    comprado = item.get('comprado', False)
    pode     = item.get('pode', False)

    if comprado:
        bg, stripe = (10, 12, 22), DARK_GREY
    elif pode:
        bg, stripe = (16, 36, 22), cor_cat
    else:
        bg, stripe = CARD_BG, _escurecer(cor_cat, 0.35)

    pygame.draw.rect(janela, bg, (x0, y, w, ROW_UPG - 1))
    pygame.draw.rect(janela, stripe, (x0, y, 4, ROW_UPG - 1))

    nome_cor = MID_GREY if comprado else (WHITE if pode else GREY)
    surf = _f['nome'].render(item['nome'], True, nome_cor)
    janela.blit(surf, (x0 + 14, y + 6))

    fator_txt = f'× {int(item["fator"])}  produção'
    surf = _f['tiny'].render(fator_txt, True, TEAL if not comprado else DARK_GREY)
    janela.blit(surf, (x0 + 14, y + 24))

    if comprado:
        # Check verde
        surf = _f['btn'].render('[OK] POSSUIDO', True, (30, 90, 50))
        janela.blit(surf, (x0 + w - surf.get_width() - PAD, y + (ROW_UPG - surf.get_height()) // 2))
    else:
        _, cs = display.formatar_numero(item['custo'])
        btn_w, btn_h = 94, 30
        btn_x = x0 + w - btn_w - PAD
        btn_y = y + (ROW_UPG - btn_h) // 2
        btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        _botao_comprar(janela, btn_rect, cs, pode, mouse_pos)
        if pode:
            registrar_botao(btn_rect, f'comprar upgrade {item["id"]}')

    pygame.draw.line(janela, (20, 18, 34), (x0, y + ROW_UPG - 1), (x0 + w, y + ROW_UPG - 1))


# ---------------------------------------------------------------------------
# Painel direito — INFO / AÇÕES / LOG
# ---------------------------------------------------------------------------
def _painel_info(janela, eco, upg, prog, mensagens, mouse_pos=(0, 0)):
    x0, y0, w, h = INFO_X, HUD_H, INFO_W, PANEL_H
    pygame.draw.rect(janela, PANEL_BG, (x0, y0, w, h))

    TITULO_H = 34
    _cabecalho_painel(janela, x0, y0, w, TITULO_H, 'PROGRESSO', WHITE)
    y = y0 + TITULO_H + 6

    nivel    = prog.get('nivel', 1)
    cristais = prog.get('cristais_revolucao', 0)
    fragmen  = prog.get('fragmentos_ascensao', 0)
    num_rev  = prog.get('num_revolucoes', 0)
    num_asc  = prog.get('num_ascensoes', 0)
    vitoria  = prog.get('vitoria', False)
    marcos   = prog.get('marcos_atingidos', [])

    # Stats em grid 2×2
    _stat_box(janela, x0 + PAD,           y,  (w - PAD*3) // 2, 38, 'Revoluções', str(num_rev),  ORANGE)
    _stat_box(janela, x0 + PAD*2 + (w - PAD*3)//2, y, (w - PAD*3) // 2, 38, 'Ascensões', str(num_asc), PURPLE)
    y += 44
    _stat_box(janela, x0 + PAD,           y,  (w - PAD*3) // 2, 38, 'Cristais',   str(cristais), GOLD)
    _stat_box(janela, x0 + PAD*2 + (w - PAD*3)//2, y, (w - PAD*3) // 2, 38, 'Fragmentos', str(fragmen), TEAL)
    y += 50

    # Marcos
    surf = _f['hdr'].render(f'MARCOS  {len(marcos)} / 13', True, GREY)
    janela.blit(surf, (x0 + PAD, y)); y += 18
    for mid in marcos[-3:]:
        surf = _f['tiny'].render(f'  >> {mid}', True, GOLD)
        janela.blit(surf, (x0 + PAD, y)); y += 16
    if len(marcos) > 3:
        surf = _f['tiny'].render(f'  ... +{len(marcos)-3} mais', True, DARK_GREY)
        janela.blit(surf, (x0 + PAD, y)); y += 16
    y += 4

    if vitoria:
        _banner_vitoria(janela, x0, y, w); y += 36

    # Separador
    _separador_h(janela, x0, y, w); y += 12

    # ── REVOLUÇÃO ───────────────────────────────────────────────────────
    _, pode_rev   = prog_mod.pode_revolucao(eco, prog)
    _, pontos_max = economia.obter_pontos_run_max(eco)
    limiar_rev    = LIMIAR_REVOLUCAO_BASE * (FATOR_LIMIAR_REVOLUCAO ** num_rev)
    _, lim_s      = display.formatar_numero(limiar_rev)

    if pode_rev:
        crist_est = max(1, int(math.floor(math.sqrt(pontos_max / limiar_rev))))
        y = _card_acao(janela, x0, y, w, mouse_pos,
                       titulo='REVOLUÇÃO DISPONÍVEL',
                       subtitulo=f'+{crist_est} cristal(is)  •  limiar: {lim_s}',
                       cmd='revolucao',
                       label_btn='EXECUTAR',
                       cor=ORANGE)
    else:
        pct_rev = min(1.0, pontos_max / limiar_rev) if limiar_rev > 0 else 0
        _, falta_s = display.formatar_numero(max(0, limiar_rev - pontos_max))
        surf = _f['hdr'].render('REVOLUÇÃO', True, _escurecer(ORANGE, 0.7))
        janela.blit(surf, (x0 + PAD, y)); y += 20
        _barra(janela, x0 + PAD, y, w - PAD*2, 10, pct_rev, ORANGE, (28, 20, 10))
        y += 14
        surf = _f['tiny'].render(f'Faltam {falta_s} pts', True, MID_GREY)
        janela.blit(surf, (x0 + PAD, y)); y += 18

    _separador_h(janela, x0, y, w); y += 12

    # ── ASCENSÃO ────────────────────────────────────────────────────────
    _, pode_asc = prog_mod.pode_ascensao(prog)

    if pode_asc:
        y = _card_acao(janela, x0, y, w, mouse_pos,
                       titulo='ASCENSÃO DISPONÍVEL',
                       subtitulo=f'+1 fragmento  •  expoente ^{1+(fragmen+1)*0.15:.2f}',
                       cmd='ascensao',
                       label_btn='ASCENDER',
                       cor=PURPLE)
    else:
        faltam = max(0, REVOLUCOES_P_ASCENSAO - num_rev)
        surf = _f['hdr'].render('ASCENSÃO', True, _escurecer(PURPLE, 0.7))
        janela.blit(surf, (x0 + PAD, y)); y += 20
        pct_asc = num_rev / REVOLUCOES_P_ASCENSAO
        _barra(janela, x0 + PAD, y, w - PAD*2, 10, pct_asc, PURPLE, (20, 10, 32))
        y += 14
        surf = _f['tiny'].render(f'Faltam {faltam} rev. ({num_rev}/{REVOLUCOES_P_ASCENSAO})', True, MID_GREY)
        janela.blit(surf, (x0 + PAD, y)); y += 18

    _separador_h(janela, x0, y, w); y += 8

    # ── LOG ─────────────────────────────────────────────────────────────
    surf = _f['hdr'].render('LOG', True, MID_GREY)
    janela.blit(surf, (x0 + PAD, y)); y += 18

    for msg in mensagens[:10]:
        if y + ROW_MSG > y0 + h - 6:
            break
        if msg.startswith('$'):
            cor, prefix = GOLD, '>> '
        elif '[ERRO]' in msg:
            cor, prefix = RED, '[!] '
        else:
            cor, prefix = (160, 155, 185), '   '
        txt = (prefix + msg.lstrip('$ '))[:54]
        surf = _f['msg'].render(txt, True, cor)
        janela.blit(surf, (x0 + PAD, y)); y += ROW_MSG


def _stat_box(janela, x, y, w, h, label, valor, cor):
    pygame.draw.rect(janela, _escurecer(cor, 0.10), (x, y, w, h), border_radius=4)
    pygame.draw.rect(janela, _escurecer(cor, 0.35), (x, y, w, h), width=1, border_radius=4)
    surf_l = _f['tiny'].render(label, True, _escurecer(cor, 0.75))
    surf_v = _f['hdr'].render(valor, True, cor)
    janela.blit(surf_l, (x + 6, y + 3))
    janela.blit(surf_v, (x + 6, y + 18))


def _card_acao(janela, x0, y, w, mouse_pos, titulo, subtitulo, cmd, label_btn, cor):
    """Desenha um card de ação disponível (revolução/ascensão) e registra o botão."""
    card_h = 72
    # Fundo pulsante
    t      = time.time()
    pulse  = 0.5 + 0.5 * math.sin(t * 2.0)
    bg_cor = tuple(max(0, int(c * (0.18 + 0.06 * pulse))) for c in cor)
    pygame.draw.rect(janela, bg_cor, (x0 + PAD, y, w - PAD*2, card_h), border_radius=6)
    brd = tuple(min(255, int(c * (0.7 + 0.3 * pulse))) for c in cor)
    pygame.draw.rect(janela, brd, (x0 + PAD, y, w - PAD*2, card_h), width=2, border_radius=6)

    surf = _f['titulo'].render(titulo, True, _clarear(cor, 1.15))
    janela.blit(surf, (x0 + PAD + 10, y + 8))
    surf = _f['tiny'].render(subtitulo, True, _escurecer(cor, 0.85))
    janela.blit(surf, (x0 + PAD + 10, y + 30))

    btn_w, btn_h = 136, 28
    btn_x = x0 + w - btn_w - PAD*2
    btn_y = y + (card_h - btn_h) // 2
    btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
    hover    = btn_rect.collidepoint(mouse_pos)

    btn_bg  = _escurecer(cor, 0.65) if hover else _escurecer(cor, 0.45)
    btn_brd = _clarear(cor, 1.35)   if hover else cor
    pygame.draw.rect(janela, btn_bg,  btn_rect, border_radius=4)
    pygame.draw.rect(janela, btn_brd, btn_rect, width=2, border_radius=4)
    surf = _f['btn'].render(label_btn, True, WHITE)
    janela.blit(surf, (btn_x + (btn_w - surf.get_width()) // 2,
                        btn_y + (btn_h - surf.get_height()) // 2))
    registrar_botao(btn_rect, cmd)

    return y + card_h + 10


def _banner_vitoria(janela, x0, y, w):
    pygame.draw.rect(janela, (55, 40, 5), (x0, y, w, 32), border_radius=4)
    pygame.draw.rect(janela, GOLD, (x0, y, w, 32), width=2, border_radius=4)
    surf = _f['hdr'].render('*** PONTO OMEGA - VITORIA! ***', True, GOLD)
    janela.blit(surf, (x0 + (w - surf.get_width()) // 2, y + 8))


def _separador_h(janela, x0, y, w):
    pygame.draw.line(janela, (30, 26, 50), (x0 + PAD, y), (x0 + w - PAD, y))
    pygame.draw.line(janela, (45, 38, 72), (x0 + PAD + 10, y), (x0 + w - PAD - 10, y))


# ---------------------------------------------------------------------------
# Bottom bar
# ---------------------------------------------------------------------------
def _bottom_bar(janela, mouse_pos=(0, 0)):
    y0 = H - BOTTOM_H
    pygame.draw.rect(janela, (10, 8, 20), (0, y0, W, BOTTOM_H))
    pygame.draw.line(janela, BORDER_HL, (0, y0), (W, y0), 1)

    surf = _f['tiny'].render('O jogo é salvo ao fechar ou clicar em Salvar e Sair', True, DARK_GREY)
    janela.blit(surf, (PAD, y0 + 10))

    _botao_barra(janela, W - 310, y0 + 4, 136, 24, 'NOVO JOGO',     CRIMSON,  'novo jogo', mouse_pos)
    _botao_barra(janela, W - 162, y0 + 4, 152, 24, 'SALVAR E SAIR', (80, 75, 110), 'sair', mouse_pos)


def _botao_barra(janela, x, y, w, h, texto, cor, cmd, mouse_pos):
    rect  = pygame.Rect(x, y, w, h)
    hover = rect.collidepoint(mouse_pos)
    bg    = _escurecer(cor, 0.55) if hover else _escurecer(cor, 0.30)
    brd   = _clarear(cor, 1.3)   if hover else cor
    pygame.draw.rect(janela, bg,  rect, border_radius=3)
    pygame.draw.rect(janela, brd, rect, width=1, border_radius=3)
    surf  = _f['btn'].render(texto, True, WHITE if hover else _clarear(cor, 1.4))
    janela.blit(surf, (x + (w - surf.get_width()) // 2, y + (h - surf.get_height()) // 2))
    registrar_botao(rect, cmd)


# ---------------------------------------------------------------------------
# Cabeçalho de painel
# ---------------------------------------------------------------------------
def _cabecalho_painel(janela, x0, y0, w, h, titulo, cor):
    pygame.draw.rect(janela, HDR_BG, (x0, y0, w, h))
    # linha de destaque em baixo do cabeçalho
    pygame.draw.line(janela, BORDER_HL, (x0, y0 + h - 1), (x0 + w, y0 + h - 1), 1)
    # acento lateral esquerdo
    pygame.draw.rect(janela, BORDER_HL, (x0, y0, 3, h))
    surf = _f['titulo'].render(titulo, True, cor)
    janela.blit(surf, (x0 + 12, y0 + (h - surf.get_height()) // 2))


# ---------------------------------------------------------------------------
# Helpers de cor e efeito
# ---------------------------------------------------------------------------
def _pulsar(cor_a, cor_b, freq=1.0):
    t   = time.time()
    mix = 0.5 + 0.5 * math.sin(t * freq * math.pi)
    return tuple(int(cor_a[i] + (cor_b[i] - cor_a[i]) * mix) for i in range(3))


def _escurecer(cor, fator):
    return tuple(max(0, int(c * fator)) for c in cor)


def _clarear(cor, fator):
    return tuple(min(255, int(c * fator)) for c in cor)


def _desenhar_particulas(janela):
    _, particulas = obter_particulas()
    for p in particulas:
        frac  = p['vida'] / p['vida_max']
        alpha = int(255 * frac)
        surf  = _f['btn'].render(p['texto'], True, p['cor'])
        surf.set_alpha(alpha)
        janela.blit(surf, (int(p['x'] - surf.get_width() // 2), int(p['y'])))


def _desenhar_flash(janela):
    _, flash = obter_flash()
    if flash is None or flash['alpha'] <= 0:
        return
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((*flash['cor'], int(flash['alpha'])))
    janela.blit(overlay, (0, 0))


def _scrollbar(janela, painel, x_panel, y_panel, panel_w, panel_h, titulo_h, scroll_y, conteudo_h):
    vis_h   = panel_h - titulo_h
    track_x = x_panel + panel_w - 8
    track_y = y_panel + titulo_h
    # Trilha — sempre visível
    pygame.draw.rect(janela, (18, 16, 32), (track_x, track_y, 6, vis_h))
    pygame.draw.rect(janela, (35, 30, 55), (track_x, track_y, 6, vis_h), width=1)

    if conteudo_h <= vis_h:
        # Thumb inativo (painel não precisa de scroll)
        pygame.draw.rect(janela, (38, 34, 60), (track_x + 1, track_y + 2, 4, vis_h - 4), border_radius=2)
        _ui['sb_info'].pop(painel, None)
        return

    thumb_h    = max(28, int(vis_h * vis_h / conteudo_h))
    max_scroll = max(1, conteudo_h - vis_h)
    thumb_y    = track_y + int((vis_h - thumb_h) * min(scroll_y, max_scroll) / max_scroll)
    drag       = _ui['drag']
    arrastando = drag is not None and drag['painel'] == painel
    cor        = (180, 160, 230) if arrastando else (110, 90, 160)
    pygame.draw.rect(janela, cor, (track_x + 1, thumb_y, 4, thumb_h), border_radius=2)
    _ui['sb_info'][painel] = {
        'track_x': track_x, 'track_y': track_y, 'track_h': vis_h,
        'thumb_y': thumb_y,  'thumb_h': thumb_h, 'conteudo_h': conteudo_h,
    }


def _visivel(y, y_min, y_max):
    return y_min - ROW_GER <= y <= y_max


# =============================================================================
# Orquestrador — loop principal
# =============================================================================

def _inicializar_jogo():
    """
    Carrega o save existente ou cria um novo estado inicial com 2 mineradoras.

    Assertiva de entrada:
        (nenhuma) — arquivo saves/save.json pode ou não existir

    Assertiva de saída:
        (dict_eco, dict_upg, dict_prog, str) — estados prontos e mensagem de boas-vindas;
                                               sem código de retorno (nunca falha)
    """
    cod, dados = persistencia.carregar_jogo()
    if cod == 0:
        eco, upg, prog = dados
        return eco, upg, prog, '[SAVE] Jogo carregado com sucesso!'
    _, eco  = economia.inicializar_estado()
    _, upg  = upg_mod.inicializar_upgrades()
    _, prog = prog_mod.inicializar_progresso()
    _, eco  = economia.adicionar_gerador(eco, 'mineradora_vermelha')
    _, eco  = economia.adicionar_gerador(eco, 'mineradora_vermelha')
    return eco, upg, prog, 'Bem-vindo! Você ganhou 2 Mineradoras Vermelhas grátis.'


def _tick_jogo(eco, upg, prog, delta):
    """
    Executa um tick de simulação: gera pontos, aplica upgrades e verifica progresso.

    Assertiva de entrada:
        eco   (dict)  — estado válido retornado por economia.inicializar_estado
        upg   (dict)  — estado válido retornado por upgrades.inicializar_upgrades
        prog  (dict)  — estado válido retornado por progresso.inicializar_progresso
        delta (float) — segundos decorridos desde o último tick; >= 0

    Assertiva de saída:
        (dict_eco, dict_upg, dict_prog, list[str], bool) —
            estados atualizados, lista de novos marcos atingidos (pode ser []),
            flag de vitória
    """
    _, eco           = economia.aplicar_geracao(eco, delta)
    _, fatores       = upg_mod.calcular_fatores_por_gerador(upg)
    _, eco           = economia.aplicar_efeitos_upgrades(eco, fatores)
    _, prog, novos   = prog_mod.verificar_progresso(eco, prog)
    _, prog, vitoria = prog_mod.verificar_vitoria(eco, prog)
    return eco, upg, prog, novos, vitoria


def _processar_clique(pos, eco, upg, prog):
    """
    Identifica o botão clicado e executa a ação correspondente.

    Assertiva de entrada:
        pos  (tuple[int, int]) — coordenadas (x, y) do clique
        eco  (dict) — estado válido retornado por economia.inicializar_estado
        upg  (dict) — estado válido retornado por upgrades.inicializar_upgrades
        prog (dict) — estado válido retornado por progresso.inicializar_progresso

    Assertiva de saída:
        (codigo, eco, upg, prog, msg, acao, cmd)
            codigo (int)  — 0 se sucesso, -1 se erro
            acao   (str|None) — 'sair', 'novo_jogo' ou None para ações especiais
            cmd    (str)  — comando original ou '' se nenhum botão foi clicado
            msg    (str)  — mensagem de feedback para o log
    """
    _, cmd = botao_em(pos)
    if not cmd:
        return (0, eco, upg, prog, '', None, '')
    if cmd == 'sair':
        return (0, eco, upg, prog, '', 'sair', cmd)
    if cmd == 'novo jogo':
        return (0, eco, upg, prog, '', 'novo_jogo', cmd)
    codigo, eco, upg, prog, msg = processar_comando(cmd, eco, upg, prog)
    return (codigo, eco, upg, prog, msg, None, cmd)


def _scroll_para_painel(pos_x, largura_ger, x_upg, largura_upg):
    """
    Determina em qual painel o cursor está posicionado para aplicar scroll.

    Assertiva de entrada:
        pos_x      (int) — coordenada x do mouse
        largura_ger (int) — largura do painel de geradores
        x_upg       (int) — x inicial do painel de upgrades
        largura_upg (int) — largura do painel de upgrades

    Assertiva de saída:
        'geradores' — cursor está sobre o painel de geradores
        'upgrades'  — cursor está sobre o painel de upgrades
        None        — cursor está fora de ambos os painéis scrolláveis
    """
    if pos_x < largura_ger:
        return 'geradores'
    if x_upg <= pos_x < x_upg + largura_upg:
        return 'upgrades'
    return None


def main():
    """
    Ponto de entrada do modo pygame: inicializa, roda o loop e salva ao sair.

    Assertiva de entrada:
        (nenhuma) — pygame deve estar disponível; saves/ pode ou não existir

    Assertiva de saída:
        (nenhuma) — função bloqueante; encerra ao fechar a janela, Esc/Q ou
                    botão 'Salvar e Sair'; estado salvo antes de encerrar
    """
    _, janela, clock = inicializar_janela()
    inicializar_ui()

    eco, upg, prog, msg_inicial = _inicializar_jogo()
    mensagens = [msg_inicial]

    ultimo_tick = time.perf_counter()

    _TITULO_H = 34
    ALTURA_CONTEUDO_GER = 40 * ROW_GER + 4 * 28 + _TITULO_H + 20
    ALTURA_CONTEUDO_UPG = 40 * (28 + 3 * ROW_UPG) + _TITULO_H + 20
    PANEL_H_VIS = PANEL_H - _TITULO_H

    rodando = True
    while rodando:
        agora = time.perf_counter()
        delta = agora - ultimo_tick
        ultimo_tick = agora

        eco, upg, prog, novos_marcos, vitoria = _tick_jogo(eco, upg, prog, delta)

        for marco in novos_marcos:
            mensagens.insert(0, f'$ Marco atingido: {marco}')
            registrar_flash('marco')
        if vitoria and '$$$ PONTO ÔMEGA' not in (mensagens[0] if mensagens else ''):
            mensagens.insert(0, '$$$ PONTO ÔMEGA ATINGIDO! VITÓRIA!')
            registrar_flash('marco')
        mensagens = mensagens[:14]

        atualizar_particulas(delta)
        atualizar_flash(delta)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                persistencia.salvar_jogo(eco, upg, prog)
                rodando = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    persistencia.salvar_jogo(eco, upg, prog)
                    rodando = False
                    break

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                _ui['drag'] = None

            if event.type == pygame.MOUSEMOTION and _ui['drag']:
                drag  = _ui['drag']
                info  = _ui['sb_info'].get(drag['painel'], {})
                if info:
                    new_thumb_top = event.pos[1] - drag['offset_y']
                    rng  = max(1, info['track_h'] - info['thumb_h'])
                    frac = max(0.0, min(1.0, (new_thumb_top - info['track_y']) / rng))
                    _ui[f"scroll_{drag['painel']}"] = int(frac * max(1, info['conteudo_h'] - info['track_h']))

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Verifica clique na scrollbar antes dos botões de jogo
                mx, my = event.pos
                sb_clicado = False
                for painel, info in _ui['sb_info'].items():
                    tx = info['track_x']
                    if tx - 3 <= mx <= tx + 8 and info['track_y'] <= my <= info['track_y'] + info['track_h']:
                        sb_clicado = True
                        ty, th = info['thumb_y'], info['thumb_h']
                        if ty <= my <= ty + th:
                            _ui['drag'] = {'painel': painel, 'offset_y': my - ty}
                        else:
                            # clique na trilha — pula direto
                            rng  = max(1, info['track_h'] - th)
                            frac = max(0.0, min(1.0, (my - info['track_y'] - th // 2) / rng))
                            _ui[f'scroll_{painel}'] = int(frac * max(1, info['conteudo_h'] - info['track_h']))
                        break
                if sb_clicado:
                    continue

                cod, eco, upg, prog, msg, acao, cmd = _processar_clique(
                    event.pos, eco, upg, prog)
                if msg:
                    mensagens.insert(0, msg)
                    mensagens = mensagens[:14]

                if cod == 0 and cmd and '[ERRO]' not in msg:
                    if cmd == 'revolucao':
                        registrar_flash('revolucao')
                        _ui['scroll_upgrades'] = 0
                        adicionar_particula(event.pos[0], event.pos[1] - 20, 'REVOLUCAO!', (230, 140, 40))
                    elif cmd == 'ascensao':
                        registrar_flash('ascensao')
                        _ui['scroll_upgrades'] = 0
                        adicionar_particula(event.pos[0], event.pos[1] - 20, 'ASCENSAO!', (160, 80, 230))
                    elif cmd.startswith('comprar gerador') and '[ERRO]' not in msg:
                        adicionar_particula(event.pos[0], event.pos[1], '+1', (60, 200, 90))
                    elif cmd.startswith('comprar upgrade') and '[ERRO]' not in msg:
                        adicionar_particula(event.pos[0], event.pos[1], 'x upgrade!', (255, 200, 55))

                if acao == 'sair':
                    persistencia.salvar_jogo(eco, upg, prog)
                    rodando = False
                    break
                elif acao == 'novo_jogo':
                    _, eco  = economia.inicializar_estado()
                    _, upg  = upg_mod.inicializar_upgrades()
                    _, prog = prog_mod.inicializar_progresso()
                    _, eco  = economia.adicionar_gerador(eco, 'mineradora_vermelha')
                    _, eco  = economia.adicionar_gerador(eco, 'mineradora_vermelha')
                    mensagens = ['Novo jogo iniciado! O save será sobrescrito ao sair.']
                    inicializar_ui()

            if event.type == pygame.MOUSEWHEEL:
                mx, my = pygame.mouse.get_pos()
                painel = _scroll_para_painel(mx, 430, 430, 410)
                if painel == 'geradores':
                    atualizar_scroll('geradores', event.y, ALTURA_CONTEUDO_GER, PANEL_H_VIS)
                elif painel == 'upgrades':
                    ch = _ui['sb_info'].get('upgrades', {}).get('conteudo_h', ALTURA_CONTEUDO_UPG)
                    atualizar_scroll('upgrades', event.y, ch, PANEL_H_VIS)

        if not rodando:
            break

        mouse_pos = pygame.mouse.get_pos()
        renderizar_frame(janela, eco, upg, prog, mensagens, mouse_pos)
        clock.tick(60)

    fechar_janela()


if __name__ == '__main__':
    main()
