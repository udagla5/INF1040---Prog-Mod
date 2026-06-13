# =============================================================================
# main.py — Orquestrador (modo terminal, turn-based com acúmulo de tempo)
# Responsável: Nicholas Esteves Ferreira
# INF1040 - 2026.1 - Grupo 2
# =============================================================================

import time
import os

import economia
import upgrades
import progresso
import display
import persistencia
from constantes import DELTA_TICK

# ---------------------------------------------------------------------------
# Funções internas
# ---------------------------------------------------------------------------
def _limpar_tela():
    """
    Limpa o terminal (cls no Windows, clear no Unix).

    Assertiva de entrada:
        (nenhuma)

    Assertiva de saída:
        (nenhuma) — efeito colateral: terminal limpo; sem valor de retorno
    """
    os.system('cls' if os.name == 'nt' else 'clear')

def processar_comando(cmd, estado_eco, estado_upg, estado_prog):
    """
    Interpreta e executa o comando digitado pelo jogador.

    Assertiva de entrada:
        cmd        (str)  — string de entrada do usuário (pode ser vazia)
        estado_eco  (dict) — estado válido retornado por economia.inicializar_estado
        estado_upg  (dict) — estado válido retornado por upgrades.inicializar_upgrades
        estado_prog (dict) — estado válido retornado por progresso.inicializar_progresso

    Assertiva de saída:
        ( 0, eco, upg, prog, str) — comando executado com sucesso; estados podem
                                    ter sido modificados; str é mensagem de feedback
        (-1, eco, upg, prog, str) — comando inválido ou operação recusada;
                                    estados originais preservados; str descreve o erro
    """
    partes = cmd.strip().lower().split()
    if not partes:
        return (0, estado_eco, estado_upg, estado_prog, "")

    # comprar gerador <id>
    if len(partes) == 3 and partes[0] == 'comprar' and partes[1] == 'gerador':
        id_ger = partes[2]
        cod, custo = economia.calcular_custo_gerador(estado_eco, id_ger)
        if cod == -1:
            return (-1, estado_eco, estado_upg, estado_prog,
                    f"[ERRO] Gerador '{id_ger}' não encontrado.")
        if cod == -4:
            return (-1, estado_eco, estado_upg, estado_prog,
                    f"[ERRO] '{id_ger}' bloqueado. Complete uma Revolução.")
        _, pode = economia.pode_gastar(estado_eco, custo)
        _, cs   = display.formatar_numero(custo)
        if not pode:
            return (-1, estado_eco, estado_upg, estado_prog,
                    f"[ERRO] Pontos insuficientes. Custo: {cs}")
        _, eco = economia.gastar_pontos(estado_eco, custo)
        _, eco = economia.adicionar_gerador(eco, id_ger)
        return (0, eco, estado_upg, estado_prog,
                f"[OK] '{id_ger}' comprado por {cs} pontos!")

    # comprar upgrade <id>
    if len(partes) == 3 and partes[0] == 'comprar' and partes[1] == 'upgrade':
        id_upg = partes[2]
        cod, upg_n, eco_n = upgrades.comprar_upgrade(estado_upg, estado_eco, id_upg)
        msgs = {
             0: "[OK] Upgrade comprado!",
            -1: "[ERRO] Upgrade não encontrado.",
            -2: "[ERRO] Pontos insuficientes.",
            -3: "[ERRO] Upgrade já comprado.",
        }
        msg = msgs.get(cod, "[ERRO] Falha.")
        if cod == 0:
            return (0, eco_n, upg_n, estado_prog, msg)
        return (-1, estado_eco, estado_upg, estado_prog, msg)

    # revolucao
    if partes[0] == 'revolucao':
        cod, eco_n, prog_n = progresso.executar_revolucao(estado_eco, estado_prog)
        if cod == 0:
            return (0, eco_n, estado_upg, prog_n,
                    "[REVOLUÇÃO] Run resetada! Multiplicador atualizado.")
        return (-1, estado_eco, estado_upg, estado_prog,
                "[ERRO] Pontos insuficientes para Revolução.")

    # ascensao
    if partes[0] == 'ascensao':
        cod, eco_n, prog_n = progresso.executar_ascensao(estado_eco, estado_prog)
        if cod == 0:
            return (0, eco_n, estado_upg, prog_n,
                    "[ASCENSÃO] Jogo resetado! Expoente atualizado.")
        return (-1, estado_eco, estado_upg, estado_prog,
                "[ERRO] Revoluções insuficientes para Ascensão.")

    # listar geradores
    if len(partes) == 2 and partes[0] == 'listar' and partes[1] == 'geradores':
        _, texto = display.renderizar_geradores(estado_eco, estado_upg)
        return (0, estado_eco, estado_upg, estado_prog, texto)

    # listar upgrades
    if len(partes) == 2 and partes[0] == 'listar' and partes[1] == 'upgrades':
        _, texto = display.renderizar_upgrades(estado_upg, estado_eco)
        return (0, estado_eco, estado_upg, estado_prog, texto)

    # status
    if partes[0] == 'status':
        _, texto = display.renderizar_painel(estado_eco, estado_upg, estado_prog)
        return (0, estado_eco, estado_upg, estado_prog, texto)

    # novo jogo — reinicia apenas na memória; o arquivo só é sobrescrito ao sair
    if len(partes) == 2 and partes[0] == 'novo' and partes[1] == 'jogo':
        _, eco  = economia.inicializar_estado()
        _, upg  = upgrades.inicializar_upgrades()
        _, prog = progresso.inicializar_progresso()
        _, eco  = economia.adicionar_gerador(eco, 'mineradora_vermelha')
        _, eco  = economia.adicionar_gerador(eco, 'mineradora_vermelha')
        return (0, eco, upg, prog, "[OK] Novo jogo iniciado! O save anterior será sobrescrito ao sair.")

    return (-1, estado_eco, estado_upg, estado_prog,
            f"[ERRO] Comando desconhecido: '{cmd}'. Digite 'ajuda'.")

def _mostrar_ajuda():
    """
    Retorna a string com todos os comandos disponíveis para o jogador.

    Assertiva de entrada:
        (nenhuma)

    Assertiva de saída:
        str — texto multilinha com comandos, sintaxe e dica de uso;
              sem código de retorno (não segue padrão TAD, função auxiliar de UI)
    """
    return (
        "\n"
        "  Comandos disponíveis:\n"
        "  comprar gerador <id>   ex: comprar gerador mineradora_laranja\n"
        "  comprar upgrade <id>   ex: comprar upgrade upgrade_mineradora_vermelha_x2\n"
        "  revolucao              executa a Revolução (se elegível)\n"
        "  ascensao               executa a Ascensão (se elegível)\n"
        "  novo jogo              apaga o save e reinicia\n"
        "  ajuda                  exibe esta mensagem\n"
        "  salvar e sair          salva e encerra\n"
        "\n"
        "  [Dica] Pressione Enter sem digitar nada para atualizar o painel."
    )

def _loop_principal():
    """
    Loop principal do modo terminal: carrega save, roda ticks e processa comandos.

    Assertiva de entrada:
        (nenhuma) — arquivo saves/save.json pode ou não existir

    Assertiva de saída:
        (nenhuma) — função bloqueante; encerra ao comando 'sair' ou Ctrl+C;
                    salva o estado antes de encerrar
    """
    # ─── Carregar ou inicializar ──────────────────────────────────────────
    cod, dados = persistencia.carregar_jogo()
    if cod == 0:
        eco, upg, prog = dados
        msg_feedback   = "  [SAVE] Jogo carregado com sucesso!"
    else:
        _, eco  = economia.inicializar_estado()
        _, upg  = upgrades.inicializar_upgrades()
        _, prog = progresso.inicializar_progresso()
        # Mineradora inicial gratuita para o jogador começar com renda passiva
        _, eco  = economia.adicionar_gerador(eco, 'mineradora_vermelha')
        _, eco  = economia.adicionar_gerador(eco, 'mineradora_vermelha')
        msg_feedback = (
            "  Bem-vindo ao Revolution Idle!\n"
            "  Você recebeu 2 Mineradoras Vermelhas gratuitas (+0.2 pts/s).\n"
            "  Em ~2 minutos você poderá comprar sua próxima.\n"
            "  Pressione Enter para atualizar ou digite um comando."
        )

    ultimo_tempo = time.perf_counter()
    notificacoes = []

    while True:
        # ─── Aplicar tempo decorrido ──────────────────────────────────────
        agora = time.perf_counter()
        delta = agora - ultimo_tempo
        ultimo_tempo = agora

        _, eco           = economia.aplicar_geracao(eco, delta)
        _, fatores       = upgrades.calcular_fatores_por_gerador(upg)
        _, eco           = economia.aplicar_efeitos_upgrades(eco, fatores)
        _, prog, novos   = progresso.verificar_progresso(eco, prog)
        _, prog, vitoria = progresso.verificar_vitoria(eco, prog)

        notificacoes = novos + notificacoes
        if vitoria:
            notificacoes = ["$$$ PONTO ÔMEGA — VITÓRIA! $$$"] + notificacoes
        notificacoes = notificacoes[:5]

        # ─── Renderizar ───────────────────────────────────────────────────
        _limpar_tela()
        _, tela = display.renderizar_painel(eco, upg, prog)
        print(tela)

        if notificacoes:
            print()
            for n in notificacoes:
                print(f"  $ {n}")

        if msg_feedback:
            print(f"\n{msg_feedback}")
            msg_feedback = ""

        # ─── Input ───────────────────────────────────────────────────────
        print()
        try:
            cmd = input("  > ").strip()
        except (KeyboardInterrupt, EOFError):
            cmd = "sair"

        if cmd.lower() in ("sair", "salvar e sair"):
            persistencia.salvar_jogo(eco, upg, prog)
            _limpar_tela()
            print("  Jogo salvo. Até logo!")
            break

        if cmd.lower() == "ajuda":
            msg_feedback = _mostrar_ajuda()
            continue

        if cmd == "":
            continue   # só atualiza o painel

        _, eco, upg, prog, msg = processar_comando(cmd, eco, upg, prog)
        msg_feedback = msg

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    _loop_principal()
