# =============================================================================
# test_progresso.py — Módulo testador de progresso.py
# INF1040 - 2026.1 - Grupo 2
# =============================================================================

import progresso
import economia
from constantes import LIMIAR_REVOLUCAO_BASE, REVOLUCOES_P_ASCENSAO, PONTO_OMEGA

_resultados = []

def _registrar(nome, passou, esperado=None, obtido=None):
    status = "PASSOU" if passou else "FALHOU"
    _resultados.append((nome, status, esperado, obtido))

def _eco_zerado():
    _, e = economia.inicializar_estado()
    return e

def _eco_com_pontos(valor):
    _, e = economia.inicializar_estado()
    _, e = economia.adicionar_pontos(e, valor)
    _, e = economia.aplicar_geracao(e, 0)   # garante pontos_run_max atualizado
    return e

def _prog_zerado():
    _, p = progresso.inicializar_progresso()
    return p

# ---------------------------------------------------------------------------
# CT01 — inicializar_progresso
# ---------------------------------------------------------------------------
def test_ct01():
    try:
        codigo, estado = progresso.inicializar_progresso()
        _, atingidos = progresso.obter_marcos_atingidos(estado)
        _, proximos  = progresso.obter_proximos_marcos(estado)
        _, nivel     = progresso.calcular_nivel(_eco_zerado())
        ok = (codigo == 0
              and atingidos == []
              and len(proximos) > 0
              and nivel == 1)
        _registrar("CT01 inicializar_progresso() — estado inicial correto", ok,
                   "(0, dict nivel=1 sem marcos)", (codigo, atingidos, len(proximos)))
    except Exception as ex:
        _registrar("CT01 inicializar_progresso()", False, "(0, dict)", str(ex))

# ---------------------------------------------------------------------------
# CT02-CT04 — calcular_nivel
# ---------------------------------------------------------------------------
def test_ct02():
    try:
        e = _eco_zerado()
        codigo, nivel = progresso.calcular_nivel(e)
        ok = (codigo == 0 and nivel == 1)
        _registrar("CT02 calcular_nivel() — recursos zerados → nível 1", ok,
                   "(0, 1)", (codigo, nivel))
    except Exception as ex:
        _registrar("CT02 calcular_nivel() — zerado", False, "(0, 1)", str(ex))

def test_ct03():
    try:
        e = _eco_com_pontos(1001.0)   # limiar nível 2 = 1e3
        codigo, nivel = progresso.calcular_nivel(e)
        ok = (codigo == 0 and nivel >= 2)
        _registrar("CT03 calcular_nivel() — acima do limiar nível 2", ok,
                   "(0, >=2)", (codigo, nivel))
    except Exception as ex:
        _registrar("CT03 calcular_nivel() — nível 2", False, "(0, >=2)", str(ex))

def test_ct04():
    try:
        e = _eco_com_pontos(1e21)   # acima do limiar máximo
        codigo, nivel = progresso.calcular_nivel(e)
        from constantes import NIVEL_MAXIMO
        ok = (codigo == 0 and nivel == NIVEL_MAXIMO)
        _registrar("CT04 calcular_nivel() — acima do limiar máximo", ok,
                   f"(0, {NIVEL_MAXIMO})", (codigo, nivel))
    except Exception as ex:
        _registrar("CT04 calcular_nivel() — máximo", False, "(0, NIVEL_MAXIMO)", str(ex))

# ---------------------------------------------------------------------------
# CT05-CT08 — verificar_progresso
# ---------------------------------------------------------------------------
def test_ct05():
    try:
        e = _eco_zerado()
        p = _prog_zerado()
        codigo, p_novo, novos = progresso.verificar_progresso(e, p)
        ok = (codigo == 0 and novos == [])
        _registrar("CT05 verificar_progresso() — nenhum marco atingido", ok,
                   "(0, dict, [])", (codigo, novos))
    except Exception as ex:
        _registrar("CT05 verificar_progresso() — nenhum marco", False, "(0, dict, [])", str(ex))

def test_ct06():
    try:
        e = _eco_com_pontos(1001.0)   # atinge marco_1k
        p = _prog_zerado()
        codigo, p_novo, novos = progresso.verificar_progresso(e, p)
        ok = (codigo == 0 and len(novos) >= 1 and 'marco_1k' in novos)
        _registrar("CT06 verificar_progresso() — marco_1k atingido", ok,
                   "(0, dict, ['marco_1k'])", (codigo, novos))
    except Exception as ex:
        _registrar("CT06 verificar_progresso() — marco_1k", False, "(0, dict, [marco])", str(ex))

def test_ct07():
    try:
        e = _eco_com_pontos(1001.0)
        p = _prog_zerado()
        _, p, _ = progresso.verificar_progresso(e, p)
        codigo, p2, novos = progresso.verificar_progresso(e, p)
        ok = (codigo == 0 and 'marco_1k' not in novos)
        _registrar("CT07 verificar_progresso() — marco já registrado não duplica", ok,
                   "(0, dict, [] sem duplicata)", (codigo, novos))
    except Exception as ex:
        _registrar("CT07 verificar_progresso() — sem duplicata", False, "(0, dict, [])", str(ex))

def test_ct08():
    try:
        e = _eco_com_pontos(1.1e4)   # atinge marco_1k e marco_10k
        p = _prog_zerado()
        codigo, p_novo, novos = progresso.verificar_progresso(e, p)
        ok = (codigo == 0
              and 'marco_1k'  in novos
              and 'marco_10k' in novos)
        _registrar("CT08 verificar_progresso() — dois marcos simultâneos", ok,
                   "(0, dict, [marco_1k, marco_10k])", (codigo, novos))
    except Exception as ex:
        _registrar("CT08 verificar_progresso() — dois marcos", False, "(0, dict, [m1,m2])", str(ex))

# ---------------------------------------------------------------------------
# CT09-CT12 — obter_marcos_atingidos / obter_proximos_marcos
# ---------------------------------------------------------------------------
def test_ct09():
    try:
        p = _prog_zerado()
        codigo, lista = progresso.obter_marcos_atingidos(p)
        ok = (codigo == 0 and lista == [])
        _registrar("CT09 obter_marcos_atingidos() — estado inicial", ok,
                   "(0, [])", (codigo, lista))
    except Exception as ex:
        _registrar("CT09 obter_marcos_atingidos() — inicial", False, "(0, [])", str(ex))

def test_ct10():
    try:
        e = _eco_com_pontos(1001.0)
        p = _prog_zerado()
        _, p, _ = progresso.verificar_progresso(e, p)
        codigo, lista = progresso.obter_marcos_atingidos(p)
        ok = (codigo == 0 and 'marco_1k' in lista)
        _registrar("CT10 obter_marcos_atingidos() — após marco registrado", ok,
                   "(0, ['marco_1k'])", (codigo, lista))
    except Exception as ex:
        _registrar("CT10 obter_marcos_atingidos() — após marco", False, "(0, list)", str(ex))

def test_ct11():
    try:
        p = _prog_zerado()
        codigo, lista = progresso.obter_proximos_marcos(p)
        ok = (codigo == 0 and len(lista) > 0)
        _registrar("CT11 obter_proximos_marcos() — estado inicial", ok,
                   "(0, list>0)", (codigo, len(lista)))
    except Exception as ex:
        _registrar("CT11 obter_proximos_marcos() — inicial", False, "(0, list)", str(ex))

def test_ct12():
    try:
        # Registrar todos marcos de pontos manualmente
        e = _eco_com_pontos(PONTO_OMEGA + 1)
        p = _prog_zerado()
        _, p, _ = progresso.verificar_progresso(e, p)
        # Registrar marcos de eventos manualmente forçando
        # (eles precisam de evento especial — verificar se lista reduz)
        _, proximos = progresso.obter_proximos_marcos(p)
        _, atingidos = progresso.obter_marcos_atingidos(p)
        ok = (len(proximos) < 13)  # pelo menos alguns marcos foram removidos
        _registrar("CT12 obter_proximos_marcos() — após atingir marcos", ok,
                   "(0, list menor que inicial)", (len(atingidos), len(proximos)))
    except Exception as ex:
        _registrar("CT12 obter_proximos_marcos() — após marcos", False, "(0, list)", str(ex))

# ---------------------------------------------------------------------------
# CT13-CT19 — pode_revolucao / executar_revolucao
# ---------------------------------------------------------------------------
def test_ct13():
    try:
        e = _eco_com_pontos(LIMIAR_REVOLUCAO_BASE + 1)
        p = _prog_zerado()
        codigo, pode = progresso.pode_revolucao(e, p)
        ok = (codigo == 0 and pode is True)
        _registrar("CT13 pode_revolucao() — elegível", ok, "(0, True)", (codigo, pode))
    except Exception as ex:
        _registrar("CT13 pode_revolucao() — elegível", False, "(0, True)", str(ex))

def test_ct14():
    try:
        e = _eco_zerado()
        p = _prog_zerado()
        codigo, pode = progresso.pode_revolucao(e, p)
        ok = (codigo == 0 and pode is False)
        _registrar("CT14 pode_revolucao() — não elegível", ok, "(0, False)", (codigo, pode))
    except Exception as ex:
        _registrar("CT14 pode_revolucao() — não elegível", False, "(0, False)", str(ex))

def test_ct15():
    try:
        e = _eco_com_pontos(LIMIAR_REVOLUCAO_BASE + 1)
        p = _prog_zerado()
        codigo, e_novo, p_novo = progresso.executar_revolucao(e, p)
        _, pontos = economia.obter_pontos(e_novo)
        _, cristais = (0, p_novo.get('cristais_revolucao', -1)) if isinstance(p_novo, dict) else (0, -1)
        ok = (codigo == 0 and pontos == 0.0 and cristais >= 1)
        _registrar("CT15 executar_revolucao() — elegível", ok,
                   "(0, eco_reset, prog_cristais)", (codigo, pontos, cristais))
    except Exception as ex:
        _registrar("CT15 executar_revolucao() — elegível", False, "(0, eco, prog)", str(ex))

def test_ct16():
    try:
        e = _eco_zerado()
        p = _prog_zerado()
        codigo, e_o, p_o = progresso.executar_revolucao(e, p)
        ok = (codigo == -2)
        _registrar("CT16 executar_revolucao() — não elegível", ok,
                   "(-2, orig, orig)", (codigo,))
    except Exception as ex:
        _registrar("CT16 executar_revolucao() — não elegível", False, "(-2, orig, orig)", str(ex))

def test_ct17():
    try:
        e = _eco_com_pontos(4 * LIMIAR_REVOLUCAO_BASE)
        p = _prog_zerado()
        _, e_novo, p_novo = progresso.executar_revolucao(e, p)
        cristais = p_novo.get('cristais_revolucao', 0) if isinstance(p_novo, dict) else 0
        ok = (cristais >= 2)   # sqrt(4e6/1e6) = 2
        _registrar("CT17 executar_revolucao() — cristais corretos (sqrt formula)", ok,
                   "cristais>=2", (cristais,))
    except Exception as ex:
        _registrar("CT17 executar_revolucao() — cristais formula", False, "cristais>=2", str(ex))

def test_ct18():
    try:
        e = _eco_com_pontos(LIMIAR_REVOLUCAO_BASE + 1)
        p = _prog_zerado()
        _, e_novo, p_novo = progresso.executar_revolucao(e, p)
        lab_desbloq = p_novo.get('laboratorios_desbloqueados', False) if isinstance(p_novo, dict) else False
        ok = (lab_desbloq is True)
        _registrar("CT18 executar_revolucao() — laboratórios desbloqueados na 1ª", ok,
                   "laboratorios=True", (lab_desbloq,))
    except Exception as ex:
        _registrar("CT18 executar_revolucao() — lab desbl", False, "laboratorios=True", str(ex))

def test_ct19():
    try:
        e = _eco_com_pontos(LIMIAR_REVOLUCAO_BASE + 1)
        p = _prog_zerado()
        _, e, p = progresso.executar_revolucao(e, p)
        num_rev = p.get('num_revolucoes', 0) if isinstance(p, dict) else 0
        ok = (num_rev == 1)
        _registrar("CT19 executar_revolucao() — num_revolucoes incrementado", ok,
                   "num_revol=1", (num_rev,))
    except Exception as ex:
        _registrar("CT19 executar_revolucao() — num_revol", False, "num_revol=1", str(ex))

# ---------------------------------------------------------------------------
# CT20-CT25 — pode_ascensao / executar_ascensao
# ---------------------------------------------------------------------------
def test_ct20():
    try:
        p = _prog_zerado()
        if isinstance(p, dict):
            p['num_revolucoes'] = REVOLUCOES_P_ASCENSAO
        codigo, pode = progresso.pode_ascensao(p)
        ok = (codigo == 0 and pode is True)
        _registrar("CT20 pode_ascensao() — elegível (10 revoluções)", ok,
                   "(0, True)", (codigo, pode))
    except Exception as ex:
        _registrar("CT20 pode_ascensao() — elegível", False, "(0, True)", str(ex))

def test_ct21():
    try:
        p = _prog_zerado()
        codigo, pode = progresso.pode_ascensao(p)
        ok = (codigo == 0 and pode is False)
        _registrar("CT21 pode_ascensao() — não elegível (0 revoluções)", ok,
                   "(0, False)", (codigo, pode))
    except Exception as ex:
        _registrar("CT21 pode_ascensao() — não elegível", False, "(0, False)", str(ex))

def test_ct22():
    try:
        e = _eco_zerado()
        p = _prog_zerado()
        if isinstance(p, dict):
            p['num_revolucoes'] = REVOLUCOES_P_ASCENSAO
            p['cristais_revolucao'] = 5
        codigo, e_novo, p_novo = progresso.executar_ascensao(e, p)
        frag = p_novo.get('fragmentos_ascensao', 0) if isinstance(p_novo, dict) else 0
        ok = (codigo == 0 and frag >= 1)
        _registrar("CT22 executar_ascensao() — elegível", ok,
                   "(0, eco_reset, prog_frag)", (codigo, frag))
    except Exception as ex:
        _registrar("CT22 executar_ascensao() — elegível", False, "(0, eco, prog)", str(ex))

def test_ct23():
    try:
        e = _eco_zerado()
        p = _prog_zerado()
        codigo, e_o, p_o = progresso.executar_ascensao(e, p)
        ok = (codigo == -2)
        _registrar("CT23 executar_ascensao() — não elegível", ok,
                   "(-2, orig, orig)", (codigo,))
    except Exception as ex:
        _registrar("CT23 executar_ascensao() — não elegível", False, "(-2, orig, orig)", str(ex))

def test_ct24():
    try:
        e = _eco_zerado()
        p = _prog_zerado()
        if isinstance(p, dict):
            p['num_revolucoes']   = REVOLUCOES_P_ASCENSAO
            p['cristais_revolucao'] = 5
        _, e_novo, p_novo = progresso.executar_ascensao(e, p)
        crist = p_novo.get('cristais_revolucao', -1) if isinstance(p_novo, dict) else -1
        revol = p_novo.get('num_revolucoes', -1)     if isinstance(p_novo, dict) else -1
        ok = (crist == 0 and revol == 0)
        _registrar("CT24 executar_ascensao() — cristais e revoluções zerados", ok,
                   "cristais=0 revol=0", (crist, revol))
    except Exception as ex:
        _registrar("CT24 executar_ascensao() — reset cristais/revol", False, "c=0 r=0", str(ex))

def test_ct25():
    try:
        e = _eco_zerado()
        p = _prog_zerado()
        if isinstance(p, dict):
            p['num_revolucoes'] = REVOLUCOES_P_ASCENSAO
        _, e_novo, p_novo = progresso.executar_ascensao(e, p)
        frag = p_novo.get('fragmentos_ascensao', 0) if isinstance(p_novo, dict) else 0
        _, exp = economia.obter_expoente_ascensao(e_novo)
        ok = (frag == 1 and abs(exp - 1.15) < 1e-9)
        _registrar("CT25 executar_ascensao() — frag+=1, expoente=1.15", ok,
                   "frag=1 exp=1.15", (frag, exp))
    except Exception as ex:
        _registrar("CT25 executar_ascensao() — frag e exp", False, "frag=1 exp=1.15", str(ex))

# ---------------------------------------------------------------------------
# CT26-CT28 — verificar_vitoria
# ---------------------------------------------------------------------------
def test_ct26():
    try:
        e = _eco_com_pontos(PONTO_OMEGA + 1)
        p = _prog_zerado()
        codigo, p_novo, vitoria = progresso.verificar_vitoria(e, p)
        ok = (codigo == 0 and vitoria is True)
        _registrar("CT26 verificar_vitoria() — pontos >= PONTO_OMEGA", ok,
                   "(0, prog, True)", (codigo, vitoria))
    except Exception as ex:
        _registrar("CT26 verificar_vitoria() — vitorioso", False, "(0, prog, True)", str(ex))

def test_ct27():
    try:
        e = _eco_zerado()
        p = _prog_zerado()
        codigo, p_novo, vitoria = progresso.verificar_vitoria(e, p)
        ok = (codigo == 0 and vitoria is False)
        _registrar("CT27 verificar_vitoria() — pontos < PONTO_OMEGA", ok,
                   "(0, prog, False)", (codigo, vitoria))
    except Exception as ex:
        _registrar("CT27 verificar_vitoria() — não vitorioso", False, "(0, prog, False)", str(ex))

def test_ct28():
    try:
        e = _eco_com_pontos(PONTO_OMEGA + 1)
        p = _prog_zerado()
        _, p, _ = progresso.verificar_vitoria(e, p)
        codigo, p2, vitoria = progresso.verificar_vitoria(e, p)
        vitoria_flag = p2.get('vitoria', False) if isinstance(p2, dict) else False
        ok = (codigo == 0 and vitoria is True and vitoria_flag is True)
        _registrar("CT28 verificar_vitoria() — não re-aciona se já registrado", ok,
                   "(0, prog, True) sem re-trigger", (codigo, vitoria))
    except Exception as ex:
        _registrar("CT28 verificar_vitoria() — sem re-trigger", False, "(0, prog, True)", str(ex))

# ---------------------------------------------------------------------------
# Relatório
# ---------------------------------------------------------------------------
def _relatorio():
    print("\n" + "=" * 60)
    print("RELATÓRIO — test_progresso.py")
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
              test_ct25, test_ct26, test_ct27, test_ct28]:
        t()
    ok = _relatorio()
    exit(0 if ok else 1)
