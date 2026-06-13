# Revolution Idle — INF1040 - 2026.1 - Grupo 2

Versão simplificada do jogo incremental *Revolution Idle* em Python procedural puro.

## Integrantes

| Nome | Módulo responsável |
|------|--------------------|
| Nicholas Esteves Ferreira | `main_console.py` |
| Rafael Carvalho Solberg | `economia.py` |
| David Pinto Coelho Benech | `upgrades.py` |
| Leonardo Dana Edelsberg | `progresso.py` |
| Carlos Eduardo Pimentel Bernardo | `display.py`, `constantes.py` |
| Igor Oliveira de Mello | `main_pygame.py`, `persistencia.py` |

---

## Como executar

```bash
# Clonar e entrar na pasta
git clone https://github.com/<org>/revolution-idle.git
cd revolution-idle

# Instalar dependência (apenas para o modo pygame)
pip install pygame

# Modo terminal (turn-based)
python main_console.py

# Modo janela pygame (tempo real, 60 fps)
python main_pygame.py

# Rodar todos os testes
python test_economia.py
python test_upgrades.py
python test_progresso.py
python test_display.py
python test_persistencia.py
python test_main_console.py
```

> Requer Python 3.10+. `pygame` é a única dependência externa (apenas para `main_pygame.py`).

---

## Diferença entre os modos

| | `python main_console.py` | `python main_pygame.py` |
|---|---|---|
| Interface | Terminal | Janela pygame |
| Atualização | Ao pressionar Enter | Automática (60 fps) |
| Input | `input()` bloqueante | Cliques e botões na tela |
| Efeito idle | Acumula entre comandos | Cresce em tempo real |
| Compatibilidade | Qualquer terminal | Requer pygame instalado |

**Dica modo terminal:** pressione Enter sem digitar nada para ver os recursos acumulados.

---

## Estrutura de arquivos

```
revolution-idle/
├── main_console.py       # Modo terminal (turn-based)
├── main_pygame.py        # Modo pygame (tempo real, arquivo único)
├── economia.py           # TAD Economia — pontos e geradores
├── upgrades.py           # TAD Upgrades — catálogo e compras
├── progresso.py          # TAD Progresso — nível, marcos, resets
├── display.py            # TAD Display — formatação de strings
├── persistencia.py       # Salvar/carregar em JSON (único módulo com I/O de arquivo)
├── constantes.py         # Catálogos e constantes do jogo
├── test_economia.py      # 39 testes de economia.py
├── test_upgrades.py      # 22 testes de upgrades.py
├── test_progresso.py     # 28 testes de progresso.py
├── test_display.py       # 27 testes de display.py
├── test_persistencia.py  # 14 testes de persistencia.py
├── test_main_console.py  # 20 testes de main_console.py
├── saves/
│   └── save.json         # Gerado ao fechar o jogo (ignorado pelo git)
└── .github/
    ├── workflows/tests.yml
    ├── PULL_REQUEST_TEMPLATE.md
    └── CODEOWNERS
```

---

## Comandos do jogo

| Comando | Ação |
|---------|------|
| `comprar gerador <id>` | Compra 1 unidade do gerador |
| `comprar upgrade <id>` | Compra o upgrade |
| `listar geradores` | Exibe todos os geradores com quantidades e custos |
| `listar upgrades` | Exibe todos os upgrades com status |
| `status` | Exibe o painel completo |
| `revolucao` | Executa Revolução (se elegível) |
| `ascensao` | Executa Ascensão (se elegível) |
| `novo jogo` | Apaga o save e reinicia |
| `ajuda` | Exibe os comandos disponíveis |
| `sair` / `salvar e sair` | Salva e encerra |

> Os comandos acima funcionam no modo terminal (`main_console.py`). No modo pygame, as mesmas ações são executadas pelos botões na tela.

### Exemplos de IDs de geradores
```
mineradora_vermelha   mineradora_laranja   mineradora_amarela
fabrica_vermelha      fabrica_laranja      fabrica_amarela
usina_vermelha        usina_laranja        (após 1ª revolução:)
laboratorio_vermelho  laboratorio_laranja
```

### Exemplos de IDs de upgrades
```
upgrade_mineradora_vermelha_x2
upgrade_mineradora_vermelha_x5
upgrade_mineradora_vermelha_x10
upgrade_fabrica_vermelha_x2
```

---

## Mecânicas do jogo

| Mecânica | Descrição |
|----------|-----------|
| **Geradores** | 40 tipos (10 Mineradoras, 10 Fábricas, 10 Usinas, 10 Laboratórios) |
| **Upgrades** | 120 total — ×2, ×5, ×10 por gerador |
| **Revolução** | Reseta a run, ganha cristais → multiplica produção global |
| **Ascensão** | Após 10 revoluções, ganha fragmentos → eleva produção a expoente |
| **Vitória** | Atingir 1×10⁵⁰ pontos (Ponto Ômega) |

