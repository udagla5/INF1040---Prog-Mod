# =============================================================================
# gui.py — Interface real-time usando curses (macOS / Linux)
#           com fallback threading+ANSI para Windows
# INF1040 · 2026.1 · Grupo 3WB
#
# Execute com: python gui.py
# O modo é detectado automaticamente pelo sistema operacional.
# =============================================================================

import os
import sys
import time
import threading
import queue

import economia
import upgrades
import progresso
import display
import persistencia
from main import processar_comando

# ---------------------------------------------------------------------------
# Estado compartilhado (dict — sem classes)
# ---------------------------------------------------------------------------
_jogo = {
    'eco':   None,
    'upg':   None,
    'prog':  None,
    'msgs':  [],   # notificações e feedback
}

# ---------------------------------------------------------------------------
# Inicialização do estado
# ---------------------------------------------------------------------------
def _inicializar():
    cod, dados = persistencia.carregar_jogo()
    if cod == 0:
        eco, upg, prog = dados
        _jogo['msgs'].append("[SAVE] Jogo carregado!")
    else:
        _, eco  = economia.inicializar_estado()
        _, upg  = upgrades.inicializar_upgrades()
        _, prog = progresso.inicializar_progresso()
        _, eco  = economia.adicionar_gerador(eco, 'mineradora_vermelha')
        _, eco  = economia.adicionar_gerador(eco, 'mineradora_vermelha')
        _jogo['msgs'].append("Bem-vindo! Você ganhou 2 Mineradoras Vermelhas gratuitas (+0.2 pts/s).")
    _jogo['eco']  = eco
    _jogo['upg']  = upg
    _jogo['prog'] = prog

# ---------------------------------------------------------------------------
# Tick de jogo + processamento de comando
# ---------------------------------------------------------------------------
def _tick(delta, cmd=None):
    eco  = _jogo['eco']
    upg  = _jogo['upg']
    prog = _jogo['prog']

    _, eco           = economia.aplicar_geracao(eco, delta)
    _, fatores       = upgrades.calcular_fatores_por_gerador(upg)
    _, eco           = economia.aplicar_efeitos_upgrades(eco, fatores)
    _, prog, novos   = progresso.verificar_progresso(eco, prog)
    _, prog, vitoria = progresso.verificar_vitoria(eco, prog)

    for m in novos:
        _jogo['msgs'].insert(0, f"★ Marco: {m}")
    if vitoria:
        _jogo['msgs'].insert(0, "★ VITÓRIA! PONTO ÔMEGA ATINGIDO!")

    if cmd:
        _, eco, upg, prog, msg = processar_comando(cmd, eco, upg, prog)
        if msg:
            _jogo['msgs'].insert(0, msg)

    _jogo['msgs'] = _jogo['msgs'][:8]
    _jogo['eco']  = eco
    _jogo['upg']  = upg
    _jogo['prog'] = prog

# ---------------------------------------------------------------------------
# MODO A: curses (macOS / Linux)  ─────────────────────────────────────────
# ---------------------------------------------------------------------------
def _safe_addstr(win, y, x, texto, attr=0):
    """addstr tolerante a erros de encoding e de posição."""
    h, w = win.getmaxyx()
    if y < 0 or y >= h:
        return
    # Cortar linha no limite da janela
    texto = texto[:max(0, w - x - 1)]
    # Substituir caracteres problemáticos para curses
    texto = texto.encode('ascii', errors='replace').decode('ascii')
    try:
        if attr:
            win.addstr(y, x, texto, attr)
        else:
            win.addstr(y, x, texto)
    except Exception:
        pass

def _desenhar_curses(win, cmd_buffer):
    import curses
    h, w   = win.getmaxyx()
    eco    = _jogo['eco']
    upg    = _jogo['upg']
    prog   = _jogo['prog']

    _, tela   = display.renderizar_painel(eco, upg, prog)
    linhas_jogo = tela.split('\n')

    win.erase()

    # ── Área do jogo (da linha 0 até h-5) ─────────────────────────────
    area_h = max(1, h - 5)
    for i, linha in enumerate(linhas_jogo[:area_h]):
        _safe_addstr(win, i, 0, linha)

    # ── Separador ─────────────────────────────────────────────────────
    _safe_addstr(win, h - 5, 0, '─' * (w - 1))

    # ── Últimas mensagens (2 linhas) ──────────────────────────────────
    msgs = _jogo['msgs']
    for i, msg in enumerate(msgs[:2]):
        _safe_addstr(win, h - 4 + i, 2, msg)

    # ── Separador input ───────────────────────────────────────────────
    _safe_addstr(win, h - 2, 0, '─' * (w - 1))

    # ── Input ─────────────────────────────────────────────────────────
    prompt = '  > ' + ''.join(cmd_buffer)
    _safe_addstr(win, h - 1, 0, prompt, curses.A_BOLD)

    # Posicionar cursor no final do input
    cur_x = min(len(prompt), w - 2)
    try:
        win.move(h - 1, cur_x)
    except Exception:
        pass

    win.refresh()

def _executar_curses(stdscr):
    import curses
    curses.curs_set(1)
    stdscr.nodelay(True)
    stdscr.keypad(True)

    cmd_buffer  = []
    ultimo_tick = time.perf_counter()
    ultimo_ref  = 0.0

    while True:
        agora = time.perf_counter()
        delta = agora - ultimo_tick
        ultimo_tick = agora

        # ── Leitura de tecla (não-bloqueante) ─────────────────────────
        cmd_pronto = None
        try:
            ch = stdscr.getch()
        except Exception:
            ch = curses.ERR

        if ch != curses.ERR:
            if ch in (ord('\n'), ord('\r')):
                cmd_pronto = ''.join(cmd_buffer).strip()
                cmd_buffer.clear()
            elif ch in (curses.KEY_BACKSPACE, 127, 8):
                if cmd_buffer:
                    cmd_buffer.pop()
            elif 32 <= ch <= 126:
                cmd_buffer.append(chr(ch))

        # ── Encerrar ──────────────────────────────────────────────────
        if cmd_pronto is not None and cmd_pronto.lower() == 'sair':
            persistencia.salvar_jogo(_jogo['eco'], _jogo['upg'], _jogo['prog'])
            break

        # ── Tick do jogo ──────────────────────────────────────────────
        _tick(delta, cmd_pronto if cmd_pronto else None)

        # ── Redesenhar (a cada 500 ms ou após comando) ────────────────
        if agora - ultimo_ref >= 0.5 or cmd_pronto is not None:
            _desenhar_curses(stdscr, cmd_buffer)
            ultimo_ref = agora

        time.sleep(0.05)

def _iniciar_curses():
    import curses
    curses.wrapper(_executar_curses)

# ---------------------------------------------------------------------------
# MODO B: threading + ANSI (Windows / fallback)  ──────────────────────────
# ---------------------------------------------------------------------------
def _thread_input(fila, parar):
    while not parar.is_set():
        try:
            line = sys.stdin.readline()
            if line:
                fila.put(line.strip())
        except (EOFError, KeyboardInterrupt):
            fila.put('sair')
            break

def _iniciar_threading():
    fila  = queue.Queue()
    parar = threading.Event()

    t = threading.Thread(target=_thread_input, args=(fila, parar), daemon=True)
    t.start()

    ultimo_tick = time.perf_counter()
    ultimo_ref  = 0.0

    # Exibição inicial
    os.system('cls' if os.name == 'nt' else 'clear')
    _, tela = display.renderizar_painel(_jogo['eco'], _jogo['upg'], _jogo['prog'])
    print(tela)
    print("\n  > ", end='', flush=True)

    while True:
        agora = time.perf_counter()
        delta = agora - ultimo_tick
        ultimo_tick = agora

        cmd = None
        try:
            cmd = fila.get_nowait()
        except queue.Empty:
            pass

        if cmd and cmd.lower() == 'sair':
            persistencia.salvar_jogo(_jogo['eco'], _jogo['upg'], _jogo['prog'])
            parar.set()
            print("\nJogo salvo. Até logo!")
            break

        _tick(delta, cmd)

        if agora - ultimo_ref >= 1.0 or cmd is not None:
            os.system('cls' if os.name == 'nt' else 'clear')
            _, tela = display.renderizar_painel(_jogo['eco'], _jogo['upg'], _jogo['prog'])
            print(tela)
            for m in _jogo['msgs'][:3]:
                print(f"  {m}")
            print("\n  > ", end='', flush=True)
            ultimo_ref = agora

        time.sleep(0.1)

# ---------------------------------------------------------------------------
# Ponto de entrada
# ---------------------------------------------------------------------------
def iniciar():
    _inicializar()

    if os.name == 'nt':
        # Windows: curses não é nativo, usar threading
        _iniciar_threading()
    else:
        # macOS / Linux: tentar curses primeiro
        try:
            import curses
            _iniciar_curses()
            print("Jogo salvo. Até logo!")
        except Exception as erro:
            print(f"[AVISO] curses falhou ({erro}). Usando modo alternativo...")
            _iniciar_threading()

if __name__ == '__main__':
    iniciar()
