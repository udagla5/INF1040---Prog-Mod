# =============================================================================
# test_upgrades.py — Módulo testador de upgrades.py
# INF1040 · 2026.1 · Grupo 3WB
# =============================================================================

import upgrades
import economia
from constantes import UPGRADES_CATALOGO

_resultados = []

def _registrar(nome, passou, esperado=None, obtido=None):
    status = "PASSOU" if passou else "FALHOU"
    _resultados.append((nome, status, esperado, obtido))

def _estado_upg():
    _, e = upgrades.inicializar_upgrades()
    return e

def _estado_eco(pontos=0.0):
    _, e = economia.inicializar_estado()
    if pontos > 0:
        _, e = economia.adicionar_pontos(e, pontos)
    return e

# ---------------------------------------------------------------------------
# CT01 — inicializar_upgrades
# ---------------------------------------------------------------------------
def test_ct01():
    try:
        codigo, estado = upgrades.inicializar_upgrades()
        _, comprados   = upgrades.listar_comprados(estado)
        _, disponiveis = upgrades.listar_disponiveis(estado)
        ok = (codigo == 0
              and isinstance(estado, dict)
              and comprados == []
              and len(disponiveis) == 120)
        _registrar("CT01 inicializar_upgrades() — 120 upgrades, comprados=[]", ok,
                   "(0, dict 120 upg)", (codigo, len(disponiveis), comprados))
    except Exception as ex:
        _registrar("CT01 inicializar_upgrades()", False, "(0, dict)", str(ex))

# ---------------------------------------------------------------------------
# CT02-CT04 — listar_disponiveis
# ---------------------------------------------------------------------------
def test_ct02():
    try:
        estado = _estado_upg()
        codigo, lista = upgrades.listar_disponiveis(estado)
        ok = (codigo == 0 and len(lista) == 120)
        _registrar("CT02 listar_disponiveis() — estado inicial", ok,
                   "(0, list 120)", (codigo, len(lista)))
    except Exception as ex:
        _registrar("CT02 listar_disponiveis() — inicial", False, "(0, list)", str(ex))

def test_ct03():
    try:
        upg_e = _estado_upg()
        eco_e = _estado_eco(pontos=100.0)
        id_upg = 'upgrade_mineradora_vermelha_x2'  # custo=100
        _, upg_e, eco_e = upgrades.comprar_upgrade(upg_e, eco_e, id_upg)
        codigo, lista = upgrades.listar_disponiveis(upg_e)
        ids = [u['id'] for u in lista]
        ok = (codigo == 0 and id_upg not in ids and len(lista) == 119)
        _registrar("CT03 listar_disponiveis() — após uma compra", ok,
                   "(0, list 119 sem comprado)", (codigo, len(lista)))
    except Exception as ex:
        _registrar("CT03 listar_disponiveis() — após compra", False, "(0, list)", str(ex))

def test_ct04():
    try:
        upg_e = _estado_upg()
        # Compra todos os 120 upgrades injetando pontos suficientes
        for id_upg, dados in UPGRADES_CATALOGO.items():
            eco_tmp = _estado_eco(pontos=dados['custo'] * 2)
            upgrades.comprar_upgrade(upg_e, eco_tmp, id_upg)
            # Marcar como comprado manualmente via comprar_upgrade
        # Abordagem: comprar todos de uma vez com saldo suficiente
        upg2 = _estado_upg()
        eco2 = _estado_eco(pontos=1e100)
        for id_upg in list(UPGRADES_CATALOGO.keys()):
            _, upg2, eco2 = upgrades.comprar_upgrade(upg2, eco2, id_upg)
        codigo, lista = upgrades.listar_disponiveis(upg2)
        ok = (codigo == 0 and lista == [])
        _registrar("CT04 listar_disponiveis() — todos comprados", ok,
                   "(0, [])", (codigo, lista))
    except Exception as ex:
        _registrar("CT04 listar_disponiveis() — todos comprados", False, "(0, [])", str(ex))

# ---------------------------------------------------------------------------
# CT05-CT06 — listar_comprados
# ---------------------------------------------------------------------------
def test_ct05():
    try:
        estado = _estado_upg()
        codigo, lista = upgrades.listar_comprados(estado)
        ok = (codigo == 0 and lista == [])
        _registrar("CT05 listar_comprados() — estado inicial", ok, "(0, [])", (codigo, lista))
    except Exception as ex:
        _registrar("CT05 listar_comprados() — inicial", False, "(0, [])", str(ex))

def test_ct06():
    try:
        upg_e = _estado_upg()
        eco_e = _estado_eco(pontos=100.0)
        id_upg = 'upgrade_mineradora_vermelha_x2'
        _, upg_e, _ = upgrades.comprar_upgrade(upg_e, eco_e, id_upg)
        codigo, lista = upgrades.listar_comprados(upg_e)
        ids = [u['id'] for u in lista]
        ok = (codigo == 0 and id_upg in ids and len(lista) == 1)
        _registrar("CT06 listar_comprados() — após uma compra", ok,
                   "(0, [upg_comprado])", (codigo, ids))
    except Exception as ex:
        _registrar("CT06 listar_comprados() — após compra", False, "(0, list)", str(ex))

# ---------------------------------------------------------------------------
# CT07-CT08 — listar_por_gerador
# ---------------------------------------------------------------------------
def test_ct07():
    try:
        estado = _estado_upg()
        codigo, lista = upgrades.listar_por_gerador(estado, 'mineradora_vermelha')
        ok = (codigo == 0 and len(lista) == 3)
        _registrar("CT07 listar_por_gerador() — ID válido", ok,
                   "(0, list 3)", (codigo, len(lista)))
    except Exception as ex:
        _registrar("CT07 listar_por_gerador() — ID válido", False, "(0, list)", str(ex))

def test_ct08():
    try:
        estado = _estado_upg()
        codigo, lista = upgrades.listar_por_gerador(estado, 'id_invalido_xyz')
        ok = (codigo == -1 and lista is None)
        _registrar("CT08 listar_por_gerador() — ID inexistente", ok,
                   "(-1, None)", (codigo, lista))
    except Exception as ex:
        _registrar("CT08 listar_por_gerador() — ID inexistente", False, "(-1, None)", str(ex))

# ---------------------------------------------------------------------------
# CT09-CT10 — obter_upgrade
# ---------------------------------------------------------------------------
def test_ct09():
    try:
        estado = _estado_upg()
        id_upg = 'upgrade_mineradora_vermelha_x2'
        codigo, dados = upgrades.obter_upgrade(estado, id_upg)
        ok = (codigo == 0
              and isinstance(dados, dict)
              and dados.get('id') == id_upg
              and dados.get('fator') == 2.0)
        _registrar("CT09 obter_upgrade() — ID válido", ok,
                   "(0, dict fator=2.0)", (codigo, dados.get('fator') if dados else None))
    except Exception as ex:
        _registrar("CT09 obter_upgrade() — ID válido", False, "(0, dict)", str(ex))

def test_ct10():
    try:
        estado = _estado_upg()
        codigo, dados = upgrades.obter_upgrade(estado, 'id_invalido_xyz')
        ok = (codigo == -1 and dados is None)
        _registrar("CT10 obter_upgrade() — ID inexistente", ok,
                   "(-1, None)", (codigo, dados))
    except Exception as ex:
        _registrar("CT10 obter_upgrade() — ID inexistente", False, "(-1, None)", str(ex))

# ---------------------------------------------------------------------------
# CT11-CT14 — pode_comprar
# ---------------------------------------------------------------------------
def test_ct11():
    try:
        upg_e = _estado_upg()
        eco_e = _estado_eco(pontos=200.0)
        codigo, pode = upgrades.pode_comprar(upg_e, eco_e, 'upgrade_mineradora_vermelha_x2')
        ok = (codigo == 0 and pode is True)
        _registrar("CT11 pode_comprar() — saldo suficiente, disponível", ok,
                   "(0, True)", (codigo, pode))
    except Exception as ex:
        _registrar("CT11 pode_comprar() — saldo suficiente", False, "(0, True)", str(ex))

def test_ct12():
    try:
        upg_e = _estado_upg()
        eco_e = _estado_eco(pontos=0.0)
        codigo, pode = upgrades.pode_comprar(upg_e, eco_e, 'upgrade_mineradora_vermelha_x2')
        ok = (codigo == 0 and pode is False)
        _registrar("CT12 pode_comprar() — saldo insuficiente", ok,
                   "(0, False)", (codigo, pode))
    except Exception as ex:
        _registrar("CT12 pode_comprar() — saldo insuficiente", False, "(0, False)", str(ex))

def test_ct13():
    try:
        upg_e = _estado_upg()
        eco_e = _estado_eco(pontos=200.0)
        id_upg = 'upgrade_mineradora_vermelha_x2'
        _, upg_e, _ = upgrades.comprar_upgrade(upg_e, eco_e, id_upg)
        eco_e2 = _estado_eco(pontos=200.0)
        codigo, pode = upgrades.pode_comprar(upg_e, eco_e2, id_upg)
        ok = (codigo == 0 and pode is False)
        _registrar("CT13 pode_comprar() — upgrade já comprado", ok,
                   "(0, False)", (codigo, pode))
    except Exception as ex:
        _registrar("CT13 pode_comprar() — já comprado", False, "(0, False)", str(ex))

def test_ct14():
    try:
        upg_e = _estado_upg()
        eco_e = _estado_eco(pontos=200.0)
        codigo, pode = upgrades.pode_comprar(upg_e, eco_e, 'id_invalido_xyz')
        ok = (codigo == -1 and pode is None)
        _registrar("CT14 pode_comprar() — ID inexistente", ok,
                   "(-1, None)", (codigo, pode))
    except Exception as ex:
        _registrar("CT14 pode_comprar() — ID inexistente", False, "(-1, None)", str(ex))

# ---------------------------------------------------------------------------
# CT15-CT18 — comprar_upgrade
# ---------------------------------------------------------------------------
def test_ct15():
    try:
        upg_e = _estado_upg()
        eco_e = _estado_eco(pontos=200.0)
        id_upg = 'upgrade_mineradora_vermelha_x2'
        codigo, upg_n, eco_n = upgrades.comprar_upgrade(upg_e, eco_e, id_upg)
        _, comprados = upgrades.listar_comprados(upg_n)
        ids_comp = [u['id'] for u in comprados]
        _, pontos = economia.obter_pontos(eco_n)
        ok = (codigo == 0 and id_upg in ids_comp and pontos < 200.0)
        _registrar("CT15 comprar_upgrade() — compra válida", ok,
                   "(0, upg_atualizado, eco_atualizado)", (codigo, id_upg in ids_comp, pontos))
    except Exception as ex:
        _registrar("CT15 comprar_upgrade() — válida", False, "(0, upg, eco)", str(ex))

def test_ct16():
    try:
        upg_e = _estado_upg()
        eco_e = _estado_eco(pontos=0.0)
        id_upg = 'upgrade_mineradora_vermelha_x2'
        codigo, upg_o, eco_o = upgrades.comprar_upgrade(upg_e, eco_e, id_upg)
        _, comprados = upgrades.listar_comprados(upg_o)
        ok = (codigo == -2 and comprados == [])
        _registrar("CT16 comprar_upgrade() — pontos insuficientes", ok,
                   "(-2, orig, orig)", (codigo, comprados))
    except Exception as ex:
        _registrar("CT16 comprar_upgrade() — pontos insuficientes", False, "(-2, orig, orig)", str(ex))

def test_ct17():
    try:
        upg_e = _estado_upg()
        eco_e = _estado_eco(pontos=1000.0)
        id_upg = 'upgrade_mineradora_vermelha_x2'
        _, upg_e, eco_e = upgrades.comprar_upgrade(upg_e, eco_e, id_upg)
        eco_e2 = _estado_eco(pontos=1000.0)
        codigo, upg_o, eco_o = upgrades.comprar_upgrade(upg_e, eco_e2, id_upg)
        ok = (codigo == -3)
        _registrar("CT17 comprar_upgrade() — upgrade já comprado", ok,
                   "(-3, orig, orig)", (codigo,))
    except Exception as ex:
        _registrar("CT17 comprar_upgrade() — já comprado", False, "(-3, orig, orig)", str(ex))

def test_ct18():
    try:
        upg_e = _estado_upg()
        eco_e = _estado_eco(pontos=1000.0)
        codigo, upg_o, eco_o = upgrades.comprar_upgrade(upg_e, eco_e, 'id_invalido_xyz')
        ok = (codigo == -1)
        _registrar("CT18 comprar_upgrade() — ID inexistente", ok,
                   "(-1, orig, orig)", (codigo,))
    except Exception as ex:
        _registrar("CT18 comprar_upgrade() — ID inexistente", False, "(-1, orig, orig)", str(ex))

# ---------------------------------------------------------------------------
# CT19-CT22 — calcular_fatores_por_gerador
# ---------------------------------------------------------------------------
def test_ct19():
    try:
        estado = _estado_upg()
        codigo, fatores = upgrades.calcular_fatores_por_gerador(estado)
        todos_um = all(abs(v - 1.0) < 1e-9 for v in fatores.values())
        ok = (codigo == 0 and todos_um)
        _registrar("CT19 calcular_fatores_por_gerador() — nenhum comprado → todos 1.0", ok,
                   "(0, dict todos=1.0)", (codigo, todos_um))
    except Exception as ex:
        _registrar("CT19 calcular_fatores_por_gerador() — nenhum", False, "(0, dict)", str(ex))

def test_ct20():
    try:
        upg_e = _estado_upg()
        eco_e = _estado_eco(pontos=200.0)
        _, upg_e, _ = upgrades.comprar_upgrade(upg_e, eco_e, 'upgrade_mineradora_vermelha_x2')
        codigo, fatores = upgrades.calcular_fatores_por_gerador(upg_e)
        fator_alvo = fatores.get('mineradora_vermelha', 0)
        ok = (codigo == 0 and abs(fator_alvo - 2.0) < 1e-9)
        _registrar("CT20 calcular_fatores_por_gerador() — x2 comprado → fator=2.0", ok,
                   "(0, dict fator=2.0)", (codigo, fator_alvo))
    except Exception as ex:
        _registrar("CT20 calcular_fatores_por_gerador() — x2", False, "(0, dict)", str(ex))

def test_ct21():
    try:
        upg_e = _estado_upg()
        eco_e = _estado_eco(pontos=1e6)
        _, upg_e, eco_e = upgrades.comprar_upgrade(upg_e, eco_e, 'upgrade_mineradora_vermelha_x2')
        _, upg_e, eco_e = upgrades.comprar_upgrade(upg_e, eco_e, 'upgrade_mineradora_vermelha_x5')
        codigo, fatores = upgrades.calcular_fatores_por_gerador(upg_e)
        fator_alvo = fatores.get('mineradora_vermelha', 0)
        ok = (codigo == 0 and abs(fator_alvo - 10.0) < 1e-9)
        _registrar("CT21 calcular_fatores_por_gerador() — x2+x5 → fator=10.0", ok,
                   "(0, dict fator=10.0)", (codigo, fator_alvo))
    except Exception as ex:
        _registrar("CT21 calcular_fatores_por_gerador() — x2+x5", False, "(0, dict)", str(ex))

def test_ct22():
    try:
        upg_e = _estado_upg()
        eco_e = _estado_eco(pontos=1e6)
        _, upg_e, eco_e = upgrades.comprar_upgrade(upg_e, eco_e, 'upgrade_mineradora_vermelha_x2')
        _, upg_e, eco_e = upgrades.comprar_upgrade(upg_e, eco_e, 'upgrade_fabrica_vermelha_x2')
        codigo, fatores = upgrades.calcular_fatores_por_gerador(upg_e)
        f_min = fatores.get('mineradora_vermelha', 0)
        f_fab = fatores.get('fabrica_vermelha', 0)
        f_out = fatores.get('usina_vermelha', 0)
        ok = (codigo == 0
              and abs(f_min - 2.0) < 1e-9
              and abs(f_fab - 2.0) < 1e-9
              and abs(f_out - 1.0) < 1e-9)
        _registrar("CT22 calcular_fatores_por_gerador() — fatores independentes", ok,
                   "(0, min=2.0 fab=2.0 usi=1.0)", (codigo, f_min, f_fab, f_out))
    except Exception as ex:
        _registrar("CT22 calcular_fatores_por_gerador() — independentes", False, "(0, dict)", str(ex))

# ---------------------------------------------------------------------------
# Relatório
# ---------------------------------------------------------------------------
def _relatorio():
    print("\n" + "=" * 60)
    print("RELATÓRIO — test_upgrades.py")
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
              test_ct21, test_ct22]:
        t()
    ok = _relatorio()
    exit(0 if ok else 1)
