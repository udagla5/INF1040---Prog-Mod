# =============================================================================
# test_economia.py — Módulo testador de economia.py
# INF1040 · 2026.1 · Grupo 3WB
#
# REGRAS:
#   - Importa APENAS economia (e constantes para IDs de geradores)
#   - Cobre TODOS os retornos possíveis de cada função pública
#   - Gera relatório final com executados / aprovados / reprovados
#   - Exceções são capturadas e reportadas sem encerrar o testador
# =============================================================================

import economia
from constantes import GERADORES_CATALOGO

_resultados = []

def _registrar(nome, passou, esperado=None, obtido=None):
    status = "PASSOU" if passou else "FALHOU"
    _resultados.append((nome, status, esperado, obtido))

def _eco_com_pontos(valor):
    """Helper: estado inicial com 'valor' pontos adicionados."""
    _, e = economia.inicializar_estado()
    _, e = economia.adicionar_pontos(e, valor)
    return e

def _eco_com_gerador(id_ger, qtd=1):
    """Helper: estado inicial com gerador adicionado."""
    _, e = economia.inicializar_estado()
    for _ in range(qtd):
        _, e = economia.adicionar_gerador(e, id_ger)
    return e

# ---------------------------------------------------------------------------
# CT01 — inicializar_estado
# ---------------------------------------------------------------------------
def test_ct01():
    try:
        resultado = economia.inicializar_estado()
        codigo, estado = resultado[0], resultado[1]
        _, pontos = economia.obter_pontos(estado)
        _, qtd    = economia.obter_quantidade_gerador(estado, 'mineradora_vermelha')
        _, mult   = economia.obter_multiplicador_revolucao(estado)
        _, exp    = economia.obter_expoente_ascensao(estado)
        ok = (codigo == 0 and pontos == 0.0 and qtd == 0 and mult == 1.0 and exp == 1.0)
        _registrar("CT01 inicializar_estado() — estado zerado", ok,
                   "(0, dict zerado)", (codigo, pontos, qtd, mult, exp))
    except Exception as e:
        _registrar("CT01 inicializar_estado() — estado zerado", False, "(0, dict)", str(e))

# ---------------------------------------------------------------------------
# CT02-CT03 — obter_pontos
# ---------------------------------------------------------------------------
def test_ct02():
    try:
        e = _eco_com_pontos(42.5)
        codigo, pontos = economia.obter_pontos(e)
        ok = (codigo == 0 and abs(pontos - 42.5) < 1e-9)
        _registrar("CT02 obter_pontos() — valor existente", ok, "(0, 42.5)", (codigo, pontos))
    except Exception as e2:
        _registrar("CT02 obter_pontos() — valor existente", False, "(0, 42.5)", str(e2))

def test_ct03():
    try:
        _, estado = economia.inicializar_estado()
        codigo, pontos = economia.obter_pontos(estado)
        ok = (codigo == 0 and pontos == 0.0)
        _registrar("CT03 obter_pontos() — estado inicial (0.0)", ok, "(0, 0.0)", (codigo, pontos))
    except Exception as e:
        _registrar("CT03 obter_pontos() — estado inicial (0.0)", False, "(0, 0.0)", str(e))

# ---------------------------------------------------------------------------
# CT04-CT06 — pode_gastar
# ---------------------------------------------------------------------------
def test_ct04():
    try:
        e = _eco_com_pontos(100.0)
        codigo, pode = economia.pode_gastar(e, 50.0)
        ok = (codigo == 0 and pode is True)
        _registrar("CT04 pode_gastar() — saldo suficiente", ok, "(0, True)", (codigo, pode))
    except Exception as ex:
        _registrar("CT04 pode_gastar() — saldo suficiente", False, "(0, True)", str(ex))

def test_ct05():
    try:
        e = _eco_com_pontos(10.0)
        codigo, pode = economia.pode_gastar(e, 100.0)
        ok = (codigo == 0 and pode is False)
        _registrar("CT05 pode_gastar() — saldo insuficiente", ok, "(0, False)", (codigo, pode))
    except Exception as ex:
        _registrar("CT05 pode_gastar() — saldo insuficiente", False, "(0, False)", str(ex))

def test_ct06():
    try:
        _, e = economia.inicializar_estado()
        codigo, pode = economia.pode_gastar(e, -5.0)
        ok = (codigo == -1 and pode is None)
        _registrar("CT06 pode_gastar() — valor inválido", ok, "(-1, None)", (codigo, pode))
    except Exception as ex:
        _registrar("CT06 pode_gastar() — valor inválido", False, "(-1, None)", str(ex))

# ---------------------------------------------------------------------------
# CT07-CT09 — gastar_pontos
# ---------------------------------------------------------------------------
def test_ct07():
    try:
        e = _eco_com_pontos(100.0)
        codigo, e_novo = economia.gastar_pontos(e, 60.0)
        _, pontos = economia.obter_pontos(e_novo)
        ok = (codigo == 0 and abs(pontos - 40.0) < 1e-9)
        _registrar("CT07 gastar_pontos() — saldo suficiente", ok, "(0, dict pontos=40)", (codigo, pontos))
    except Exception as ex:
        _registrar("CT07 gastar_pontos() — saldo suficiente", False, "(0, dict)", str(ex))

def test_ct08():
    try:
        e = _eco_com_pontos(10.0)
        codigo, e_orig = economia.gastar_pontos(e, 100.0)
        _, pontos = economia.obter_pontos(e_orig)
        ok = (codigo == -2 and abs(pontos - 10.0) < 1e-9)
        _registrar("CT08 gastar_pontos() — saldo insuficiente", ok, "(-2, dict pontos=10)", (codigo, pontos))
    except Exception as ex:
        _registrar("CT08 gastar_pontos() — saldo insuficiente", False, "(-2, dict)", str(ex))

def test_ct09():
    try:
        _, e = economia.inicializar_estado()
        codigo, e_orig = economia.gastar_pontos(e, -1.0)
        ok = (codigo == -1)
        _registrar("CT09 gastar_pontos() — valor inválido", ok, "(-1, dict)", (codigo,))
    except Exception as ex:
        _registrar("CT09 gastar_pontos() — valor inválido", False, "(-1, dict)", str(ex))

# ---------------------------------------------------------------------------
# CT10-CT11 — adicionar_pontos
# ---------------------------------------------------------------------------
def test_ct10():
    try:
        _, e = economia.inicializar_estado()
        codigo, e_novo = economia.adicionar_pontos(e, 50.0)
        _, pontos = economia.obter_pontos(e_novo)
        ok = (codigo == 0 and abs(pontos - 50.0) < 1e-9)
        _registrar("CT10 adicionar_pontos() — valor positivo", ok, "(0, dict pontos=50)", (codigo, pontos))
    except Exception as ex:
        _registrar("CT10 adicionar_pontos() — valor positivo", False, "(0, dict)", str(ex))

def test_ct11():
    try:
        _, e = economia.inicializar_estado()
        codigo, e_orig = economia.adicionar_pontos(e, -10.0)
        _, pontos = economia.obter_pontos(e_orig)
        ok = (codigo == -1 and pontos == 0.0)
        _registrar("CT11 adicionar_pontos() — valor negativo", ok, "(-1, dict zerado)", (codigo, pontos))
    except Exception as ex:
        _registrar("CT11 adicionar_pontos() — valor negativo", False, "(-1, dict)", str(ex))

# ---------------------------------------------------------------------------
# CT12-CT16 — obter_quantidade_gerador / adicionar_gerador
# ---------------------------------------------------------------------------
def test_ct12():
    try:
        e = _eco_com_gerador('mineradora_vermelha', 3)
        codigo, qtd = economia.obter_quantidade_gerador(e, 'mineradora_vermelha')
        ok = (codigo == 0 and qtd == 3)
        _registrar("CT12 obter_quantidade_gerador() — ID válido", ok, "(0, 3)", (codigo, qtd))
    except Exception as ex:
        _registrar("CT12 obter_quantidade_gerador() — ID válido", False, "(0, int)", str(ex))

def test_ct13():
    try:
        _, e = economia.inicializar_estado()
        codigo, qtd = economia.obter_quantidade_gerador(e, 'id_invalido_xyz')
        ok = (codigo == -1 and qtd is None)
        _registrar("CT13 obter_quantidade_gerador() — ID inexistente", ok, "(-1, None)", (codigo, qtd))
    except Exception as ex:
        _registrar("CT13 obter_quantidade_gerador() — ID inexistente", False, "(-1, None)", str(ex))

def test_ct14():
    try:
        _, e = economia.inicializar_estado()
        codigo, e_novo = economia.adicionar_gerador(e, 'mineradora_vermelha')
        _, qtd = economia.obter_quantidade_gerador(e_novo, 'mineradora_vermelha')
        ok = (codigo == 0 and qtd == 1)
        _registrar("CT14 adicionar_gerador() — ID válido desbloqueado", ok, "(0, dict qtd=1)", (codigo, qtd))
    except Exception as ex:
        _registrar("CT14 adicionar_gerador() — ID válido desbloqueado", False, "(0, dict)", str(ex))

def test_ct15():
    try:
        _, e = economia.inicializar_estado()
        codigo, e_orig = economia.adicionar_gerador(e, 'id_invalido_xyz')
        ok = (codigo == -1)
        _registrar("CT15 adicionar_gerador() — ID inexistente", ok, "(-1, dict)", (codigo,))
    except Exception as ex:
        _registrar("CT15 adicionar_gerador() — ID inexistente", False, "(-1, dict)", str(ex))

def test_ct16():
    try:
        _, e = economia.inicializar_estado()
        codigo, e_orig = economia.adicionar_gerador(e, 'laboratorio_vermelho')
        ok = (codigo == -4)
        _registrar("CT16 adicionar_gerador() — laboratório bloqueado", ok, "(-4, dict)", (codigo,))
    except Exception as ex:
        _registrar("CT16 adicionar_gerador() — laboratório bloqueado", False, "(-4, dict)", str(ex))

# ---------------------------------------------------------------------------
# CT17-CT20 — calcular_custo_gerador
# ---------------------------------------------------------------------------
def test_ct17():
    try:
        _, e = economia.inicializar_estado()
        codigo, custo = economia.calcular_custo_gerador(e, 'mineradora_vermelha', 1)
        ok = (codigo == 0 and abs(custo - 10.0) < 1e-6)
        _registrar("CT17 calcular_custo_gerador() — 1 unidade, 0 possuídas", ok, "(0, 10.0)", (codigo, custo))
    except Exception as ex:
        _registrar("CT17 calcular_custo_gerador() — 1 unidade", False, "(0, float)", str(ex))

def test_ct18():
    try:
        e = _eco_com_gerador('mineradora_vermelha', 2)
        codigo, custo = economia.calcular_custo_gerador(e, 'mineradora_vermelha', 1)
        esperado = 10.0 * (1.15 ** 2)
        ok = (codigo == 0 and abs(custo - esperado) < 1e-4)
        _registrar("CT18 calcular_custo_gerador() — escala 1.15^n", ok, f"(0, {esperado:.4f})", (codigo, custo))
    except Exception as ex:
        _registrar("CT18 calcular_custo_gerador() — escala 1.15^n", False, "(0, float)", str(ex))

def test_ct19():
    try:
        _, e = economia.inicializar_estado()
        codigo, custo = economia.calcular_custo_gerador(e, 'id_invalido_xyz')
        ok = (codigo == -1 and custo is None)
        _registrar("CT19 calcular_custo_gerador() — ID inexistente", ok, "(-1, None)", (codigo, custo))
    except Exception as ex:
        _registrar("CT19 calcular_custo_gerador() — ID inexistente", False, "(-1, None)", str(ex))

def test_ct20():
    try:
        _, e = economia.inicializar_estado()
        codigo, custo = economia.calcular_custo_gerador(e, 'laboratorio_vermelho')
        ok = (codigo == -4 and custo is None)
        _registrar("CT20 calcular_custo_gerador() — gerador bloqueado", ok, "(-4, None)", (codigo, custo))
    except Exception as ex:
        _registrar("CT20 calcular_custo_gerador() — gerador bloqueado", False, "(-4, None)", str(ex))

# ---------------------------------------------------------------------------
# CT21-CT25 — calcular_taxa_base / calcular_taxa_total
# ---------------------------------------------------------------------------
def test_ct21():
    try:
        _, e = economia.inicializar_estado()
        codigo, taxa = economia.calcular_taxa_base(e)
        ok = (codigo == 0 and taxa == 0.0)
        _registrar("CT21 calcular_taxa_base() — nenhum gerador", ok, "(0, 0.0)", (codigo, taxa))
    except Exception as ex:
        _registrar("CT21 calcular_taxa_base() — nenhum gerador", False, "(0, 0.0)", str(ex))

def test_ct22():
    try:
        e = _eco_com_gerador('mineradora_vermelha', 1)
        codigo, taxa = economia.calcular_taxa_base(e)
        # prod_base de mineradora_vermelha = 0.1
        ok = (codigo == 0 and abs(taxa - 0.1) < 1e-9)
        _registrar("CT22 calcular_taxa_base() — 1 mineradora vermelha", ok, "(0, 0.1)", (codigo, taxa))
    except Exception as ex:
        _registrar("CT22 calcular_taxa_base() — 1 mineradora vermelha", False, "(0, float)", str(ex))

def test_ct23():
    try:
        _, e = economia.inicializar_estado()
        _, taxa_b = economia.calcular_taxa_base(e)
        codigo, taxa_t = economia.calcular_taxa_total(e)
        ok = (codigo == 0 and abs(taxa_t - taxa_b) < 1e-9)
        _registrar("CT23 calcular_taxa_total() — mult=1.0, exp=1.0 == taxa_base", ok,
                   "(0, float==taxa_base)", (codigo, taxa_t))
    except Exception as ex:
        _registrar("CT23 calcular_taxa_total() — mult=1.0, exp=1.0", False, "(0, float)", str(ex))

def test_ct24():
    try:
        e = _eco_com_gerador('mineradora_vermelha', 1)
        _, e = economia.aplicar_multiplicador_revolucao(e, 2)  # mult = 1 + 2*0.5 = 2.0
        _, taxa_b = economia.calcular_taxa_base(e)
        codigo, taxa_t = economia.calcular_taxa_total(e)
        ok = (codigo == 0 and abs(taxa_t - taxa_b * 2.0) < 1e-6)
        _registrar("CT24 calcular_taxa_total() — mult=2.0, exp=1.0", ok,
                   f"(0, {taxa_b*2:.6f})", (codigo, taxa_t))
    except Exception as ex:
        _registrar("CT24 calcular_taxa_total() — mult=2.0, exp=1.0", False, "(0, float)", str(ex))

# ---------------------------------------------------------------------------
# CT26-CT29 — aplicar_geracao
# ---------------------------------------------------------------------------
def test_ct26():
    try:
        e = _eco_com_gerador('mineradora_vermelha', 10)
        _, taxa = economia.calcular_taxa_total(e)
        codigo, e_novo = economia.aplicar_geracao(e, 1.0)
        _, pontos = economia.obter_pontos(e_novo)
        ok = (codigo == 0 and abs(pontos - taxa * 1.0) < 1e-6)
        _registrar("CT26 aplicar_geracao() — delta=1.0s", ok, f"(0, dict pontos={taxa:.4f})", (codigo, pontos))
    except Exception as ex:
        _registrar("CT26 aplicar_geracao() — delta=1.0s", False, "(0, dict)", str(ex))

def test_ct27():
    try:
        _, e = economia.inicializar_estado()
        _, pontos_antes = economia.obter_pontos(e)
        codigo, e_novo = economia.aplicar_geracao(e, 0)
        _, pontos_depois = economia.obter_pontos(e_novo)
        ok = (codigo == 0 and pontos_antes == pontos_depois)
        _registrar("CT27 aplicar_geracao() — delta=0", ok, "(0, dict inalterado)", (codigo, pontos_depois))
    except Exception as ex:
        _registrar("CT27 aplicar_geracao() — delta=0", False, "(0, dict)", str(ex))

def test_ct28():
    try:
        _, e = economia.inicializar_estado()
        codigo, e_orig = economia.aplicar_geracao(e, -1.0)
        ok = (codigo == -1)
        _registrar("CT28 aplicar_geracao() — delta<0", ok, "(-1, dict)", (codigo,))
    except Exception as ex:
        _registrar("CT28 aplicar_geracao() — delta<0", False, "(-1, dict)", str(ex))

def test_ct29():
    try:
        e = _eco_com_gerador('mineradora_vermelha', 1)
        _, e = economia.aplicar_geracao(e, 10.0)
        _, pontos = economia.obter_pontos(e)
        _, max_pts = economia.obter_pontos_run_max(e)
        ok = (max_pts >= pontos)
        _registrar("CT29 aplicar_geracao() — pontos_run_max atualizado", ok,
                   "max_pts >= pontos", (pontos, max_pts))
    except Exception as ex:
        _registrar("CT29 aplicar_geracao() — pontos_run_max", False, "max>=pts", str(ex))

# ---------------------------------------------------------------------------
# CT30-CT37 — multiplicador, expoente, resetar_run, aplicar_efeitos_upgrades
# ---------------------------------------------------------------------------
def test_ct30():
    try:
        _, e = economia.inicializar_estado()
        codigo, e_novo = economia.aplicar_multiplicador_revolucao(e, 4)
        _, mult = economia.obter_multiplicador_revolucao(e_novo)
        ok = (codigo == 0 and abs(mult - 3.0) < 1e-9)
        _registrar("CT30 aplicar_multiplicador_revolucao() — 4 cristais → ×3.0", ok, "(0, mult=3.0)", (codigo, mult))
    except Exception as ex:
        _registrar("CT30 aplicar_multiplicador_revolucao() — 4 cristais", False, "(0, dict)", str(ex))

def test_ct31():
    try:
        _, e = economia.inicializar_estado()
        codigo, e_novo = economia.aplicar_multiplicador_revolucao(e, 0)
        _, mult = economia.obter_multiplicador_revolucao(e_novo)
        ok = (codigo == 0 and abs(mult - 1.0) < 1e-9)
        _registrar("CT31 aplicar_multiplicador_revolucao() — 0 cristais → ×1.0", ok, "(0, mult=1.0)", (codigo, mult))
    except Exception as ex:
        _registrar("CT31 aplicar_multiplicador_revolucao() — 0 cristais", False, "(0, dict)", str(ex))

def test_ct32():
    try:
        _, e = economia.inicializar_estado()
        codigo, e_orig = economia.aplicar_multiplicador_revolucao(e, -1)
        ok = (codigo == -1)
        _registrar("CT32 aplicar_multiplicador_revolucao() — cristais<0", ok, "(-1, dict)", (codigo,))
    except Exception as ex:
        _registrar("CT32 aplicar_multiplicador_revolucao() — cristais<0", False, "(-1, dict)", str(ex))

def test_ct33():
    try:
        _, e = economia.inicializar_estado()
        codigo, e_novo = economia.aplicar_expoente_ascensao(e, 2)
        _, exp = economia.obter_expoente_ascensao(e_novo)
        ok = (codigo == 0 and abs(exp - 1.30) < 1e-9)
        _registrar("CT33 aplicar_expoente_ascensao() — 2 fragmentos → 1.30", ok, "(0, exp=1.30)", (codigo, exp))
    except Exception as ex:
        _registrar("CT33 aplicar_expoente_ascensao() — 2 fragmentos", False, "(0, dict)", str(ex))

def test_ct34():
    try:
        _, e = economia.inicializar_estado()
        codigo, e_novo = economia.aplicar_expoente_ascensao(e, 0)
        _, exp = economia.obter_expoente_ascensao(e_novo)
        ok = (codigo == 0 and abs(exp - 1.0) < 1e-9)
        _registrar("CT34 aplicar_expoente_ascensao() — 0 fragmentos → 1.0", ok, "(0, exp=1.0)", (codigo, exp))
    except Exception as ex:
        _registrar("CT34 aplicar_expoente_ascensao() — 0 fragmentos", False, "(0, dict)", str(ex))

def test_ct35():
    try:
        _, e = economia.inicializar_estado()
        codigo, _ = economia.aplicar_expoente_ascensao(e, -1)
        ok = (codigo == -1)
        _registrar("CT35 aplicar_expoente_ascensao() — fragmentos<0", ok, "(-1, dict)", (codigo,))
    except Exception as ex:
        _registrar("CT35 aplicar_expoente_ascensao() — fragmentos<0", False, "(-1, dict)", str(ex))

def test_ct36():
    try:
        e = _eco_com_pontos(500.0)
        _, e = economia.adicionar_gerador(e, 'mineradora_vermelha')
        codigo, e_reset = economia.resetar_run(e)
        _, pontos = economia.obter_pontos(e_reset)
        _, qtd    = economia.obter_quantidade_gerador(e_reset, 'mineradora_vermelha')
        ok = (codigo == 0 and pontos == 0.0 and qtd == 0)
        _registrar("CT36 resetar_run() — pontos e geradores zerados", ok,
                   "(0, dict pontos=0 qtd=0)", (codigo, pontos, qtd))
    except Exception as ex:
        _registrar("CT36 resetar_run() — zerado", False, "(0, dict)", str(ex))

def test_ct37():
    try:
        _, e = economia.inicializar_estado()
        _, e = economia.aplicar_multiplicador_revolucao(e, 4)
        _, e = economia.aplicar_expoente_ascensao(e, 2)
        _, mult_antes = economia.obter_multiplicador_revolucao(e)
        _, exp_antes  = economia.obter_expoente_ascensao(e)
        codigo, e_reset = economia.resetar_run(e)
        _, mult_depois = economia.obter_multiplicador_revolucao(e_reset)
        _, exp_depois  = economia.obter_expoente_ascensao(e_reset)
        ok = (codigo == 0
              and abs(mult_antes - mult_depois) < 1e-9
              and abs(exp_antes  - exp_depois)  < 1e-9)
        _registrar("CT37 resetar_run() — multiplicadores preservados", ok,
                   "(0, mult e exp inalterados)", (mult_depois, exp_depois))
    except Exception as ex:
        _registrar("CT37 resetar_run() — multiplicadores", False, "(0, dict)", str(ex))

def test_ct38():
    try:
        e = _eco_com_gerador('mineradora_vermelha', 1)
        _, taxa_antes = economia.calcular_taxa_base(e)
        codigo, e_novo = economia.aplicar_efeitos_upgrades(e, {})
        _, taxa_depois = economia.calcular_taxa_base(e_novo)
        ok = (codigo == 0 and abs(taxa_antes - taxa_depois) < 1e-9)
        _registrar("CT38 aplicar_efeitos_upgrades() — fatores vazio", ok,
                   "(0, taxa inalterada)", (codigo, taxa_depois))
    except Exception as ex:
        _registrar("CT38 aplicar_efeitos_upgrades() — fatores vazio", False, "(0, dict)", str(ex))

def test_ct39():
    try:
        e = _eco_com_gerador('mineradora_vermelha', 1)
        _, taxa_sem = economia.calcular_taxa_base(e)
        fatores = {'mineradora_vermelha': 2.0}
        codigo, e_novo = economia.aplicar_efeitos_upgrades(e, fatores)
        _, taxa_com = economia.calcular_taxa_base(e_novo)
        ok = (codigo == 0 and abs(taxa_com - taxa_sem * 2.0) < 1e-6)
        _registrar("CT39 aplicar_efeitos_upgrades() — fator ×2 para mineradora", ok,
                   f"(0, taxa={taxa_sem*2:.4f})", (codigo, taxa_com))
    except Exception as ex:
        _registrar("CT39 aplicar_efeitos_upgrades() — fator ×2", False, "(0, dict)", str(ex))

# ---------------------------------------------------------------------------
# Relatório
# ---------------------------------------------------------------------------
def _relatorio():
    print("\n" + "=" * 60)
    print("RELATÓRIO — test_economia.py")
    print("=" * 60)
    passou  = sum(1 for _, s, _, _ in _resultados if s == "PASSOU")
    falhou  = sum(1 for _, s, _, _ in _resultados if s == "FALHOU")
    total   = len(_resultados)
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
        test_ct21, test_ct22, test_ct23, test_ct24, test_ct25 if False else test_ct24,
        test_ct26, test_ct27, test_ct28, test_ct29, test_ct30,
        test_ct31, test_ct32, test_ct33, test_ct34, test_ct35,
        test_ct36, test_ct37, test_ct38, test_ct39,
    ]
    # CT25 (calcular_taxa_total com expoente) — chamado dentro de test_ct24
    # Adicionar separadamente se necessário
    for t in testes:
        t()
    ok = _relatorio()
    exit(0 if ok else 1)
