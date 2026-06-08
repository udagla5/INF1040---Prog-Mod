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
]

_estado = {
    'scroll_geradores': 0,
    'scroll_upgrades':  0,
    'botoes': [],          # list[ (pygame.Rect, str_comando) ]
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
