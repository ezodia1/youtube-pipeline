import glob
import json
import os

import pandas as pd


def carregar_bruto():
    linhas = []
    for caminho in glob.glob("data/raw/*.json"):
        with open(caminho, encoding="utf-8") as f:
            bruto = json.load(f)
        for v in bruto["videos"]:
            stats = v.get("statistics", {})
            linhas.append({
                "video_id": v["id"],
                "canal_id": v["snippet"]["channelId"],
                "canal": v["snippet"]["channelTitle"],
                "titulo": v["snippet"]["title"],
                "publicado_em": v["snippet"]["publishedAt"],
                "duracao": v["contentDetails"]["duration"],
                "views": stats.get("viewCount"),
                "likes": stats.get("likeCount"),
                "comentarios": stats.get("commentCount"),
                "coletado_em": bruto["coletado_em"],
                "is_live": "liveStreamingDetails" in v,
            })
    return pd.DataFrame(linhas)


def transformar(df):
    df = df.sort_values("coletado_em").drop_duplicates("video_id", keep="last")
    df["publicado_em"] = pd.to_datetime(df["publicado_em"])
    df["coletado_em"] = pd.to_datetime(df["coletado_em"], format="%Y%m%d_%H%M%S")
    for col in ["views", "likes", "comentarios"]:
        df[col] = pd.to_numeric(df[col]).astype("Int64")
    df["duracao_seg"] = pd.to_timedelta(df["duracao"], errors="coerce").dt.total_seconds().astype("Int64")
    df["is_short"] = (df["duracao_seg"] <= 180) & ~df["is_live"]
    df["taxa_engajamento"] = (df["likes"] + df["comentarios"]) / df["views"].where(df["views"] > 0)
    return df.drop(columns="duracao")


if __name__ == "__main__":
    df = transformar(carregar_bruto())
    os.makedirs("data/processed", exist_ok=True)
    df.to_csv("data/processed/videos.csv", index=False)
    print(df.shape)
    print(df.dtypes)
    print(df["is_short"].value_counts())
    print(df.groupby("canal")["is_live"].value_counts())