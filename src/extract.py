from dotenv import load_dotenv
from datetime import datetime
import os
import json
import requests

load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

with open("config/channels.json", "r") as f:
    config = json.load(f)

def buscar_canal(handle):
    url = "https://www.googleapis.com/youtube/v3/channels"
    params = {
        "part": "snippet,statistics,contentDetails",
        "forHandle": handle,
        "key": YOUTUBE_API_KEY,
    }
    resposta = requests.get(url, params=params)
    resposta.raise_for_status()
    dados = resposta.json()

    if not dados.get("items"):
        raise ValueError(f"Canal não encontrado: {handle}")

    return dados["items"][0]

def listar_video_ids(playlist_id):
    url = "https://www.googleapis.com/youtube/v3/playlistItems"
    params = {
        "part": "contentDetails",
        "playlistId": playlist_id,
        "maxResults": 50,
        "key": YOUTUBE_API_KEY,
    }
    ids = []
    while True:
        resposta = requests.get(url, params=params)
        resposta.raise_for_status()
        dados = resposta.json()

        ids += [item["contentDetails"]["videoId"] for item in dados["items"]]

        proximo = dados.get("nextPageToken")
        if not proximo:
            break
        params["pageToken"] = proximo
    return ids


def buscar_videos(video_ids):
    url = "https://www.googleapis.com/youtube/v3/videos"
    videos = []
    for i in range(0, len(video_ids), 50):
        lote = video_ids[i:i + 50]
        params = {
            "part": "snippet,statistics,contentDetails,liveStreamingDetails",
            "id": ",".join(lote),
            "key": YOUTUBE_API_KEY,
        }
        resposta = requests.get(url, params=params)
        resposta.raise_for_status()
        videos += resposta.json()["items"]
    return videos


def salvar_bruto(handle, canal, videos):
    os.makedirs("data/raw", exist_ok=True)
    agora = datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho = f"data/raw/{handle.lstrip('@')}_{agora}.json"
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(
            {"coletado_em": agora, "canal": canal, "videos": videos},
            f,
            ensure_ascii=False,
            indent=2,
        )
    return caminho


for handle in config["channels"]:
    canal = buscar_canal(handle)
    uploads = canal["contentDetails"]["relatedPlaylists"]["uploads"]
    video_ids = listar_video_ids(uploads)
    videos = buscar_videos(video_ids)
    caminho = salvar_bruto(handle, canal, videos)
    print(f"{handle}: {len(videos)} vídeos salvos em {caminho}")