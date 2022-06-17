import pandas as pd

# Carregar listagem com a base de palavras do Instituto de Matemática e Estatística Universidade de São Paulo (IME-USP)
palavras = pd.read_csv('https://www.ime.usp.br/~pf/dicios/br-utf8.txt', header=None)[0]

# Adicionar o nome da empresa
nomes = pd.DataFrame(['Lutscher'])
# Adicionar os produtos do catálogo da empresa
produtos = pd.DataFrame(['Chupscher', 'DulCacau', 'Marsher'])

# Limpeza de palavras que devem ser evitadas
palavras_limpas = palavras[
    # Remoção de referências com diabo ou diabetes
    ~palavras.str.startswith('diab') &
    # Remoção de referências com tristeza
    ~palavras.str.startswith('trist') &
    # Remoção de referências com diabo ou diabetes
    ~palavras.str.startswith('amarg')
]

# Adicionar na empresa para a listagem de palavras
nova_listagem = pd.concat([palavras_limpas, nomes, produtos])

# Salvar listagem de palavras tratadas 
nova_listagem.to_csv('./data/palavras.csv', header=False, index=False)
