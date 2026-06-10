# =============================================================================
# main_pygame.py — Front-end pygame do idle game
# INF1040 · 2026.1 · Grupo 3WB
#
# Uso: python main_pygame.py
#
# Este arquivo é o orquestrador: conecta os TADs existentes (economia,
# upgrades, progresso, persistencia) com a interface visual pygame.
# Não modifica nenhum arquivo original do projeto.
# =============================================================================

import sys
import time
import pygame

# TADs existentes (inalterados)
import economia
import upgrades  as upg_mod
import progresso as prog_mod
import persistencia
from main import processar_comando          # reusa a lógica de comandos já testada

# Nova camada de interface (apenas desenho + estado de UI)
from interface_pygame.renderizador import inicializar_janela, fechar_janela, renderizar_frame
from interface_pygame.ui_estado    import (
    inicializar_ui, botao_em, atualizar_scroll,
    adicionar_particula, atualizar_particulas,
    registrar_flash, atualizar_flash,
)

# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _inicializar_jogo():
    """
    Carrega save existente ou cria estado zerado com bônus inicial.
    Retornos:
        (eco, upg, prog, str_mensagem)
    """
    cod, dados = persistencia.carregar_jogo()
    if cod == 0:
        eco, upg, prog = dados
        return eco, upg, prog, '[SAVE] Jogo carregado com sucesso!'

    _, eco  = economia.inicializar_estado()
    _, upg  = upg_mod.inicializar_upgrades()
    _, prog = prog_mod.inicializar_progresso()
    # Bônus de boas-vindas
    _, eco = economia.adicionar_gerador(eco, 'mineradora_vermelha')
    _, eco = economia.adicionar_gerador(eco, 'mineradora_vermelha')
    return eco, upg, prog, 'Bem-vindo! Você ganhou 2 Mineradoras Vermelhas grátis.'


def _tick_jogo(eco, upg, prog, delta):
    """
    Executa um tick de simulação: gera pontos, aplica upgrades e verifica progresso.
    Retornos:
        (eco, upg, prog, novos_marcos, vitoria)
    """
    _, eco           = economia.aplicar_geracao(eco, delta)
    _, fatores       = upg_mod.calcular_fatores_por_gerador(upg)
    _, eco           = economia.aplicar_efeitos_upgrades(eco, fatores)
    _, prog, novos   = prog_mod.verificar_progresso(eco, prog)
    _, prog, vitoria = prog_mod.verificar_vitoria(eco, prog)
    return eco, upg, prog, novos, vitoria


def _processar_clique(pos, eco, upg, prog):
    """
    Identifica o botão clicado e executa o comando correspondente.
    Retornos:
        (codigo, eco, upg, prog, mensagem, acao_especial, cmd)
        acao_especial: None | 'sair' | 'salvar' | 'novo_jogo'
    """
    _, cmd = botao_em(pos)
    if not cmd:
        return (0, eco, upg, prog, '', None, '')

    if cmd == 'sair':
        return (0, eco, upg, prog, '', 'sair', cmd)

    if cmd == 'novo jogo':
        return (0, eco, upg, prog, '', 'novo_jogo', cmd)

    # Qualquer outro comando passa pelo processador testado de main.py
    codigo, eco, upg, prog, msg = processar_comando(cmd, eco, upg, prog)
    return (codigo, eco, upg, prog, msg, None, cmd)


def _scroll_para_painel(pos_x, largura_ger, x_upg, largura_upg):
    """
    Decide qual painel recebe o scroll com base na posição X do mouse.
    Retornos:
        (str) 'geradores' | 'upgrades' | None
    """
    if pos_x < largura_ger:
        return 'geradores'
    if x_upg <= pos_x < x_upg + largura_upg:
        return 'upgrades'
    return None


# ---------------------------------------------------------------------------
# Loop principal
# ---------------------------------------------------------------------------

def main():
    _, janela, clock = inicializar_janela()
    inicializar_ui()

    eco, upg, prog, msg_inicial = _inicializar_jogo()
    mensagens = [msg_inicial]

    ultimo_tick = time.perf_counter()

    # Alturas de conteúdo para scroll (aprox.)
    # 40 geradores × 58px + 4 cabeçalhos × 26px ≈ 2424px
    ALTURA_CONTEUDO_GER = 40 * 58 + 4 * 26 + 32
    # Upgrades: variável, estimativa
    ALTURA_CONTEUDO_UPG = 120 * 52 + 40 * 22 + 32
    PANEL_H_VIS = 634    # H - HUD_H - BOTTOM_H

    rodando = True
    while rodando:
        agora = time.perf_counter()
        delta = agora - ultimo_tick
        ultimo_tick = agora

        # ── Tick de economia ────────────────────────────────────────────
        eco, upg, prog, novos_marcos, vitoria = _tick_jogo(eco, upg, prog, delta)

        for marco in novos_marcos:
            mensagens.insert(0, f'$ Marco atingido: {marco}')
            registrar_flash('marco')
        if vitoria and '$$$ PONTO ÔMEGA' not in (mensagens[0] if mensagens else ''):
            mensagens.insert(0, '$$$ PONTO ÔMEGA ATINGIDO! VITÓRIA!')
            registrar_flash('marco')
        mensagens = mensagens[:14]

        # ── Atualiza efeitos visuais ─────────────────────────────────────
        atualizar_particulas(delta)
        atualizar_flash(delta)

        # ── Eventos ─────────────────────────────────────────────────────
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

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                cod, eco, upg, prog, msg, acao, cmd = _processar_clique(
                    event.pos, eco, upg, prog)
                if msg:
                    mensagens.insert(0, msg)
                    mensagens = mensagens[:14]

                # Efeitos de game feel por tipo de ação
                if cod == 0 and cmd and '[ERRO]' not in msg:
                    if cmd == 'revolucao':
                        registrar_flash('revolucao')
                        adicionar_particula(event.pos[0], event.pos[1] - 20,
                                            '🔁 REVOLUÇÃO!', (230, 140, 40))
                    elif cmd == 'ascensao':
                        registrar_flash('ascensao')
                        adicionar_particula(event.pos[0], event.pos[1] - 20,
                                            '⬆ ASCENSÃO!', (160, 80, 230))
                    elif cmd.startswith('comprar gerador') and msg and '[ERRO]' not in msg:
                        adicionar_particula(event.pos[0], event.pos[1],
                                            '+1', (60, 200, 90))
                    elif cmd.startswith('comprar upgrade') and msg and '[ERRO]' not in msg:
                        adicionar_particula(event.pos[0], event.pos[1],
                                            '× upgrade!', (255, 200, 55))

                if acao == 'sair':
                    persistencia.salvar_jogo(eco, upg, prog)
                    rodando = False
                    break
                elif acao == 'novo_jogo':
                    # Reinicia só na memória — o arquivo é sobrescrito ao sair
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
                    atualizar_scroll('geradores', event.y,
                                     ALTURA_CONTEUDO_GER, PANEL_H_VIS)
                elif painel == 'upgrades':
                    atualizar_scroll('upgrades', event.y,
                                     ALTURA_CONTEUDO_UPG, PANEL_H_VIS)

        if not rodando:
            break

        # ── Renderização ────────────────────────────────────────────────
        mouse_pos = pygame.mouse.get_pos()
        renderizar_frame(janela, eco, upg, prog, mensagens, mouse_pos)
        clock.tick(60)

    fechar_janela()


if __name__ == '__main__':
    main()
