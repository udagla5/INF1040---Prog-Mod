# Revolution Idle — INF1040 · 2026.1 · Grupo 3WB

Versão simplificada do jogo incremental *Revolution Idle* em Python procedural puro.

## Integrantes

| Nome | Módulo responsável | Branch |
|------|--------------------|--------|
| Nicholas Esteves Ferreira | `main.py`, `gui.py`, `persistencia.py`, `constantes.py` | `feat/main-persistencia` |
| Rafael Carvalho Solberg | `economia.py` | `feat/economia` |
| David Pinto Coelho Benech | `upgrades.py` | `feat/upgrades` |
| Leonardo Dana Edelsberg | `progresso.py` | `feat/progresso` |
| Carlos Eduardo Pimentel Bernardo | `display.py` | `feat/display` |

---

## Como executar

```bash
# Clonar e entrar na pasta
git clone https://github.com/<org>/revolution-idle.git
cd revolution-idle

# Modo terminal (turn-based — recursos acumulam enquanto você lê)
python main.py

# Modo janela gráfica (real-time — atualiza sozinho a cada 500ms)
python gui.py

# Rodar todos os testes
python test_economia.py
python test_upgrades.py
python test_progresso.py
python test_display.py
```

> Requer Python 3.10+. Nenhuma dependência externa — apenas stdlib.

---

## Diferença entre os modos

| | `python main.py` | `python gui.py` |
|---|---|---|
| Interface | Terminal | Janela tkinter |
| Atualização | Ao pressionar Enter | Automática (500ms) |
| Input | `input()` bloqueante | Campo de texto na janela |
| Efeito idle | Acumula entre comandos | Cresce em tempo real |
| Compatibilidade | Qualquer terminal | Requer display gráfico |

**Dica modo terminal:** pressione Enter sem digitar nada para ver os recursos acumulados.

---

## Estrutura de arquivos

```
revolution-idle/
├── main.py               # Modo terminal (turn-based)
├── gui.py                # Modo janela gráfica (tkinter real-time)
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
| `revolucao` | Executa Revolução (se elegível) |
| `ascensao` | Executa Ascensão (se elegível) |
| `novo jogo` | Apaga o save e reinicia |
| `ajuda` | Exibe os comandos disponíveis |
| `sair` | Salva e encerra |

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

## Fluxo de trabalho no GitHub

### 1. Criar sua branch
```bash
git checkout main && git pull origin main
git checkout -b feat/<seu-modulo>
```

### 2. Implementar e testar
```bash
python test_<seu_modulo>.py
# Deve finalizar com: Falhou: 0
```

### 3. Abrir Pull Request para `main`
- Use o template automático de PR
- CI roda os 4 testadores automaticamente
- PR aprovado somente com CI verde + revisão do CODEOWNER

### 4. Configurar proteção da branch `main`
Settings → Branches → Add rule → `main`:
- ✅ Require pull request before merging
- ✅ Require status checks to pass → selecionar `testes`
- ✅ Require review from Code Owners

---

## Mecânicas do jogo

| Mecânica | Descrição |
|----------|-----------|
| **Geradores** | 40 tipos (10 Mineradoras, 10 Fábricas, 10 Usinas, 10 Laboratórios) |
| **Upgrades** | 120 total — ×2, ×5, ×10 por gerador |
| **Revolução** | Reseta a run, ganha cristais → multiplica produção global |
| **Ascensão** | Após 10 revoluções, ganha fragmentos → eleva produção a expoente |
| **Vitória** | Atingir 1×10⁵⁰ pontos (Ponto Ômega) |

---

## Critérios de avaliação

| Critério | Pontos |
|----------|--------|
| Aplicação funcionando | 2,0 |
| Testes automatizados completos sem erro | 2,0 |
| Especificação completa das funções | 2,0 |
| Modularização de TADs (encapsulamento correto) | 3,0 |
| Persistência entre execuções | 1,0 |
| **Total** | **10,0** |
