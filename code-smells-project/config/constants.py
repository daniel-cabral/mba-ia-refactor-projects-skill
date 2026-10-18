API_VERSION = "1.0.0"

CATEGORIAS_VALIDAS = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]
NOME_PRODUTO_MIN = 2
NOME_PRODUTO_MAX = 200

STATUS_PEDIDO = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]
STATUS_INICIAL_PEDIDO = "pendente"
STATUS_CANCELADO = "cancelado"
TRANSICOES_STATUS = {
    "pendente": ["aprovado", "cancelado"],
    "aprovado": ["enviado", "cancelado"],
    "enviado": ["entregue"],
    "entregue": [],
    "cancelado": [],
}

# (faturamento minimo exclusivo, percentual de desconto), do maior para o menor
FAIXAS_DESCONTO = [(10000, 0.10), (5000, 0.05), (1000, 0.02)]

TIPO_USUARIO_PADRAO = "cliente"

DEFAULT_PAGE_SIZE = 100
MAX_PAGE_SIZE = 100
