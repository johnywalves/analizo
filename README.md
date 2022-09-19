# Analizo

Análise textual para validação de comunicação corporativa

## Spacy

Instalação da biblioteca

```bash
pip3 install spacy
```

Download biblioteca 

```bash
python -m spacy download pt_core_news_lg
```

## Run provider



```bash
uvicorn provider:app --reload
```


> **POST** http://127.0.0.1:8000


```javascript
{
    "frase": "Comer Doce bom demais"
}
```