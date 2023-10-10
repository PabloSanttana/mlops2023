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
import pendulum

from airflow.decorators import dag, task
from airflow.providers.sqlite.operators.sqlite import SqliteOperator
from airflow.providers.sqlite.hooks.sqlite import SqliteHook

from vosk import Model, KaldiRecognizer
from pydub import AudioSegment

PODCAST_URL = "https://www.marketplace.org/feed/podcast/marketplace/"
EPISODE_FOLDER = "/home/pablo/mlops2023/python_essentials_for_MLOps/project_02/episodes"
FRAME_RATE = 16000

@task()
def create_database_episodes() ->  SqliteOperator:
    """
    Create a SQLite database table for podcast episodes.

    This function creates a table named 'episodes' in the SQLite database
    specified by the 'sqlite_conn_id' parameter. The table has columns for
    'link', 'title', 'filename', 'published', 'description', and 'transcript'.

    Args:
        None

    Returns:
        SqliteOperator: An instance of SqliteOperator.
    """
    create_database = SqliteOperator(
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
    return create_database

@task()
def get_request_episodes() -> list:
    """
    Fetch podcast episodes from the specified URL.

    This function sends an HTTP GET request to the PODCAST_URL and parses the
    response to extract podcast episodes. It handles exceptions related to
    HTTP requests and XML parsing.

    Returns:
        list: A list of podcast episodes as dictionaries.
    """
    try:
        logging.info("Fetching episodes.")
        data = requests.get(PODCAST_URL,timeout=15)
        # Raises an exception if the HTTP request is not successful.
        data.raise_for_status()
        feed = xmltodict.parse(data.text)
        episodes = feed["rss"]["channel"]["item"]
        logging.info("Found %s episodes.", len(episodes))
        return episodes
    except requests.exceptions.RequestException as requests_error:
        # Catches exceptions related to HTTP requests, such as failed connections.
        logging.error("HTTP request error: %s", str(requests_error))
        return []  # Retorna uma lista vazia em caso de erro

    except (KeyError, ValueError, TypeError) as erro_all:
        # Catches exceptions related to XML parsing or invalid data structure.
        logging.error("XML parsing error or invalid data structure: %s", str(erro_all))
        return []  # Retorna uma lista vazia em caso de erro.


@task()
def load_databese_episodes(episodes) -> list:
    """
    Load new podcast episodes into the SQLite database.

    This function checks if each episode is already in the database and inserts
    new episodes if they are not present.

    Args:
        episodes (list): A list of podcast episodes as dictionaries.

    Returns:
        list: A list of newly inserted episodes.
    """
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
    except Exception as exception:
        logging.error("An error occurred: %s", str(exception))
        return []




@task()
def download_episodes(episodes):
    """
    Download podcast episodes as audio files.

    This function takes a list of podcast episodes and downloads their audio files
    if they do not already exist in the specified folder.

    Args:
        episodes (list): A list of podcast episodes as dictionaries.

    Returns:
        list: A list of downloaded audio files (dictionary with link and filename).
    """
    audio_files = []
    for episode in episodes:
        name_end = episode["link"].split('/')[-1]
        filename = f"{name_end}.mp3"
        audio_path = os.path.join(EPISODE_FOLDER, filename)
        try:
            if not os.path.exists(audio_path):
                logging.info("Downloading %s", filename)
                audio = requests.get(episode["enclosure"]["@url"], timeout=15)
                audio.raise_for_status()  # Raise an exception if the request is not successful
                with open(audio_path, "wb+") as audio_file:
                    audio_file.write(audio.content)
                audio_files.append({
                    "link": episode["link"],
                    "filename": filename
                })
            else:
                logging.info("Skipped downloading %s as it already exists.", filename)
        except requests.exceptions.RequestException as request_error:
            logging.error("HTTP request error for episode %s: %s",
                          episode['link'],
                          str(request_error))
            continue
        except IOError as io_error:
            logging.error("IO error while downloading episode %s: %s",
                          episode['link'],
                          str(io_error))
            continue
    return audio_files

def transcribe_audio_segment(audio_segment, recognizer):
    """
    Transcribe an audio segment and return the result.
    """
    transcript = ""
    step = 20000
    for i in range(0, len(audio_segment), step):
        progress = i / len(audio_segment)
        logging.info("Progress %s", progress)  # Log progress
        segment = audio_segment[i:i + step]
        recognizer.AcceptWaveform(segment.raw_data)
        result = recognizer.Result()
        text = json.loads(result)["text"]
        transcript += text
    return transcript

@task()
def speech_to_text() -> None:
    """
    Transcribe audio files to text and update the database.

    This function takes a list of audio files, transcribes them to text using the Vosk
    speech recognition model, and updates the database with the transcriptions.

    Returns:
        None
    """
    try:
        hook = SqliteHook(sqlite_conn_id="podcasts")
        untranscribed_episodes = hook.get_pandas_df(
            "SELECT * from episodes WHERE transcript IS NULL;")

        model = Model(model_name="vosk-model-en-us-0.22-lgraph")
        rec = KaldiRecognizer(model, FRAME_RATE)
        rec.SetWords(True)

        for _, row in untranscribed_episodes.iterrows():
            logging.info("Transcribing %s", row['filename'])  # Log important step
            filepath = os.path.join(EPISODE_FOLDER, row["filename"])
            mp3 = AudioSegment.from_mp3(filepath)
            mp3 = mp3.set_channels(1)
            mp3 = mp3.set_frame_rate(FRAME_RATE)

            transcript = transcribe_audio_segment(mp3, rec)

            hook.insert_rows(table='episodes',
                             rows=[[row["link"], transcript]],
                             target_fields=["link", "transcript"],
                             replace=True)
    except FileNotFoundError as file_error:
        # Handle file not found error
        logging.error("File not found: %s", str(file_error))
    except Exception as exception:
        logging.error("An error occurred: %s", str(exception))

@dag(
    dag_id='podcast_summary',
    schedule_interval="@daily",
    start_date=pendulum.datetime(2022, 5, 30),
    catchup=False,
)
def podcast_summary():
    """
    This function defines the workflow for the podcast processing DAG.

    It creates a database, fetches podcast episodes, loads them into the database,
    and downloads audio files. You can also uncomment the 'speech_to_text' call
    to enable speech-to-text transcription (may not work).

    Returns:
        None
    """
    create_database = create_database_episodes()

    podcast_episodes = get_request_episodes()
    create_database.set_downstream(podcast_episodes)

    load_databese_episodes(podcast_episodes)

    download_episodes(podcast_episodes)

    #Uncomment this to try speech to text (may not work)
    #speech_to_text(audio_files, new_episodes)

summary = podcast_summary()
