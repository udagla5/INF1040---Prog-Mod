# =============================================================================
# interface_pygame/ui_estado.py — TAD de estado da interface pygame
# INF1040 · 2026.1 · Grupo 3WB
#
# Armazena: scroll dos painéis e registro de botões clicáveis.
# Não conhece os TADs de jogo. Não chama pygame diretamente.
# =============================================================================

__all__ = [
    'inicializar_ui',
    'obter_scroll',
    'atualizar_scroll',
    'limpar_botoes',
    'registrar_botao',
    'botao_em',
    # game feel
    'adicionar_particula',
    'atualizar_particulas',
    'obter_particulas',
    'registrar_flash',
    'atualizar_flash',
    'obter_flash',
]

_estado = {
    'scroll_geradores': 0,
    'scroll_upgrades':  0,
    'botoes': [],          # list[ (pygame.Rect, str_comando) ]
    'particulas': [],      # list[ dict ] — textos flutuantes
    'flash': None,         # dict | None — overlay de tela
}

_SCROLL_MIN = 0
_SCROLL_MAX = 5000
_SCROLL_PX  = 28           # pixels por tick de roda do mouse


def inicializar_ui():
    """
    Reseta o estado da UI para o início de sessão.
    Retornos:
        (0, None)
    """
    _estado['scroll_geradores'] = 0
    _estado['scroll_upgrades']  = 0
    _estado['botoes']           = []
    _estado['particulas']       = []
    _estado['flash']            = None
    return (0, None)


def obter_scroll(painel):
    """
    Retorna o offset de scroll atual de um painel.
    Parâmetros:
        painel (str) — 'geradores' | 'upgrades'
    Retornos:
        (0, int) — offset em pixels
        (1,   0) — painel desconhecido
    """
    chave = f'scroll_{painel}'
    if chave not in _estado:
        return (1, 0)
    return (0, _estado[chave])


def atualizar_scroll(painel, delta_ticks, altura_conteudo, altura_visivel):
    """
    Ajusta o scroll de um painel com base no evento de roda do mouse.
    Parâmetros:
        painel          (str) — 'geradores' | 'upgrades'
        delta_ticks     (int) — positivo = scroll para cima
        altura_conteudo (int) — altura total do conteúdo em pixels
        altura_visivel  (int) — altura da janela de visualização
    Retornos:
        (0, int) — novo offset
        (1,   0) — painel desconhecido
    """
    chave = f'scroll_{painel}'
    if chave not in _estado:
        return (1, 0)

    max_scroll = max(0, altura_conteudo - altura_visivel)
    novo = _estado[chave] - delta_ticks * _SCROLL_PX
    novo = max(0, min(novo, max_scroll))
    _estado[chave] = novo
    return (0, novo)


def limpar_botoes():
    """
    Descarta todos os botões registrados (chamado a cada frame antes de renderizar).
    Retornos:
        (0, None)
    """
    _estado['botoes'] = []
    return (0, None)


def registrar_botao(rect, comando):
    """
    Registra um botão clicável.
    Parâmetros:
        rect    (pygame.Rect) — posição absoluta na tela
        comando (str)         — string de comando a retornar ao ser clicado
    Retornos:
        (0, None)
    """
    _estado['botoes'].append((rect, comando))
    return (0, None)


def botao_em(pos):
    """
    Verifica se a posição clicada está sobre algum botão.
    Parâmetros:
        pos (tuple) — (x, y) do clique
    Retornos:
        (0, str ) — comando do botão clicado
        (0, None) — nenhum botão na posição
    """
    for rect, cmd in _estado['botoes']:
        if rect.collidepoint(pos):
            return (0, cmd)
    return (0, None)


# ---------------------------------------------------------------------------
# Partículas flutuantes
# ---------------------------------------------------------------------------

def adicionar_particula(x, y, texto, cor=(255, 200, 55)):
    """
    Spawna um texto flutuante na posição (x, y).
    Parâmetros:
        x, y  (float) — posição inicial na tela
        texto (str)   — texto a exibir
        cor   (tuple) — cor RGB
    Retornos:
        (0, None)
    """
    import random
    _estado['particulas'].append({
        'x':       float(x) + random.uniform(-10, 10),
        'y':       float(y),
        'vx':      random.uniform(-18, 18),
        'vy':      -75.0,
        'texto':   texto,
        'cor':     cor,
        'vida':    1.4,
        'vida_max': 1.4,
    })
    return (0, None)


def atualizar_particulas(delta):
    """
    Avança a simulação das partículas pelo tempo delta (segundos).
    Remove as que expiraram.
    Retornos:
        (0, None)
    """
    vivas = []
    for p in _estado['particulas']:
        p['vida'] -= delta
        p['x'] += p['vx'] * delta
        p['y'] += p['vy'] * delta
        p['vy'] += 30 * delta   # leve gravidade
        if p['vida'] > 0:
            vivas.append(p)
    _estado['particulas'] = vivas
    return (0, None)


def obter_particulas():
    """
    Retorna cópia da lista de partículas ativas.
    Retornos:
        (0, list[dict])
    """
    return (0, list(_estado['particulas']))


# ---------------------------------------------------------------------------
# Flash de tela
# ---------------------------------------------------------------------------

_FLASH_CORES = {
    'revolucao': (230, 140,  40),
    'ascensao':  (160,  80, 230),
    'compra':    ( 60, 200,  90),
    'marco':     (255, 200,  55),
}

def registrar_flash(tipo):
    """
    Inicia um flash de overlay na tela.
    Parâmetros:
        tipo (str) — 'revolucao' | 'ascensao' | 'compra' | 'marco'
    Retornos:
        (0, None)
    """
    cor = _FLASH_CORES.get(tipo, (255, 255, 255))
    alpha_inicial = 160 if tipo in ('revolucao', 'ascensao') else 80
    _estado['flash'] = {
        'cor':   cor,
        'alpha': float(alpha_inicial),
        'decay': 280.0,
    }
    return (0, None)


def atualizar_flash(delta):
    """
    Decai o alpha do flash de tela.
    Retornos:
        (0, None)
    """
    f = _estado['flash']
    if f is not None:
        f['alpha'] -= f['decay'] * delta
        if f['alpha'] <= 0:
            _estado['flash'] = None
    return (0, None)


def obter_flash():
    """
    Retorna o estado atual do flash de tela.
    Retornos:
        (0, dict | None)
    """
    return (0, _estado['flash'])
