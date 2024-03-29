# -*- coding: utf-8 -*-
"""Desenvolvimento - Analizo.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1I4MM38bhcNceRq5hMrSySKu9uNKdKS20
"""

# Download tokenização e treinamento em português
#!python -m spacy download pt_core_news_lg

# Importar Pandas - biblioteca para manipulação de datasets
import pandas as pd

# Carregar listagem de frases
df_frases = pd.read_csv('./data/frases.csv', encoding='utf-8')

# Visualizar as 5 primeiras linhas
df_frases.head()

# Importar biblioteca de processamento linguagem natural
import spacy
# Carregar tokenização e treinamento em português
nlp = spacy.load('pt_core_news_lg')

def lematizar(list):
  # Definição de classes gramaticais Substantivos, Verbos, Advérbios e Adjetivos
  classe_gramatical = ['NOUN', 'VERB', 'ADV', 'ADJ']

  # Criar listagem de lematização
  lema = []

  # Loop para criação das frases lematizadas
  for frase in list:
      doc = nlp(frase)
      spacy_lema = [token.lemma_ for token in doc if token.pos_ in classe_gramatical]

      lema.append(' '.join(spacy_lema))

  return lema

# Alimentação das listas do corpos das frases e classificações
corpus = df_frases['Texto'].tolist()
classificacoes = df_frases['Classificacao'].tolist()

# Alimentar a lista e dataset com a lematização dos corpos
lematizacao = lematizar(corpus)
df_frases['Lematizacao'] = lematizacao

df_frases.head()

# Importação da biblioteca para vetorização
from sklearn.feature_extraction.text import CountVectorizer

vectorizer = CountVectorizer()
vector_lematizacao = vectorizer.fit_transform(lematizacao)

# Agregação da vetorização para a base
df_frases['Vetorizado'] = vector_lematizacao.toarray().tolist()

# Ver palavras do vetor
print(vectorizer.get_feature_names_out())
# Ver vetorização
print('Formato: ' + str(vector_lematizacao.toarray().shape))

df_frases.head()

# Biblioteca de Separação de Treino/Teste
from sklearn.model_selection import train_test_split

# Separação das frases para treino do modelo e geração de métricas
## Negativas 
negativas = df_frases.query("Classificacao == 'Negativa'")
vector_neg_lematizacao = negativas['Vetorizado'].tolist()
classificacoes_neg = negativas['Classificacao'].tolist()

vector_neg_treino, vector_neg_teste, classificacoes_neg_treino, classificacoes_neg_teste = train_test_split(vector_neg_lematizacao, classificacoes_neg, test_size=0.3, random_state=42)

## Positivas
positivas = df_frases.query("Classificacao == 'Positiva'")
vector_pos_lematizacao = positivas['Vetorizado'].tolist()
classificacoes_pos = positivas['Classificacao'].tolist()

vector_pos_treino, vector_pos_teste, classificacoes_pos_treino, classificacoes_pos_teste = train_test_split(vector_pos_lematizacao, classificacoes_pos, test_size=0.3, random_state=42)

# Concatenar listagem para treino e teste
vector_treino = vector_neg_treino + vector_pos_treino
vector_teste =  vector_neg_teste + vector_pos_teste
classificacoes_treino = classificacoes_neg_treino + classificacoes_pos_treino
classificacoes_teste =  classificacoes_neg_teste + classificacoes_pos_teste

# Biblioteca de Métricas
from sklearn import metrics

# Frases de amostra  que estão no dicionário
frases_amostra = [
    'Sua confeitaria a todo momento',
    'Sobremesa para alegrar o dia',
    'Brigar por doce, pode'
  ]

# Coleção de métricas do modelo
resultado_metricas = pd.DataFrame(data={
    'Name': [], 'Accuracy': [], 'Precision': [], 
    'Recall': [], 'F1 Score': [], 'Classifier': []})

# Geração da análise por frases
def analizar_frase(texto, modelo):
  # Lematizar o texto recebido
  lematizada = lematizar([texto])

  # Vetorizar o texto lemaizado
  vetorizada = vectorizer.transform(lematizada).toarray()

  # Realizar predição modelo oferecido
  predicao = modelo.predict(vetorizada)

  return predicao[0]

# Apresentar análise do modelo  
def analizar_modelo(name, modelo):
  # Loop de apresentação dos conceitos
  for frase in frases_amostra:
    analise = analizar_frase(frase, modelo)
    print(frase + ' | ' +  analise)

  # Cálculo das métricas
  predicoes_teste = modelo.predict(vector_teste)

  accuracy = metrics.accuracy_score(classificacoes_teste, predicoes_teste)
  precision = metrics.precision_score(classificacoes_teste, predicoes_teste, average='weighted')
  recall = metrics.recall_score(classificacoes_teste, predicoes_teste, average='weighted')
  f1_score = metrics.f1_score(classificacoes_teste, predicoes_teste, average='weighted')
 
  print("")
  print("Acurária:", "{:.4f}".format(accuracy))
  print("Precisão:", "{:.4f}".format(precision))
  print("Recall Score:", "{:.4f}".format(recall))
  print("F1 Score:", "{:.4f}".format(f1_score))

  df_metric = pd.DataFrame(data={
      'Name': [name], 'Accuracy': [accuracy], 'Precision': [precision], 
      'Recall': [recall], 'F1 Score': [f1_score], 'Classifier': [modelo]})
  
  return pd.concat([resultado_metricas, df_metric])

##############################################
# C-Support Vector Classification
##############################################
from sklearn.svm import SVC

# Gerar modelo "Support Vector Classification" para realizar as previsões, com um valor de seed, forçar um resultado para as chaves aleatórias, para garantir replicabilidade do projeto
modelo_svc_linear = SVC(random_state=42, kernel="linear", C=0.025)
# Gerar fit do modelo para predições
modelo_svc_linear.fit(vector_treino, classificacoes_treino)
# Cálculo das métricas
resultado_metricas = analizar_modelo('C-Support Vector Classification - Linear', modelo_svc_linear)

# Gerar modelo "Support Vector Classification" para realizar as previsões, com um valor de seed, forçar um resultado para as chaves aleatórias, para garantir replicabilidade do projeto
modelo_svc_gamma = SVC(random_state=42, gamma=2, C=1)
# Gerar fit do modelo para predições
modelo_svc_gamma.fit(vector_treino, classificacoes_treino)
# Cálculo das métricas
resultado_metricas = analizar_modelo('C-Support Vector Classification - Gammma', modelo_svc_gamma)

##############################################
# Multinomial Naive Bayes
##############################################
from sklearn.naive_bayes import MultinomialNB

# Gerar modelo "Naive Bayes" para realizar as previsões
modelo_mnb = MultinomialNB()

# Gerar fit do modelo para predições
modelo_mnb.fit(vector_treino, classificacoes_treino)

# Apresentação dos conceitos
resultado_metricas = analizar_modelo('Multinomial Naive Bayes', modelo_mnb)

##############################################
# Gaussian Naive Bayes
##############################################
from sklearn.naive_bayes import GaussianNB

# Gerar modelo "Naive Bayes" para realizar as previsões
modelo_gnb = GaussianNB()

# Gerar fit do modelo para predições
modelo_gnb.fit(vector_treino, classificacoes_treino)

# Apresentação dos conceitos
resultado_metricas = analizar_modelo('Gaussian Naive Bayes', modelo_gnb)

##############################################
# Random Florest Classifier
##############################################
from sklearn.ensemble import RandomForestClassifier

# Gerar modelo "Random Florest" para realizar as previsões, com um valor de seed, forçar um resultado para as chaves aleatórias, para garantir replicabilidade do projeto
modelo_rf = RandomForestClassifier(max_depth=10, n_estimators=10, random_state=42)

# Gerar fit do modelo para predições
modelo_rf.fit(vector_treino, classificacoes_treino)

# Apresentação dos conceitos
resultado_metricas = analizar_modelo('Random Florest Classifier', modelo_rf)

##############################################
# Gradient Boosting Classifier
##############################################
from sklearn.ensemble import GradientBoostingClassifier

modelo_bg = GradientBoostingClassifier(n_estimators=100, learning_rate=1.0, max_depth=1, random_state=42)

# Gerar fit do modelo para predições
modelo_bg.fit(vector_treino, classificacoes_treino)

# Apresentação dos conceitos
resultado_metricas = analizar_modelo('Gradient Boosting Classifier', modelo_bg)

##############################################
# K-Neighbors Classifier
##############################################
from sklearn.neighbors import KNeighborsClassifier

modelo_knc = KNeighborsClassifier(n_neighbors=5)

# Gerar fit do modelo para predições
modelo_knc.fit(vector_treino, classificacoes_treino)

# Apresentação dos conceitos
resultado_metricas = analizar_modelo('K-Neighbors Classifier', modelo_knc)

##############################################
# Decision Tree Classifier
##############################################
from sklearn.tree import DecisionTreeClassifier

modelo_dtc = DecisionTreeClassifier(random_state=42)

# Gerar fit do modelo para predições
modelo_dtc.fit(vector_treino, classificacoes_treino)

# Apresentação dos conceitos
resultado_metricas = analizar_modelo('Decision Tree Classifier', modelo_dtc)

##############################################
# Gaussian Process Classifier
##############################################
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF

kernel = 1.0 * RBF(1.0)
modelo_gpc = GaussianProcessClassifier(kernel=kernel, random_state=42)

# Gerar fit do modelo para predições
modelo_gpc.fit(vector_treino, classificacoes_treino)

# Apresentação dos conceitos
resultado_metricas = analizar_modelo('Gaussian Process Classifier', modelo_gpc)

##############################################
# Multi-Layer Perceptron Classifier
##############################################
from sklearn.neural_network import MLPClassifier

modelo_clf = MLPClassifier(random_state=42, max_iter=1000)

# Gerar fit do modelo para predições
modelo_clf.fit(vector_treino, classificacoes_treino)

# Apresentação dos conceitos
resultado_metricas = analizar_modelo('Multi-Layer Perceptron Classifier', modelo_clf)

##############################################
# Quadratic Discriminant Analysis
##############################################
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis

modelo_qda = QuadraticDiscriminantAnalysis()

# Gerar fit do modelo para predições
modelo_qda.fit(vector_treino, classificacoes_treino)

# Apresentação dos conceitos
resultado_metricas = analizar_modelo('Quadratic Discriminant Analysis', modelo_qda)

##############################################
# Apuração de resultados os modelos
##############################################
print(resultado_metricas[['Name', 'Accuracy', 'Precision', 'Recall', 'F1 Score']])

# Selecionar o melhor modelo por acurácia
top_accuracy = 0
name_selected = ''
model_selected = None

for index, metrica in resultado_metricas.iterrows():
  if top_accuracy < metrica.Accuracy:
    top_accuracy = metrica.Accuracy
    name_selected = metrica.Name
    model_selected = metrica.Classifier

print('Modelo selecionado é {} com acurácia {}'.format(name_selected, top_accuracy))

# Importação de biblioteca de serialização
import pickle

# Geração do arquivo 'model_selected.sav' com o modelo 
pickle.dump(model_selected, open('./data/model_selected.sav', 'wb'))
pickle.dump(vectorizer, open('./data/vectorizer.sav', 'wb'))

# Carregar o arquivo com o modelo gerado
loaded_model = pickle.load(open('./data/model_selected.sav', 'rb'))

# Classificar a frase armazenada
classe = analizar_frase('Sua confeitaria a todo momento', loaded_model)

print(classe)