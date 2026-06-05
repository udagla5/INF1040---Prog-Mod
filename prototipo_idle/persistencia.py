# =============================================================================
# persistencia.py — Persistência de dados entre execuções
# Responsável: Nicholas Esteves Ferreira
# INF1040 · 2026.1 · Grupo 3WB
#
# ÚNICO módulo que lê/escreve arquivos.
# Os TADs (economia, upgrades, progresso) NÃO acessam arquivos.
# main.py chama carregar_jogo() no início e salvar_jogo() no encerramento.
# =============================================================================

import json
import os

__all__ = [
    'salvar_jogo',
    'carregar_jogo',
    'existe_save',
    'deletar_save',
]

_ARQUIVO_SAVE = os.path.join('saves', 'save.json')

# ---------------------------------------------------------------------------
# Interface pública
# ---------------------------------------------------------------------------

def salvar_jogo(estado_eco, estado_upg, estado_prog):
    """
    Grava o estado completo do jogo em arquivo JSON.

    Parâmetros:
        estado_eco  (dict) — estado retornado por economia
        estado_upg  (dict) — estado retornado por upgrades
        estado_prog (dict) — estado retornado por progresso

    Retornos:
        ( 0, None) — sucesso
        (-1, None) — erro ao gravar (ex: sem permissão)
    """
    try:
        os.makedirs('saves', exist_ok=True)
        dados = {
            'estado_eco':  estado_eco,
            'estado_upg':  estado_upg,
            'estado_prog': estado_prog,
        }
        with open(_ARQUIVO_SAVE, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        return (0, None)
    except Exception:
        return (-1, None)

def carregar_jogo():
    """
    Lê o estado salvo do arquivo JSON.

    Retornos:
        ( 0, (dict_eco, dict_upg, dict_prog)) — sucesso
        (-1, None)                             — arquivo não encontrado ou corrompido
    """
    try:
        if not os.path.isfile(_ARQUIVO_SAVE):
            return (-1, None)
        with open(_ARQUIVO_SAVE, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        eco  = dados['estado_eco']
        upg  = dados['estado_upg']
        prog = dados['estado_prog']
        return (0, (eco, upg, prog))
    except Exception:
        return (-1, None)

def existe_save():
    """
    Verifica se existe um arquivo de save.

    Retornos:
        (0, True ) — save encontrado
        (0, False) — sem save
    """
    return (0, os.path.isfile(_ARQUIVO_SAVE))

def deletar_save():
    """
    Remove o arquivo de save (usado para novo jogo).

    Retornos:
        ( 0, None) — sucesso ou arquivo já inexistente
        (-1, None) — erro ao deletar
    """
    try:
        if os.path.isfile(_ARQUIVO_SAVE):
            os.remove(_ARQUIVO_SAVE)
        return (0, None)
    except Exception:
        return (-1, None)
