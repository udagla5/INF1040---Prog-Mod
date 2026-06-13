# =============================================================================
# test_persistencia.py — Módulo testador de persistencia.py
# INF1040 - 2026.1 - Grupo 2
#
# REGRAS:
#   - Usa diretório temporário para não sujar saves/ real
#   - Cobre TODOS os retornos possíveis de cada função pública
#   - Gera relatório final com executados / aprovados / reprovados
#   - Exceções são capturadas e reportadas sem encerrar o testador
# =============================================================================

import os
import tempfile
import shutil

import persistencia
import economia
import upgrades
import progresso

_resultados = []

def _registrar(nome, passou, esperado=None, obtido=None):
    status = "PASSOU" if passou else "FALHOU"
    _resultados.append((nome, status, esperado, obtido))

# ---------------------------------------------------------------------------
# Fixtures — diretório temporário isolado por teste
# ---------------------------------------------------------------------------
def _setup():
    """Cria dir temporário e redireciona _ARQUIVO_SAVE para dentro dele."""
    tmp = tempfile.mkdtemp()
    persistencia._ARQUIVO_SAVE = os.path.join(tmp, 'save.json')
    return tmp

def _teardown(tmp):
    shutil.rmtree(tmp, ignore_errors=True)

def _estados_padrao():
    _, eco  = economia.inicializar_estado()
    _, upg  = upgrades.inicializar_upgrades()
    _, prog = progresso.inicializar_progresso()
    _, eco  = economia.adicionar_pontos(eco, 500.0)
    _, eco  = economia.adicionar_gerador(eco, 'mineradora_vermelha')
    return eco, upg, prog

# ---------------------------------------------------------------------------
# CT01 — salvar_jogo: salva sem erro e cria o arquivo
# ---------------------------------------------------------------------------
def test_ct01():
    tmp = _setup()
    try:
        eco, upg, prog = _estados_padrao()
        cod, _ = persistencia.salvar_jogo(eco, upg, prog)
        arquivo_existe = os.path.isfile(persistencia._ARQUIVO_SAVE)
        ok = (cod == 0 and arquivo_existe)
        _registrar("CT01 salvar_jogo() — cria arquivo com sucesso", ok,
                   "(0, None) e arquivo existe", (cod, arquivo_existe))
    except Exception as e:
        _registrar("CT01 salvar_jogo() — cria arquivo com sucesso", False, "(0, None)", str(e))
    finally:
        _teardown(tmp)

# ---------------------------------------------------------------------------
# CT02 — salvar_jogo: retorna -1 se o diretório não tem permissão de escrita
# ---------------------------------------------------------------------------
def test_ct02():
    tmp = _setup()
    try:
        # Aponta para caminho impossível (diretório inexistente somente-leitura)
        persistencia._ARQUIVO_SAVE = os.path.join(tmp, 'nao_existe', 'x', 'save.json')
        # Cria o diretório pai como somente-leitura para forçar falha
        bloqueado = os.path.join(tmp, 'nao_existe', 'x')
        os.makedirs(os.path.join(tmp, 'nao_existe'))
        # Força erro redirecionando para path impossível em profundidade
        persistencia._ARQUIVO_SAVE = '/nao_existe_raiz/saves/save.json'
        eco, upg, prog = _estados_padrao()
        cod, _ = persistencia.salvar_jogo(eco, upg, prog)
        ok = (cod == -1)
        _registrar("CT02 salvar_jogo() — retorna -1 em caminho inacessível", ok,
                   "(-1, None)", (cod,))
    except Exception as e:
        _registrar("CT02 salvar_jogo() — retorna -1 em caminho inacessível", False, "(-1, None)", str(e))
    finally:
        _teardown(tmp)

# ---------------------------------------------------------------------------
# CT03 — carregar_jogo: retorna -1 quando não há arquivo
# ---------------------------------------------------------------------------
def test_ct03():
    tmp = _setup()
    try:
        cod, dados = persistencia.carregar_jogo()
        ok = (cod == -1 and dados is None)
        _registrar("CT03 carregar_jogo() — arquivo inexistente → -1", ok,
                   "(-1, None)", (cod, dados))
    except Exception as e:
        _registrar("CT03 carregar_jogo() — arquivo inexistente → -1", False, "(-1, None)", str(e))
    finally:
        _teardown(tmp)

# ---------------------------------------------------------------------------
# CT04 — carregar_jogo: recupera exatamente o que foi salvo
# ---------------------------------------------------------------------------
def test_ct04():
    tmp = _setup()
    try:
        eco, upg, prog = _estados_padrao()
        persistencia.salvar_jogo(eco, upg, prog)
        cod, dados = persistencia.carregar_jogo()
        eco2, upg2, prog2 = dados
        pontos_ok  = eco2['pontos'] == eco['pontos']
        comprados_ok = upg2['comprados'] == upg['comprados']
        nivel_ok   = prog2['nivel'] == prog['nivel']
        ok = (cod == 0 and pontos_ok and comprados_ok and nivel_ok)
        _registrar("CT04 carregar_jogo() — recupera estado salvo", ok,
                   "(0, (eco, upg, prog)) idênticos",
                   (cod, pontos_ok, comprados_ok, nivel_ok))
    except Exception as e:
        _registrar("CT04 carregar_jogo() — recupera estado salvo", False,
                   "(0, (eco, upg, prog))", str(e))
    finally:
        _teardown(tmp)

# ---------------------------------------------------------------------------
# CT05 — carregar_jogo: geradores preservados após salvar/carregar
# ---------------------------------------------------------------------------
def test_ct05():
    tmp = _setup()
    try:
        eco, upg, prog = _estados_padrao()
        persistencia.salvar_jogo(eco, upg, prog)
        _, dados = persistencia.carregar_jogo()
        eco2, _, _ = dados
        _, qtd = economia.obter_quantidade_gerador(eco2, 'mineradora_vermelha')
        ok = (qtd == 1)
        _registrar("CT05 carregar_jogo() — quantidade de geradores preservada", ok,
                   "qtd=1", qtd)
    except Exception as e:
        _registrar("CT05 carregar_jogo() — quantidade de geradores preservada", False,
                   "qtd=1", str(e))
    finally:
        _teardown(tmp)

# ---------------------------------------------------------------------------
# CT06 — carregar_jogo: retorna -1 com JSON corrompido
# ---------------------------------------------------------------------------
def test_ct06():
    tmp = _setup()
    try:
        # Cria arquivo com conteúdo inválido
        os.makedirs(os.path.dirname(persistencia._ARQUIVO_SAVE), exist_ok=True)
        with open(persistencia._ARQUIVO_SAVE, 'w') as f:
            f.write('{ isso nao e json valido }}}')
        cod, dados = persistencia.carregar_jogo()
        ok = (cod == -1 and dados is None)
        _registrar("CT06 carregar_jogo() — JSON corrompido → -1", ok,
                   "(-1, None)", (cod, dados))
    except Exception as e:
        _registrar("CT06 carregar_jogo() — JSON corrompido → -1", False, "(-1, None)", str(e))
    finally:
        _teardown(tmp)

# ---------------------------------------------------------------------------
# CT07 — carregar_jogo: retorna -1 com JSON sem chaves esperadas
# ---------------------------------------------------------------------------
def test_ct07():
    tmp = _setup()
    try:
        os.makedirs(os.path.dirname(persistencia._ARQUIVO_SAVE), exist_ok=True)
        with open(persistencia._ARQUIVO_SAVE, 'w') as f:
            f.write('{"chave_errada": 42}')
        cod, dados = persistencia.carregar_jogo()
        ok = (cod == -1 and dados is None)
        _registrar("CT07 carregar_jogo() — JSON sem chaves esperadas → -1", ok,
                   "(-1, None)", (cod, dados))
    except Exception as e:
        _registrar("CT07 carregar_jogo() — JSON sem chaves esperadas → -1", False,
                   "(-1, None)", str(e))
    finally:
        _teardown(tmp)

# ---------------------------------------------------------------------------
# CT08 — existe_save: retorna False quando não há arquivo
# ---------------------------------------------------------------------------
def test_ct08():
    tmp = _setup()
    try:
        cod, existe = persistencia.existe_save()
        ok = (cod == 0 and existe is False)
        _registrar("CT08 existe_save() — sem arquivo → False", ok,
                   "(0, False)", (cod, existe))
    except Exception as e:
        _registrar("CT08 existe_save() — sem arquivo → False", False, "(0, False)", str(e))
    finally:
        _teardown(tmp)

# ---------------------------------------------------------------------------
# CT09 — existe_save: retorna True após salvar
# ---------------------------------------------------------------------------
def test_ct09():
    tmp = _setup()
    try:
        eco, upg, prog = _estados_padrao()
        persistencia.salvar_jogo(eco, upg, prog)
        cod, existe = persistencia.existe_save()
        ok = (cod == 0 and existe is True)
        _registrar("CT09 existe_save() — após salvar → True", ok,
                   "(0, True)", (cod, existe))
    except Exception as e:
        _registrar("CT09 existe_save() — após salvar → True", False, "(0, True)", str(e))
    finally:
        _teardown(tmp)

# ---------------------------------------------------------------------------
# CT10 — deletar_save: retorna 0 mesmo sem arquivo
# ---------------------------------------------------------------------------
def test_ct10():
    tmp = _setup()
    try:
        cod, _ = persistencia.deletar_save()
        ok = (cod == 0)
        _registrar("CT10 deletar_save() — arquivo inexistente → 0", ok,
                   "(0, None)", (cod,))
    except Exception as e:
        _registrar("CT10 deletar_save() — arquivo inexistente → 0", False, "(0, None)", str(e))
    finally:
        _teardown(tmp)

# ---------------------------------------------------------------------------
# CT11 — deletar_save: remove o arquivo existente
# ---------------------------------------------------------------------------
def test_ct11():
    tmp = _setup()
    try:
        eco, upg, prog = _estados_padrao()
        persistencia.salvar_jogo(eco, upg, prog)
        cod, _ = persistencia.deletar_save()
        _, existe = persistencia.existe_save()
        ok = (cod == 0 and not existe)
        _registrar("CT11 deletar_save() — remove arquivo existente", ok,
                   "(0, None) e arquivo removido", (cod, existe))
    except Exception as e:
        _registrar("CT11 deletar_save() — remove arquivo existente", False,
                   "(0, None)", str(e))
    finally:
        _teardown(tmp)

# ---------------------------------------------------------------------------
# CT12 — salvar + carregar: multiplicador e expoente preservados
# ---------------------------------------------------------------------------
def test_ct12():
    tmp = _setup()
    try:
        eco, upg, prog = _estados_padrao()
        _, eco  = economia.aplicar_multiplicador_revolucao(eco, 4)
        _, eco  = economia.aplicar_expoente_ascensao(eco, 2)
        persistencia.salvar_jogo(eco, upg, prog)
        _, dados = persistencia.carregar_jogo()
        eco2, _, _ = dados
        _, mult = economia.obter_multiplicador_revolucao(eco2)
        _, exp  = economia.obter_expoente_ascensao(eco2)
        ok = (abs(mult - eco['multiplicador_revolucao']) < 1e-9 and
              abs(exp  - eco['expoente_ascensao'])       < 1e-9)
        _registrar("CT12 salvar/carregar — multiplicador e expoente preservados", ok,
                   f"mult={eco['multiplicador_revolucao']:.2f} exp={eco['expoente_ascensao']:.2f}",
                   (mult, exp))
    except Exception as e:
        _registrar("CT12 salvar/carregar — multiplicador e expoente preservados", False,
                   "(mult, exp) iguais", str(e))
    finally:
        _teardown(tmp)

# ---------------------------------------------------------------------------
# CT13 — salvar + carregar: upgrades comprados preservados
# ---------------------------------------------------------------------------
def test_ct13():
    tmp = _setup()
    try:
        eco, upg, prog = _estados_padrao()
        _, eco  = economia.adicionar_pontos(eco, 1e6)
        _, upg, eco = upgrades.comprar_upgrade(upg, eco, 'upgrade_mineradora_vermelha_x2')
        persistencia.salvar_jogo(eco, upg, prog)
        _, dados = persistencia.carregar_jogo()
        _, upg2, _ = dados
        ok = ('upgrade_mineradora_vermelha_x2' in upg2['comprados'])
        _registrar("CT13 salvar/carregar — upgrades comprados preservados", ok,
                   "upgrade na lista comprados", upg2['comprados'])
    except Exception as e:
        _registrar("CT13 salvar/carregar — upgrades comprados preservados", False,
                   "upgrade na lista", str(e))
    finally:
        _teardown(tmp)

# ---------------------------------------------------------------------------
# CT14 — salvar + deletar + carregar: retorna -1 após deletar
# ---------------------------------------------------------------------------
def test_ct14():
    tmp = _setup()
    try:
        eco, upg, prog = _estados_padrao()
        persistencia.salvar_jogo(eco, upg, prog)
        persistencia.deletar_save()
        cod, dados = persistencia.carregar_jogo()
        ok = (cod == -1 and dados is None)
        _registrar("CT14 salvar+deletar+carregar — retorna -1 após deletar", ok,
                   "(-1, None)", (cod, dados))
    except Exception as e:
        _registrar("CT14 salvar+deletar+carregar — retorna -1 após deletar", False,
                   "(-1, None)", str(e))
    finally:
        _teardown(tmp)

# ---------------------------------------------------------------------------
# Relatório
# ---------------------------------------------------------------------------
def _relatorio():
    print("\n" + "=" * 60)
    print("RELATÓRIO — test_persistencia.py")
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
        test_ct11, test_ct12, test_ct13, test_ct14,
    ]
    for t in testes:
        t()
    ok = _relatorio()
    exit(0 if ok else 1)
