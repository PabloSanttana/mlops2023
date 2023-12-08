FROM apache/airflow:2.8.0b1-python3.9

# Copie o arquivo requirements.txt para o contêiner
ENV WANDB_API_KEY=548b0d8a0c79d031f020a87b46b8434bb8e215bc

RUN pip3 install numpy pandas wandb requests matplotlib nltk pytest tensorflow-datasets
RUN pip3 install scikit-learn codecarbon transformers tensorflow seaborn datasets wordcloud


