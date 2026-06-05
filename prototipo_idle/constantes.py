# =============================================================================
# constantes.py — Dados e constantes globais do jogo
# INF1040 · 2026.1 · Grupo 3WB
# Não é um TAD — é um módulo de configuração. Pode ser importado livremente.
# =============================================================================

# ---------------------------------------------------------------------------
# Constantes numéricas globais
# ---------------------------------------------------------------------------
ESCALA_CUSTO_GERADOR    = 1.15        # custo cresce 15% por unidade comprada
MULT_POR_CRISTAL        = 0.5         # +50% produção por cristal de revolução
EXP_POR_FRAGMENTO       = 0.15        # expoente += 0.15 por fragmento de ascensão
REVOLUCOES_P_ASCENSAO   = 10          # revoluções necessárias para ascender
LIMIAR_REVOLUCAO_BASE   = 1_000_000.0 # pontos mínimos para 1ª revolução
FATOR_LIMIAR_REVOLUCAO  = 10.0        # limiar multiplica a cada revolução
PONTO_OMEGA             = 1e50        # condição de vitória
DELTA_TICK              = 0.1         # segundos por tick (100 ms)

# ---------------------------------------------------------------------------
# Catálogo de geradores (40 total)
# Formato: (id, nome, custo_base, prod_base, categoria, bloqueado)
# ---------------------------------------------------------------------------
_DADOS_GERADORES = [
    # Mineradoras
    ('mineradora_vermelha',    'Mineradora Vermelha',    10,      0.1,     'mineradora',   False),
    ('mineradora_laranja',     'Mineradora Laranja',     150,     1.0,     'mineradora',   False),
    ('mineradora_amarela',     'Mineradora Amarela',     2_000,   12.0,    'mineradora',   False),
    ('mineradora_verde',       'Mineradora Verde',       25_000,  150.0,   'mineradora',   False),
    ('mineradora_ciana',       'Mineradora Ciana',       3e5,     2_000.0, 'mineradora',   False),
    ('mineradora_azul',        'Mineradora Azul',        4e6,     25_000.0,'mineradora',   False),
    ('mineradora_violeta',     'Mineradora Violeta',     5e7,     3e5,     'mineradora',   False),
    ('mineradora_rosa',        'Mineradora Rosa',        6e8,     4e6,     'mineradora',   False),
    ('mineradora_branca',      'Mineradora Branca',      8e9,     5e7,     'mineradora',   False),
    ('mineradora_arco_iris',   'Mineradora Arco-íris',   1e11,    6e8,     'mineradora',   False),
    # Fábricas
    ('fabrica_vermelha',       'Fábrica Vermelha',       500,     3.0,     'fabrica',      False),
    ('fabrica_laranja',        'Fábrica Laranja',        7_500,   36.0,    'fabrica',      False),
    ('fabrica_amarela',        'Fábrica Amarela',        1e5,     450.0,   'fabrica',      False),
    ('fabrica_verde',          'Fábrica Verde',          1.5e6,   5_500.0, 'fabrica',      False),
    ('fabrica_ciana',          'Fábrica Ciana',          2e7,     70_000.0,'fabrica',      False),
    ('fabrica_azul',           'Fábrica Azul',           3e8,     9e5,     'fabrica',      False),
    ('fabrica_violeta',        'Fábrica Violeta',        4e9,     1.1e7,   'fabrica',      False),
    ('fabrica_rosa',           'Fábrica Rosa',           5e10,    1.4e8,   'fabrica',      False),
    ('fabrica_branca',         'Fábrica Branca',         7e11,    1.8e9,   'fabrica',      False),
    ('fabrica_arco_iris',      'Fábrica Arco-íris',      1e13,    2.3e10,  'fabrica',      False),
    # Usinas
    ('usina_vermelha',         'Usina Vermelha',         1e4,     100.0,   'usina',        False),
    ('usina_laranja',          'Usina Laranja',          1.5e5,   1_200.0, 'usina',        False),
    ('usina_amarela',          'Usina Amarela',          2e6,     15_000.0,'usina',        False),
    ('usina_verde',            'Usina Verde',            3e7,     1.8e5,   'usina',        False),
    ('usina_ciana',            'Usina Ciana',            4e8,     2.2e6,   'usina',        False),
    ('usina_azul',             'Usina Azul',             5e9,     2.8e7,   'usina',        False),
    ('usina_violeta',          'Usina Violeta',          7e10,    3.5e8,   'usina',        False),
    ('usina_rosa',             'Usina Rosa',             9e11,    4.5e9,   'usina',        False),
    ('usina_branca',           'Usina Branca',           1.2e13,  5.8e10,  'usina',        False),
    ('usina_arco_iris',        'Usina Arco-íris',        1.6e14,  7.5e11,  'usina',        False),
    # Laboratórios — bloqueados até 1ª revolução
    ('laboratorio_vermelho',   'Laboratório Vermelho',   1e6,     8_000.0, 'laboratorio',  True),
    ('laboratorio_laranja',    'Laboratório Laranja',    2e7,     1e5,     'laboratorio',  True),
    ('laboratorio_amarelo',    'Laboratório Amarelo',    3e8,     1.3e6,   'laboratorio',  True),
    ('laboratorio_verde',      'Laboratório Verde',      4e9,     1.7e7,   'laboratorio',  True),
    ('laboratorio_ciano',      'Laboratório Ciano',      6e10,    2.2e8,   'laboratorio',  True),
    ('laboratorio_azul',       'Laboratório Azul',       8e11,    2.9e9,   'laboratorio',  True),
    ('laboratorio_violeta',    'Laboratório Violeta',    1e13,    3.8e10,  'laboratorio',  True),
    ('laboratorio_rosa',       'Laboratório Rosa',       1.5e14,  5e11,    'laboratorio',  True),
    ('laboratorio_branco',     'Laboratório Branco',     2e15,    6.5e12,  'laboratorio',  True),
    ('laboratorio_arco_iris',  'Laboratório Arco-íris',  3e16,    8.5e13,  'laboratorio',  True),
]

GERADORES_CATALOGO = {
    id_: {
        'id':        id_,
        'nome':      nome,
        'custo_base': custo,
        'prod_base': prod,
        'categoria': cat,
        'bloqueado': bloq,
    }
    for id_, nome, custo, prod, cat, bloq in _DADOS_GERADORES
}

# ---------------------------------------------------------------------------
# Catálogo de upgrades — gerado automaticamente (40 × 3 = 120)
# ---------------------------------------------------------------------------
_FATORES_UPGRADES = [
    ('x2',  2.0,   10.0),   # (sufixo, fator_producao, mult_custo)
    ('x5',  5.0,   50.0),
    ('x10', 10.0, 200.0),
]

def _gerar_upgrades():
    resultado = {}
    for id_ger, dados in GERADORES_CATALOGO.items():
        for sufixo, fator, mult_custo in _FATORES_UPGRADES:
            uid = f'upgrade_{id_ger}_{sufixo}'
            resultado[uid] = {
                'id':    uid,
                'nome':  f'{dados["nome"]} ({sufixo.upper()})',
                'alvo':  id_ger,
                'custo': dados['custo_base'] * mult_custo,
                'fator': fator,
            }
    return resultado

UPGRADES_CATALOGO = _gerar_upgrades()

# ---------------------------------------------------------------------------
# Marcos de progresso
# ---------------------------------------------------------------------------
MARCOS_CATALOGO = [
    {'id': 'marco_1k',         'descricao': 'Acumule 1.000 pontos',          'limiar': 1e3,  'tipo': 'pontos'},
    {'id': 'marco_10k',        'descricao': 'Acumule 10.000 pontos',         'limiar': 1e4,  'tipo': 'pontos'},
    {'id': 'marco_100k',       'descricao': 'Acumule 100.000 pontos',        'limiar': 1e5,  'tipo': 'pontos'},
    {'id': 'marco_1m',         'descricao': 'Acumule 1 Milhão de pontos',    'limiar': 1e6,  'tipo': 'pontos'},
    {'id': 'marco_10m',        'descricao': 'Acumule 10 Milhões de pontos',  'limiar': 1e7,  'tipo': 'pontos'},
    {'id': 'marco_1b',         'descricao': 'Acumule 1 Bilhão de pontos',    'limiar': 1e9,  'tipo': 'pontos'},
    {'id': 'marco_1t',         'descricao': 'Acumule 1 Trilhão de pontos',   'limiar': 1e12, 'tipo': 'pontos'},
    {'id': 'marco_1qa',        'descricao': 'Acumule 1 Quadrilhão',          'limiar': 1e15, 'tipo': 'pontos'},
    {'id': 'marco_1qi',        'descricao': 'Acumule 1 Quintilhão',          'limiar': 1e18, 'tipo': 'pontos'},
    {'id': 'marco_revolucao',  'descricao': 'Execute sua 1ª Revolução',      'limiar': None, 'tipo': 'evento'},
    {'id': 'marco_ascensao',   'descricao': 'Execute sua 1ª Ascensão',       'limiar': None, 'tipo': 'evento'},
    {'id': 'marco_laboratorio','descricao': 'Construa seu 1º Laboratório',   'limiar': None, 'tipo': 'evento'},
    {'id': 'marco_omega',      'descricao': 'Atinja o Ponto Ômega! (1e50)',  'limiar': 1e50, 'tipo': 'pontos'},
]

# ---------------------------------------------------------------------------
# Limiares de nível (índice = nível-1, valor = pontos necessários)
# ---------------------------------------------------------------------------
LIMIARES_NIVEL = [0, 1e3, 1e4, 1e5, 1e6, 1e8, 1e10, 1e12, 1e15, 1e20]
NIVEL_MAXIMO   = len(LIMIARES_NIVEL)

# ---------------------------------------------------------------------------
# Categorias na ordem de exibição
# ---------------------------------------------------------------------------
CATEGORIAS_ORDEM = ['mineradora', 'fabrica', 'usina', 'laboratorio']
