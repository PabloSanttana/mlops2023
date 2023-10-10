"""
Main DAG file for the podcast summary project.
Author: Guilherme Pablo de Santana Maciel
Date: 2023-10-09
"""
import os
import json
import requests
import xmltodict
import logging

from airflow.decorators import dag, task
import pendulum
from airflow.providers.sqlite.operators.sqlite import SqliteOperator
from airflow.providers.sqlite.hooks.sqlite import SqliteHook

from vosk import Model, KaldiRecognizer
from pydub import AudioSegment

PODCAST_URL = "https://www.marketplace.org/feed/podcast/marketplace/"
EPISODE_FOLDER = "/home/pablo/mlops2023/python_essentials_for_MLOps/project_02/episodes"
FRAME_RATE = 16000


# set the logging level
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')


def create_database_episodes():
    return SqliteOperator(
        task_id='create_table_sqlite',
        sql=r"""
        CREATE TABLE IF NOT EXISTS episodes (
            link TEXT PRIMARY KEY,
            title TEXT,
            filename TEXT,
            published TEXT,
            description TEXT,
            transcript TEXT
        );
        """,
        sqlite_conn_id="podcasts"
    )

@task()
def get_episodes() -> list:
    try:
        logging.info("Fetching episodes.")
        data = requests.get(PODCAST_URL)
        # Raises an exception if the HTTP request is not successful.
        data.raise_for_status()
        feed = xmltodict.parse(data.text)
        episodes = feed["rss"]["channel"]["item"]
        logging.info("Found %s episodes.", len(episodes))
        return episodes
    except requests.exceptions.RequestException as e:
        # Catches exceptions related to HTTP requests, such as failed connections.
        logging.error("HTTP request error: %s", str(e))
        return []  # Retorna uma lista vazia em caso de erro
    except (KeyError, ValueError, TypeError) as e:
        # Catches exceptions related to XML parsing or invalid data structure.
        logging.error("XML parsing error or invalid data structure: %s", str(e))
        return []  # Returns an empty list in case of an error.

@task()
def load_episodes(episodes) -> list:
    try:
        hook = SqliteHook(sqlite_conn_id="podcasts")
        stored_episodes = hook.get_pandas_df("SELECT * from episodes;")
        new_episodes = []
        for episode in episodes:
            if episode["link"] not in stored_episodes["link"].values:
                filename = f"{episode['link'].split('/')[-1]}.mp3"
                new_episodes.append([episode["link"],
                                     episode["title"],
                                     episode["pubDate"],
                                     episode["description"],
                                     filename])

        hook.insert_rows(table='episodes',
                         rows=new_episodes,
                         target_fields=["link",
                                        "title",
                                        "published",
                                        "description",
                                        "filename"])
        return new_episodes
    except Exception as e:
        # Registre a exceção e continue ou tome medidas apropriadas, se necessário.
        logging.error("An error occurred in load_episodes: %s", str(e))
        return []

@task()
def download_episodes(episodes):
    audio_files = []
    for episode in episodes:
        name_end = episode["link"].split('/')[-1]
        filename = f"{name_end}.mp3"
        audio_path = os.path.join(EPISODE_FOLDER, filename)
        try:
            if not os.path.exists(audio_path):
                logging.info("Downloading %s", filename)
                audio = requests.get(episode["enclosure"]["@url"])
                with open(audio_path, "wb+") as f:
                    f.write(audio.content)
                audio_files.append({
                    "link": episode["link"],
                    "filename": filename
                })
            else:
                logging.info("Skipped downloading %s as it already exists.", filename)
        except Exception as e:
            logging.error("Error downloading episode %s: %s", episode['link'], str(e))
            continue
    return audio_files

@task()
def speech_to_text(audio_files, new_episodes) -> None:
    try:
        hook = SqliteHook(sqlite_conn_id="podcasts")
        untranscribed_episodes = hook.get_pandas_df(
            "SELECT * from episodes WHERE transcript IS NULL;")

        model = Model(model_name="vosk-model-en-us-0.22-lgraph")
        rec = KaldiRecognizer(model, FRAME_RATE)
        rec.SetWords(True)

        for _, row in untranscribed_episodes.iterrows():
            logging.info(f"Transcribing {row['filename']}")  # Log important step
            filepath = os.path.join(EPISODE_FOLDER, row["filename"])
            mp3 = AudioSegment.from_mp3(filepath)
            mp3 = mp3.set_channels(1)
            mp3 = mp3.set_frame_rate(FRAME_RATE)

            step = 20000
            transcript = ""
            for i in range(0, len(mp3), step):
                progress = i / len(mp3)
                logging.info(f"Progress: {progress}")  # Log progress
                segment = mp3[i:i + step]
                rec.AcceptWaveform(segment.raw_data)
                result = rec.Result()
                text = json.loads(result)["text"]
                transcript += text
            hook.insert_rows(table='episodes',
                             rows=[[row["link"], transcript]],
                             target_fields=["link", "transcript"],
                             replace=True)
    except Exception as e:
        # Handle exceptions and log the error
        logging.error(f"An error occurred: {str(e)}")


@dag(
    dag_id='podcast_summary',
    schedule_interval="@daily",
    start_date=pendulum.datetime(2022, 5, 30),
    catchup=False,
)
def podcast_summary():

    # create the database
    database = create_database_episodes()

    podcast_episodes = get_episodes()

    database.set_downstream(podcast_episodes)

    load_episodes(podcast_episodes)

    download_episodes(podcast_episodes)
    #Uncomment this to try speech to text (may not work)
    #speech_to_text(audio_files, new_episodes)

podcast_summary()
