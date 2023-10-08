# Projeto Sistema de Recomendação de Filmes em python

Bem-vindo ao Sistema de Recomendação de Filmes! Este projeto oferece uma solução completa para recomendar filmes com base em diferentes critérios, como títulos de filmes similares e avaliações dos usuários. Ele também inclui funcionalidades para o download de dados, limpeza de títulos de filmes e impressão de tabelas de dados.

## Visão Geral

O projeto consiste em um conjunto de funções e utilitários implementados em Python para ajudar os usuários a descobrir e explorar filmes de maneira eficaz. Ele abrange as seguintes funcionalidades principais:

1. **Download e Extração de Dados:** Permite o download de conjuntos de dados de filmes a partir de URLs e extrai os arquivos ZIP correspondentes. Tratativas de erros robustas estão incorporadas para lidar com problemas comuns, como conexões fracas ou interrompidas.

2. **Limpeza de Títulos de Filmes:** Remove caracteres especiais e não alfanuméricos de títulos de filmes, tornando-os mais legíveis e fáceis de processar.

3. **Busca por Títulos de Filmes Similares:** Encontra títulos de filmes similares com base em um título fornecido. Esta função usa uma abordagem de análise de texto para determinar a similaridade entre títulos de filmes.

4. **Recomendação de Filmes com Base nas Avaliações dos Usuários:** Descobre filmes similares com base nas avaliações dos usuários. A função identifica usuários que classificaram um filme de forma positiva e recomenda outros filmes que esses usuários também apreciaram.

5. **Impressão de Tabelas de Dados:** Fornece uma maneira conveniente de exibir dados tabulares, facilitando a visualização e a análise de resultados.


## Pré-Requisitos

Antes de começar, certifique-se de ter os seguintes requisitos instalados:

- Python 3.6 ou superior
- Bibliotecas Python listadas em `requirements.txt`.

## Modo de Uso

Para usar o Sistema de Recomendação de Filmes, siga estas etapas simples:

1. Clone este repositório para o seu ambiente local ou use o codespace do github:

Execute o script movie_recommendation_system.py com o comando abaixo e substitua "Toy Story" pelo título do filme de sua escolha:

```
python movie_recommendation_system.py --movie-title "Toy Story"
```
A saída no seu terminal deve se assemelhar ao que é mostrado na imagem abaixo.

![main](./images/main.png)

## codigo

1. Define variáveis importantes, como a URL de onde os dados serão baixados e o diretório de armazenamento.
2. Obtém o título do filme especificado pelo usuário a partir da linha de comando.
3. Realiza o download e extração dos dados relacionados a filmes a partir de uma URL.
4. Lê os dados dos filmes a partir de um arquivo CSV e armazena-os em um DataFrame.
5. Encontra filmes semelhantes com base no título do filme especificado.
6. Imprime os resultados dos filmes semelhantes.
7. Lê os dados de classificação dos filmes a partir de outro arquivo CSV.
8. Encontra filmes semelhantes com base nas classificações dos usuários.
10. Imprime os filmes recomendados com base nas classificações dos usuários, se houver algum.
    
O arquivo movie_recommendation_system.py, o código principal coordena o download, processamento e apresentação de filmes semelhantes com base em diferentes critérios, como título e classificações de usuários.

```python

URL = "https://files.grouplens.org/datasets/movielens/ml-25m.zip"
script_path = os.path.abspath(__file__)
base_directory = os.path.dirname(script_path)


title_movie = services.get_title_movie()
if title_movie == "Unknown":
    sys.exit()

services.download_and_extract(URL, base_directory)


# import data from moveis
logging.info("set data movies")
# Construct the path to the movies.csv file
movies_csv_path = os.path.join(base_directory, "ml-25m", "movies.csv")

movies_df = pd.read_csv(movies_csv_path)

# log the shape of the data
logging.info("The shape of the data is %s", movies_df.shape)

# get the most similar movies
logging.info("Getting the most similar movies to %s", title_movie)
results = services.get_similar_movie_titles(title_movie, movies_df)

# print the results
columns_to_include = ["title", "genres"]
services.print_dataframe_table(results, columns_to_include)

ratings_csv_path = os.path.join(base_directory, "ml-25m", "ratings.csv")
# read the ratings data

logging.info("loading csv ratings")

ratings_df = pd.read_csv(ratings_csv_path)

logging.info("Finding similar by user ratings")

# Get the first movie title from 'results'
first_movie_title = results.iloc[0]["title"]

top_recommendations_movies = services.discover_similar_movies(
    movies_df,
    ratings_df,
    first_movie_title
)

if top_recommendations_movies.empty:
    logging.warning("o similar movies were found.")
else:
    columns_to_include = ["title", "genres"]
    services.print_dataframe_table(
        top_recommendations_movies, columns_to_include)
```


