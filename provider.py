# Importação de biblioteca de serialização
import pickle
# Importação de biblioteca para lidar com APIs
from fastapi import FastAPI
# Biblioteca de validação de tipos
from pydantic import BaseModel
# Biblioteca para possibilitar uso nulo para tipos
from typing import Union
# Importar biblioteca de processamento linguagem natural
import spacy
# Importar Pandas - biblioteca para manipulação de datasets
import pandas as pd
# Bilbioteca de
from datetime import datetime

# Iniciar instância para lidar com API
app = FastAPI()

# Carregar tokenização e treinamento em português
nlp = spacy.load('pt_core_news_lg')

# Carregar o arquivo com o modelo gerado, vetorizador e dicionário de palavras
loaded_model = pickle.load(open('./data/model_selected.sav', 'rb'))
vectorizer = pickle.load(open('./data/vectorizer.sav', 'rb'))
dicionario = pd.read_csv('./data/palavras.csv', header=None)


def lematizar(list):
    # Definição de classes gramaticais Substantivos, Verbos, Advérbios e Adjetivos
    classe_gramatical = ['NOUN', 'VERB', 'ADV', 'ADJ']
    # Criar listagem de lematização
    lema = []
    # Loop para criação das frases lematizadas
    for frase in list:
        doc = nlp(frase)
        spacy_lema = [
            token.lemma_ for token in doc if token.pos_ in classe_gramatical]
        lema.append(' '.join(spacy_lema))
    # Retornar frase lematizzada
    return lema


def analizar_frase(texto, modelo):
    # Lematizar o texto recebido
    lematizada = lematizar([texto])
    # Vetorizar o texto lemaizado
    vetorizada = vectorizer.transform(lematizada).toarray()
    # Realizar predição modelo oferecido
    predicao = modelo.predict(vetorizada)
    # Retornar a análise da frase
    return predicao[0]


def marcar_palavras_desaconselhadas(texto):
    result = []
    for word in texto.split():
        if word.lower() in dicionario.values:
            result.append(word)
        else:
            result.append('<notfound>' + word + '</notfound>')
    return " ".join(result)


class Item(BaseModel):
    frase: str
    classificacao: Union[str, None] = None
    data_resposta: Union[datetime, None] = None


@app.get("/")
def check_healthy():
    return "Funcionando"


@app.post("/")
def check_phase(item: Item):
    item.classificacao = analizar_frase(item.frase, loaded_model)
    item.data_resposta = datetime.today()
    item.frase = marcar_palavras_desaconselhadas(item.frase)

    return item
