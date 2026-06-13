# =============================================================================
# test_display.py — Módulo testador de display.py
# INF1040 - 2026.1 - Grupo 2
# =============================================================================

import display
import economia
import upgrades
import progresso

_resultados = []

def _registrar(nome, passou, esperado=None, obtido=None):
    status = "PASSOU" if passou else "FALHOU"
    _resultados.append((nome, status, esperado, obtido))

def _estados():
    _, e = economia.inicializar_estado()
    _, u = upgrades.inicializar_upgrades()
    _, p = progresso.inicializar_progresso()
    return e, u, p

def _eco_com_pontos(valor):
    _, e = economia.inicializar_estado()
    _, e = economia.adicionar_pontos(e, valor)
    return e

# ---------------------------------------------------------------------------
# CT01-CT08 — formatar_numero
# ---------------------------------------------------------------------------
def test_ct01():
    try:
        codigo, s = display.formatar_numero(0)
        ok = (codigo == 0 and s == "0")
        _registrar("CT01 formatar_numero() — 0 → '0'", ok, "(0, '0')", (codigo, s))
    except Exception as ex:
        _registrar("CT01 formatar_numero() — 0", False, "(0, '0')", str(ex))

def test_ct02():
    try:
        codigo, s = display.formatar_numero(750)
        ok = (codigo == 0 and "K" not in s and "M" not in s)
        _registrar("CT02 formatar_numero() — 750 → sem sufixo", ok, "(0, '750')", (codigo, s))
    except Exception as ex:
        _registrar("CT02 formatar_numero() — 750", False, "(0, str)", str(ex))

def test_ct03():
    try:
        codigo, s = display.formatar_numero(1500)
        ok = (codigo == 0 and "K" in s)
        _registrar("CT03 formatar_numero() — 1500 → '1.5K'", ok, "(0, '1.5K')", (codigo, s))
    except Exception as ex:
        _registrar("CT03 formatar_numero() — 1500", False, "(0, '1.5K')", str(ex))

def test_ct04():
    try:
        codigo, s = display.formatar_numero(2_000_000)
        ok = (codigo == 0 and "M" in s)
        _registrar("CT04 formatar_numero() — 2e6 → '2.0M'", ok, "(0, '2.0M')", (codigo, s))
    except Exception as ex:
        _registrar("CT04 formatar_numero() — 2e6", False, "(0, '2.0M')", str(ex))

def test_ct05():
    try:
        codigo, s = display.formatar_numero(1_000_000_000)
        ok = (codigo == 0 and "B" in s)
        _registrar("CT05 formatar_numero() — 1e9 → '1.0B'", ok, "(0, '1.0B')", (codigo, s))
    except Exception as ex:
        _registrar("CT05 formatar_numero() — 1e9", False, "(0, '1.0B')", str(ex))

def test_ct06():
    try:
        codigo, s = display.formatar_numero(1e12)
        ok = (codigo == 0 and "T" in s)
        _registrar("CT06 formatar_numero() — 1e12 → '1.0T'", ok, "(0, '1.0T')", (codigo, s))
    except Exception as ex:
        _registrar("CT06 formatar_numero() — 1e12", False, "(0, '1.0T')", str(ex))

def test_ct07():
    try:
        codigo, s = display.formatar_numero(1e50)
        ok = (codigo == 0 and s is not None and len(s) > 0)
        _registrar("CT07 formatar_numero() — 1e50 → str válida", ok,
                   "(0, str não vazia)", (codigo, s))
    except Exception as ex:
        _registrar("CT07 formatar_numero() — 1e50", False, "(0, str)", str(ex))

def test_ct08():
    try:
        codigo, s = display.formatar_numero(-1.0)
        ok = (codigo == -1 and s is None)
        _registrar("CT08 formatar_numero() — negativo → erro", ok,
                   "(-1, None)", (codigo, s))
    except Exception as ex:
        _registrar("CT08 formatar_numero() — negativo", False, "(-1, None)", str(ex))

# ---------------------------------------------------------------------------
# CT09-CT11 — renderizar_pontos
# ---------------------------------------------------------------------------
def test_ct09():
    try:
        e = _eco_com_pontos(12345.0)
        codigo, s = display.renderizar_pontos(e)
        ok = (codigo == 0 and isinstance(s, str) and len(s) > 0)
        _registrar("CT09 renderizar_pontos() — pontos > 0", ok,
                   "(0, str com pontos)", (codigo, s[:40] if s else None))
    except Exception as ex:
        _registrar("CT09 renderizar_pontos() — pontos > 0", False, "(0, str)", str(ex))

def test_ct10():
    try:
        _, e = economia.inicializar_estado()
        _, e = economia.aplicar_multiplicador_revolucao(e, 4)
        codigo, s = display.renderizar_pontos(e)
        ok = (codigo == 0 and isinstance(s, str))
        _registrar("CT10 renderizar_pontos() — multiplicador ativo", ok,
                   "(0, str c/ mult)", (codigo, bool(s)))
    except Exception as ex:
        _registrar("CT10 renderizar_pontos() — mult ativo", False, "(0, str)", str(ex))

def test_ct11():
    try:
        _, e = economia.inicializar_estado()
        _, e = economia.aplicar_expoente_ascensao(e, 2)
        codigo, s = display.renderizar_pontos(e)
        ok = (codigo == 0 and isinstance(s, str))
        _registrar("CT11 renderizar_pontos() — expoente ativo", ok,
                   "(0, str c/ exp)", (codigo, bool(s)))
    except Exception as ex:
        _registrar("CT11 renderizar_pontos() — exp ativo", False, "(0, str)", str(ex))

# ---------------------------------------------------------------------------
# CT12-CT14 — renderizar_geradores
# ---------------------------------------------------------------------------
def test_ct12():
    try:
        _, e = economia.inicializar_estado()
        _, u = upgrades.inicializar_upgrades()
        codigo, s = display.renderizar_geradores(e, u)
        ok = (codigo == 0 and isinstance(s, str) and len(s) > 0)
        _registrar("CT12 renderizar_geradores() — nenhum comprado", ok,
                   "(0, str com qtd 0)", (codigo, bool(s)))
    except Exception as ex:
        _registrar("CT12 renderizar_geradores() — nenhum", False, "(0, str)", str(ex))

def test_ct13():
    try:
        _, e = economia.inicializar_estado()
        _, e = economia.adicionar_gerador(e, 'mineradora_vermelha', 3)
        _, u = upgrades.inicializar_upgrades()
        codigo, s = display.renderizar_geradores(e, u)
        ok = (codigo == 0 and "3" in s)
        _registrar("CT13 renderizar_geradores() — mostra qtd=3", ok,
                   "(0, str com '3')", (codigo, "3" in s if s else False))
    except Exception as ex:
        _registrar("CT13 renderizar_geradores() — qtd", False, "(0, str)", str(ex))

def test_ct14():
    try:
        _, e = economia.inicializar_estado()
        _, u = upgrades.inicializar_upgrades()
        codigo, s = display.renderizar_geradores(e, u)
        ok = (codigo == 0 and ("bloqueado" in s.lower() or "locked" in s.lower() or "🔒" in s))
        _registrar("CT14 renderizar_geradores() — laboratórios bloqueados", ok,
                   "(0, str indica bloqueado)", (codigo, bool(s)))
    except Exception as ex:
        _registrar("CT14 renderizar_geradores() — bloqueado", False, "(0, str)", str(ex))

# ---------------------------------------------------------------------------
# CT15-CT17 — renderizar_upgrades
# ---------------------------------------------------------------------------
def test_ct15():
    try:
        _, u = upgrades.inicializar_upgrades()
        e = _eco_com_pontos(1e6)
        codigo, s = display.renderizar_upgrades(u, e)
        ok = (codigo == 0 and isinstance(s, str) and len(s) > 0)
        _registrar("CT15 renderizar_upgrades() — disponível e acessível", ok,
                   "(0, str com disponível)", (codigo, bool(s)))
    except Exception as ex:
        _registrar("CT15 renderizar_upgrades() — disponível", False, "(0, str)", str(ex))

def test_ct16():
    try:
        _, u = upgrades.inicializar_upgrades()
        e = _eco_com_pontos(1e6)
        _, u, _ = upgrades.comprar_upgrade(u, e, 'upgrade_mineradora_vermelha_x2')
        codigo, s = display.renderizar_upgrades(u, e)
        ok = (codigo == 0 and isinstance(s, str))
        _registrar("CT16 renderizar_upgrades() — upgrade comprado indicado", ok,
                   "(0, str c/ comprado)", (codigo, bool(s)))
    except Exception as ex:
        _registrar("CT16 renderizar_upgrades() — comprado", False, "(0, str)", str(ex))

def test_ct17():
    try:
        _, u = upgrades.inicializar_upgrades()
        _, e = economia.inicializar_estado()   # pontos = 0
        codigo, s = display.renderizar_upgrades(u, e)
        ok = (codigo == 0 and isinstance(s, str) and len(s) > 0)
        _registrar("CT17 renderizar_upgrades() — inacessível indicado", ok,
                   "(0, str c/ inacessível)", (codigo, bool(s)))
    except Exception as ex:
        _registrar("CT17 renderizar_upgrades() — inacessível", False, "(0, str)", str(ex))

# ---------------------------------------------------------------------------
# CT18-CT20 — renderizar_progresso
# ---------------------------------------------------------------------------
def test_ct18():
    try:
        _, p = progresso.inicializar_progresso()
        codigo, s = display.renderizar_progresso(p)
        ok = (codigo == 0 and isinstance(s, str) and len(s) > 0)
        _registrar("CT18 renderizar_progresso() — sem marcos", ok,
                   "(0, str sem marcos)", (codigo, bool(s)))
    except Exception as ex:
        _registrar("CT18 renderizar_progresso() — sem marcos", False, "(0, str)", str(ex))

def test_ct19():
    try:
        e = _eco_com_pontos(1001.0)
        _, p = progresso.inicializar_progresso()
        _, p, _ = progresso.verificar_progresso(e, p)
        codigo, s = display.renderizar_progresso(p)
        ok = (codigo == 0 and isinstance(s, str) and len(s) > 0)
        _registrar("CT19 renderizar_progresso() — com marco atingido", ok,
                   "(0, str c/ marco)", (codigo, bool(s)))
    except Exception as ex:
        _registrar("CT19 renderizar_progresso() — com marco", False, "(0, str)", str(ex))

def test_ct20():
    try:
        _, p = progresso.inicializar_progresso()
        if isinstance(p, dict):
            p['cristais_revolucao'] = 3
            p['fragmentos_ascensao'] = 1
        codigo, s = display.renderizar_progresso(p)
        ok = (codigo == 0 and isinstance(s, str))
        _registrar("CT20 renderizar_progresso() — cristais e fragmentos", ok,
                   "(0, str c/ contadores)", (codigo, bool(s)))
    except Exception as ex:
        _registrar("CT20 renderizar_progresso() — cristais frag", False, "(0, str)", str(ex))

# ---------------------------------------------------------------------------
# CT21-CT24 — renderizar_resets
# ---------------------------------------------------------------------------
def test_ct21():
    try:
        from constantes import LIMIAR_REVOLUCAO_BASE
        e = _eco_com_pontos(LIMIAR_REVOLUCAO_BASE + 1)
        _, p = progresso.inicializar_progresso()
        codigo, s = display.renderizar_resets(e, p)
        ok = (codigo == 0 and isinstance(s, str) and len(s) > 0)
        _registrar("CT21 renderizar_resets() — elegível para revolução", ok,
                   "(0, str c/ ganho estimado)", (codigo, bool(s)))
    except Exception as ex:
        _registrar("CT21 renderizar_resets() — elegível revol", False, "(0, str)", str(ex))

def test_ct22():
    try:
        _, e = economia.inicializar_estado()
        _, p = progresso.inicializar_progresso()
        codigo, s = display.renderizar_resets(e, p)
        ok = (codigo == 0 and isinstance(s, str) and len(s) > 0)
        _registrar("CT22 renderizar_resets() — não elegível para revolução", ok,
                   "(0, str c/ pts faltantes)", (codigo, bool(s)))
    except Exception as ex:
        _registrar("CT22 renderizar_resets() — não elegível revol", False, "(0, str)", str(ex))

def test_ct23():
    try:
        from constantes import REVOLUCOES_P_ASCENSAO
        _, e = economia.inicializar_estado()
        _, p = progresso.inicializar_progresso()
        if isinstance(p, dict):
            p['num_revolucoes'] = REVOLUCOES_P_ASCENSAO
        codigo, s = display.renderizar_resets(e, p)
        ok = (codigo == 0 and isinstance(s, str))
        _registrar("CT23 renderizar_resets() — elegível para ascensão", ok,
                   "(0, str c/ ascensão)", (codigo, bool(s)))
    except Exception as ex:
        _registrar("CT23 renderizar_resets() — elegível ascensão", False, "(0, str)", str(ex))

def test_ct24():
    try:
        _, e = economia.inicializar_estado()
        _, p = progresso.inicializar_progresso()
        codigo, s = display.renderizar_resets(e, p)
        ok = (codigo == 0 and isinstance(s, str))
        _registrar("CT24 renderizar_resets() — não elegível ascensão", ok,
                   "(0, str c/ revol faltantes)", (codigo, bool(s)))
    except Exception as ex:
        _registrar("CT24 renderizar_resets() — não elegível ascens", False, "(0, str)", str(ex))

# ---------------------------------------------------------------------------
# CT25 — montar_menu_comando
# ---------------------------------------------------------------------------
def test_ct25():
    try:
        codigo, s = display.montar_menu_comando()
        ok = (codigo == 0 and isinstance(s, str) and len(s) > 10)
        _registrar("CT25 montar_menu_comando() — lista de comandos", ok,
                   "(0, str com comandos)", (codigo, s[:50] if s else None))
    except Exception as ex:
        _registrar("CT25 montar_menu_comando()", False, "(0, str)", str(ex))

# ---------------------------------------------------------------------------
# CT26-CT27 — renderizar_painel
# ---------------------------------------------------------------------------
def test_ct26():
    try:
        e, u, p = _estados()
        codigo, s = display.renderizar_painel(e, u, p)
        ok = (codigo == 0 and isinstance(s, str) and len(s) > 50)
        _registrar("CT26 renderizar_painel() — estado completo válido", ok,
                   "(0, str não vazia)", (codigo, len(s) if s else 0))
    except Exception as ex:
        _registrar("CT26 renderizar_painel() — estado completo", False, "(0, str)", str(ex))

def test_ct27():
    """Verifica que renderizar_painel não produz side effects (sem print)."""
    import io, sys
    try:
        e, u, p = _estados()
        captura = io.StringIO()
        sys.stdout = captura
        codigo, s = display.renderizar_painel(e, u, p)
        sys.stdout = sys.__stdout__
        saida_capturada = captura.getvalue()
        ok = (codigo == 0 and saida_capturada == "")
        _registrar("CT27 renderizar_painel() — sem side effects (sem print)", ok,
                   "(0, str, stdout vazio)", (codigo, repr(saida_capturada)))
    except Exception as ex:
        sys.stdout = sys.__stdout__
        _registrar("CT27 renderizar_painel() — sem side effects", False,
                   "(0, str, stdout='')", str(ex))

# ---------------------------------------------------------------------------
# Relatório
# ---------------------------------------------------------------------------
def _relatorio():
    print("\n" + "=" * 60)
    print("RELATÓRIO — test_display.py")
    print("=" * 60)
    passou = sum(1 for _, s, _, _ in _resultados if s == "PASSOU")
    falhou = sum(1 for _, s, _, _ in _resultados if s == "FALHOU")
    for nome, status, esp, obt in _resultados:
        print(f"  [{status}] {nome}")
        if status != "PASSOU":
            print(f"           Esperado : {esp}")
            print(f"           Obtido   : {obt}")
    print("-" * 60)
    print(f"  Total: {len(_resultados)}  |  Passou: {passou}  |  Falhou: {falhou}")
    print("=" * 60)
    return falhou == 0

if __name__ == '__main__':
    for t in [test_ct01, test_ct02, test_ct03, test_ct04,
              test_ct05, test_ct06, test_ct07, test_ct08,
              test_ct09, test_ct10, test_ct11, test_ct12,
              test_ct13, test_ct14, test_ct15, test_ct16,
              test_ct17, test_ct18, test_ct19, test_ct20,
              test_ct21, test_ct22, test_ct23, test_ct24,
              test_ct25, test_ct26, test_ct27]:
        t()
    ok = _relatorio()
    exit(0 if ok else 1)
