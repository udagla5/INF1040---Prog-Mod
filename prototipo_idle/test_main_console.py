# =============================================================================
# test_main_console.py — Módulo testador de main_console.py (processar_comando)
# INF1040 - 2026.1 - Grupo 2
#
# REGRAS:
#   - Testa APENAS processar_comando (função pública reutilizável)
#   - Cobre todos os comandos: comprar, listar, status, revolucao, ascensao,
#     novo jogo e comando desconhecido
#   - Gera relatório final com executados / aprovados / reprovados
#   - Exceções são capturadas e reportadas sem encerrar o testador
# =============================================================================

import economia
import upgrades
import progresso
from main_console import processar_comando

_resultados = []

def _registrar(nome, passou, esperado=None, obtido=None):
    status = "PASSOU" if passou else "FALHOU"
    _resultados.append((nome, status, esperado, obtido))

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _estados_iniciais():
    _, eco  = economia.inicializar_estado()
    _, upg  = upgrades.inicializar_upgrades()
    _, prog = progresso.inicializar_progresso()
    _, eco  = economia.adicionar_gerador(eco, 'mineradora_vermelha')
    _, eco  = economia.adicionar_gerador(eco, 'mineradora_vermelha')
    return eco, upg, prog

def _estados_com_pontos(valor):
    eco, upg, prog = _estados_iniciais()
    _, eco = economia.adicionar_pontos(eco, valor)
    return eco, upg, prog

# ---------------------------------------------------------------------------
# CT01 — comando vazio retorna código 0 sem alterar estados
# ---------------------------------------------------------------------------
def test_ct01():
    try:
        eco, upg, prog = _estados_iniciais()
        cod, eco2, upg2, prog2, msg = processar_comando('', eco, upg, prog)
        ok = (cod == 0 and eco2 is eco and upg2 is upg and prog2 is prog and msg == '')
        _registrar("CT01 processar_comando('') — sem alteração, cod=0", ok,
                   "(0, eco, upg, prog, '')", (cod, msg))
    except Exception as e:
        _registrar("CT01 processar_comando('') — sem alteração, cod=0", False,
                   "(0, eco, upg, prog, '')", str(e))

# ---------------------------------------------------------------------------
# CT02 — comprar gerador válido com saldo suficiente
# ---------------------------------------------------------------------------
def test_ct02():
    try:
        eco, upg, prog = _estados_com_pontos(1e9)
        cod, eco2, _, _, msg = processar_comando(
            'comprar gerador mineradora_laranja', eco, upg, prog)
        _, qtd = economia.obter_quantidade_gerador(eco2, 'mineradora_laranja')
        ok = (cod == 0 and qtd == 1 and '[OK]' in msg)
        _registrar("CT02 comprar gerador — válido, saldo suficiente → cod=0", ok,
                   "(0, eco com qtd=1, '[OK]')", (cod, qtd, msg[:40]))
    except Exception as e:
        _registrar("CT02 comprar gerador — válido, saldo suficiente → cod=0", False,
                   "(0, ...)", str(e))

# ---------------------------------------------------------------------------
# CT03 — comprar gerador com saldo insuficiente retorna -1
# ---------------------------------------------------------------------------
def test_ct03():
    try:
        eco, upg, prog = _estados_iniciais()   # pontos = 0
        cod, eco2, _, _, msg = processar_comando(
            'comprar gerador mineradora_laranja', eco, upg, prog)
        _, qtd = economia.obter_quantidade_gerador(eco2, 'mineradora_laranja')
        ok = (cod == -1 and qtd == 0 and '[ERRO]' in msg)
        _registrar("CT03 comprar gerador — saldo insuficiente → cod=-1", ok,
                   "(-1, qtd=0, '[ERRO]')", (cod, qtd, msg[:40]))
    except Exception as e:
        _registrar("CT03 comprar gerador — saldo insuficiente → cod=-1", False,
                   "(-1, ...)", str(e))

# ---------------------------------------------------------------------------
# CT04 — comprar gerador com ID inexistente retorna -1
# ---------------------------------------------------------------------------
def test_ct04():
    try:
        eco, upg, prog = _estados_com_pontos(1e12)
        cod, _, _, _, msg = processar_comando(
            'comprar gerador gerador_inexistente', eco, upg, prog)
        ok = (cod == -1 and '[ERRO]' in msg)
        _registrar("CT04 comprar gerador — ID inexistente → cod=-1", ok,
                   "(-1, '[ERRO]')", (cod, msg[:40]))
    except Exception as e:
        _registrar("CT04 comprar gerador — ID inexistente → cod=-1", False,
                   "(-1, ...)", str(e))

# ---------------------------------------------------------------------------
# CT05 — comprar gerador bloqueado (laboratório sem revolução) retorna -1
# ---------------------------------------------------------------------------
def test_ct05():
    try:
        eco, upg, prog = _estados_com_pontos(1e30)
        cod, _, _, _, msg = processar_comando(
            'comprar gerador laboratorio_vermelho', eco, upg, prog)
        ok = (cod == -1 and '[ERRO]' in msg)
        _registrar("CT05 comprar gerador — bloqueado (lab sem revolução) → cod=-1", ok,
                   "(-1, '[ERRO]')", (cod, msg[:50]))
    except Exception as e:
        _registrar("CT05 comprar gerador — bloqueado (lab sem revolução) → cod=-1", False,
                   "(-1, ...)", str(e))

# ---------------------------------------------------------------------------
# CT06 — comprar upgrade válido com saldo suficiente
# ---------------------------------------------------------------------------
def test_ct06():
    try:
        eco, upg, prog = _estados_com_pontos(1e9)
        cod, _, upg2, _, msg = processar_comando(
            'comprar upgrade upgrade_mineradora_vermelha_x2', eco, upg, prog)
        ok = (cod == 0 and
              'upgrade_mineradora_vermelha_x2' in upg2['comprados'] and
              '[OK]' in msg)
        _registrar("CT06 comprar upgrade — válido, saldo suficiente → cod=0", ok,
                   "(0, upgrade comprado, '[OK]')", (cod, msg[:40]))
    except Exception as e:
        _registrar("CT06 comprar upgrade — válido, saldo suficiente → cod=0", False,
                   "(0, ...)", str(e))

# ---------------------------------------------------------------------------
# CT07 — comprar upgrade com saldo insuficiente retorna -1
# ---------------------------------------------------------------------------
def test_ct07():
    try:
        eco, upg, prog = _estados_iniciais()
        cod, _, upg2, _, msg = processar_comando(
            'comprar upgrade upgrade_mineradora_vermelha_x2', eco, upg, prog)
        ok = (cod == -1 and
              'upgrade_mineradora_vermelha_x2' not in upg2['comprados'] and
              '[ERRO]' in msg)
        _registrar("CT07 comprar upgrade — saldo insuficiente → cod=-1", ok,
                   "(-1, não comprado, '[ERRO]')", (cod, msg[:40]))
    except Exception as e:
        _registrar("CT07 comprar upgrade — saldo insuficiente → cod=-1", False,
                   "(-1, ...)", str(e))

# ---------------------------------------------------------------------------
# CT08 — comprar upgrade já comprado retorna -1
# ---------------------------------------------------------------------------
def test_ct08():
    try:
        eco, upg, prog = _estados_com_pontos(1e12)
        _, eco2, upg2, prog2, _ = processar_comando(
            'comprar upgrade upgrade_mineradora_vermelha_x2', eco, upg, prog)
        cod, _, _, _, msg = processar_comando(
            'comprar upgrade upgrade_mineradora_vermelha_x2', eco2, upg2, prog2)
        ok = (cod == -1 and '[ERRO]' in msg)
        _registrar("CT08 comprar upgrade — já comprado → cod=-1", ok,
                   "(-1, '[ERRO]')", (cod, msg[:40]))
    except Exception as e:
        _registrar("CT08 comprar upgrade — já comprado → cod=-1", False,
                   "(-1, ...)", str(e))

# ---------------------------------------------------------------------------
# CT09 — comprar upgrade com ID inexistente retorna -1
# ---------------------------------------------------------------------------
def test_ct09():
    try:
        eco, upg, prog = _estados_com_pontos(1e12)
        cod, _, _, _, msg = processar_comando(
            'comprar upgrade upgrade_inexistente', eco, upg, prog)
        ok = (cod == -1 and '[ERRO]' in msg)
        _registrar("CT09 comprar upgrade — ID inexistente → cod=-1", ok,
                   "(-1, '[ERRO]')", (cod, msg[:40]))
    except Exception as e:
        _registrar("CT09 comprar upgrade — ID inexistente → cod=-1", False,
                   "(-1, ...)", str(e))

# ---------------------------------------------------------------------------
# CT10 — revolucao elegível: estados resetados, multiplicador atualizado
# ---------------------------------------------------------------------------
def test_ct10():
    try:
        eco, upg, prog = _estados_com_pontos(1e8)
        # Simula pontos_run_max alto o suficiente
        eco = {**eco, 'pontos_run_max': 1e8}
        cod, eco2, _, prog2, msg = processar_comando('revolucao', eco, upg, prog)
        _, pontos2 = economia.obter_pontos(eco2)
        ok = (cod == 0 and pontos2 == 0.0 and
              prog2['num_revolucoes'] == 1 and '[REVOLUÇÃO]' in msg)
        _registrar("CT10 revolucao — elegível: run resetada, num_rev=1", ok,
                   "(0, pontos=0, num_rev=1, '[REVOLUÇÃO]')",
                   (cod, pontos2, prog2['num_revolucoes'], msg[:30]))
    except Exception as e:
        _registrar("CT10 revolucao — elegível: run resetada, num_rev=1", False,
                   "(0, ...)", str(e))

# ---------------------------------------------------------------------------
# CT11 — revolucao não elegível retorna -1
# ---------------------------------------------------------------------------
def test_ct11():
    try:
        eco, upg, prog = _estados_iniciais()   # pontos_run_max = 0
        cod, _, _, prog2, msg = processar_comando('revolucao', eco, upg, prog)
        ok = (cod == -1 and prog2['num_revolucoes'] == 0 and '[ERRO]' in msg)
        _registrar("CT11 revolucao — não elegível → cod=-1", ok,
                   "(-1, num_rev=0, '[ERRO]')", (cod, prog2['num_revolucoes'], msg[:40]))
    except Exception as e:
        _registrar("CT11 revolucao — não elegível → cod=-1", False,
                   "(-1, ...)", str(e))

# ---------------------------------------------------------------------------
# CT12 — ascensao elegível: estados resetados, num_ascensoes=1
# ---------------------------------------------------------------------------
def test_ct12():
    try:
        eco, upg, prog = _estados_com_pontos(1e8)
        # Força 10 revoluções diretamente no estado
        prog = {**prog, 'num_revolucoes': 10}
        cod, eco2, _, prog2, msg = processar_comando('ascensao', eco, upg, prog)
        _, pontos2 = economia.obter_pontos(eco2)
        ok = (cod == 0 and pontos2 == 0.0 and
              prog2['num_ascensoes'] == 1 and
              prog2['num_revolucoes'] == 0 and
              '[ASCENSÃO]' in msg)
        _registrar("CT12 ascensao — elegível: run resetada, num_asc=1", ok,
                   "(0, pontos=0, num_asc=1, '[ASCENSÃO]')",
                   (cod, pontos2, prog2['num_ascensoes'], msg[:30]))
    except Exception as e:
        _registrar("CT12 ascensao — elegível: run resetada, num_asc=1", False,
                   "(0, ...)", str(e))

# ---------------------------------------------------------------------------
# CT13 — ascensao não elegível retorna -1
# ---------------------------------------------------------------------------
def test_ct13():
    try:
        eco, upg, prog = _estados_iniciais()   # num_revolucoes = 0
        cod, _, _, prog2, msg = processar_comando('ascensao', eco, upg, prog)
        ok = (cod == -1 and prog2['num_ascensoes'] == 0 and '[ERRO]' in msg)
        _registrar("CT13 ascensao — não elegível → cod=-1", ok,
                   "(-1, num_asc=0, '[ERRO]')", (cod, prog2['num_ascensoes'], msg[:40]))
    except Exception as e:
        _registrar("CT13 ascensao — não elegível → cod=-1", False,
                   "(-1, ...)", str(e))

# ---------------------------------------------------------------------------
# CT14 — listar geradores retorna cod=0 e string não vazia
# ---------------------------------------------------------------------------
def test_ct14():
    try:
        eco, upg, prog = _estados_iniciais()
        cod, _, _, _, msg = processar_comando('listar geradores', eco, upg, prog)
        ok = (cod == 0 and len(msg) > 0 and 'mineradora' in msg.lower())
        _registrar("CT14 listar geradores — retorna cod=0 e texto com geradores", ok,
                   "(0, texto com 'mineradora')", (cod, len(msg)))
    except Exception as e:
        _registrar("CT14 listar geradores — retorna cod=0 e texto com geradores", False,
                   "(0, ...)", str(e))

# ---------------------------------------------------------------------------
# CT15 — listar upgrades retorna cod=0 e string não vazia
# ---------------------------------------------------------------------------
def test_ct15():
    try:
        eco, upg, prog = _estados_iniciais()
        cod, _, _, _, msg = processar_comando('listar upgrades', eco, upg, prog)
        ok = (cod == 0 and len(msg) > 0 and 'upgrade' in msg.lower())
        _registrar("CT15 listar upgrades — retorna cod=0 e texto com upgrades", ok,
                   "(0, texto com 'upgrade')", (cod, len(msg)))
    except Exception as e:
        _registrar("CT15 listar upgrades — retorna cod=0 e texto com upgrades", False,
                   "(0, ...)", str(e))

# ---------------------------------------------------------------------------
# CT16 — status retorna cod=0 e painel completo
# ---------------------------------------------------------------------------
def test_ct16():
    try:
        eco, upg, prog = _estados_iniciais()
        cod, _, _, _, msg = processar_comando('status', eco, upg, prog)
        ok = (cod == 0 and len(msg) > 0 and 'PONTOS' in msg.upper())
        _registrar("CT16 status — retorna cod=0 e painel com 'PONTOS'", ok,
                   "(0, painel completo)", (cod, len(msg)))
    except Exception as e:
        _registrar("CT16 status — retorna cod=0 e painel com 'PONTOS'", False,
                   "(0, ...)", str(e))

# ---------------------------------------------------------------------------
# CT17 — novo jogo: estados zerados, 2 mineradoras iniciais
# ---------------------------------------------------------------------------
def test_ct17():
    try:
        eco, upg, prog = _estados_com_pontos(1e12)
        cod, eco2, upg2, prog2, msg = processar_comando('novo jogo', eco, upg, prog)
        _, pontos2 = economia.obter_pontos(eco2)
        _, qtd_min = economia.obter_quantidade_gerador(eco2, 'mineradora_vermelha')
        ok = (cod == 0 and pontos2 == 0.0 and qtd_min == 2 and
              upg2['comprados'] == [] and '[OK]' in msg)
        _registrar("CT17 novo jogo — estados zerados, 2 mineradoras iniciais", ok,
                   "(0, pontos=0, qtd_min=2, comprados=[], '[OK]')",
                   (cod, pontos2, qtd_min, upg2['comprados'], msg[:30]))
    except Exception as e:
        _registrar("CT17 novo jogo — estados zerados, 2 mineradoras iniciais", False,
                   "(0, ...)", str(e))

# ---------------------------------------------------------------------------
# CT18 — comando desconhecido retorna -1 com mensagem de erro
# ---------------------------------------------------------------------------
def test_ct18():
    try:
        eco, upg, prog = _estados_iniciais()
        cod, eco2, upg2, prog2, msg = processar_comando('xpto comando invalido', eco, upg, prog)
        ok = (cod == -1 and eco2 is eco and upg2 is upg and prog2 is prog and '[ERRO]' in msg)
        _registrar("CT18 comando desconhecido — cod=-1, estados preservados", ok,
                   "(-1, eco/upg/prog inalterados, '[ERRO]')", (cod, msg[:50]))
    except Exception as e:
        _registrar("CT18 comando desconhecido — cod=-1, estados preservados", False,
                   "(-1, ...)", str(e))

# ---------------------------------------------------------------------------
# CT19 — case insensitive: 'COMPRAR GERADOR' funciona igual a minúsculo
# ---------------------------------------------------------------------------
def test_ct19():
    try:
        eco, upg, prog = _estados_com_pontos(1e9)
        cod, eco2, _, _, msg = processar_comando(
            'COMPRAR GERADOR MINERADORA_LARANJA', eco, upg, prog)
        _, qtd = economia.obter_quantidade_gerador(eco2, 'mineradora_laranja')
        ok = (cod == 0 and qtd == 1)
        _registrar("CT19 case insensitive — 'COMPRAR GERADOR' aceito", ok,
                   "(0, qtd=1)", (cod, qtd))
    except Exception as e:
        _registrar("CT19 case insensitive — 'COMPRAR GERADOR' aceito", False,
                   "(0, qtd=1)", str(e))

# ---------------------------------------------------------------------------
# CT20 — revolucao atualiza multiplicador com cristais ganhos
# ---------------------------------------------------------------------------
def test_ct20():
    try:
        eco, upg, prog = _estados_com_pontos(1e8)
        eco = {**eco, 'pontos_run_max': 1e8}
        _, eco2, _, prog2, _ = processar_comando('revolucao', eco, upg, prog)
        _, mult = economia.obter_multiplicador_revolucao(eco2)
        ok = (mult > 1.0 and prog2['cristais_revolucao'] > 0)
        _registrar("CT20 revolucao — multiplicador > 1.0 após cristais ganhos", ok,
                   "mult > 1.0 e cristais > 0",
                   (mult, prog2['cristais_revolucao']))
    except Exception as e:
        _registrar("CT20 revolucao — multiplicador > 1.0 após cristais ganhos", False,
                   "(mult>1.0, ...)", str(e))

# ---------------------------------------------------------------------------
# Relatório
# ---------------------------------------------------------------------------
def _relatorio():
    print("\n" + "=" * 60)
    print("RELATÓRIO — test_main_console.py")
    print("=" * 60)
    passou = sum(1 for _, s, _, _ in _resultados if s == "PASSOU")
    falhou = sum(1 for _, s, _, _ in _resultados if s == "FALHOU")
    total  = len(_resultados)
    for nome, status, esp, obt in _resultados:
        print(f"  [{status}] {nome}")
        if status != "PASSOU":
            print(f"           Esperado : {esp}")
            print(f"           Obtido   : {obt}")
    print("-" * 60)
    print(f"  Total: {total}  |  Passou: {passou}  |  Falhou: {falhou}")
    print("=" * 60)
    return falhou == 0

if __name__ == '__main__':
    testes = [
        test_ct01, test_ct02, test_ct03, test_ct04, test_ct05,
        test_ct06, test_ct07, test_ct08, test_ct09, test_ct10,
        test_ct11, test_ct12, test_ct13, test_ct14, test_ct15,
        test_ct16, test_ct17, test_ct18, test_ct19, test_ct20,
    ]
    for t in testes:
        t()
    ok = _relatorio()
    exit(0 if ok else 1)
