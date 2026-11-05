import sqlite3

import pandas as pd


def criar_tabela(con):
    con.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            video_id TEXT PRIMARY KEY,
            canal_id TEXT,
            canal TEXT,
            titulo TEXT,
            publicado_em TEXT,
            views INTEGER,
            likes INTEGER,
            comentarios INTEGER,
            coletado_em TEXT,
            is_live INTEGER,
            duracao_seg INTEGER,
            is_short INTEGER,
            taxa_engajamento REAL
        )
    """)


def carregar(df, con):
    df = df.astype(object).where(df.notna(), None)
    colunas = ", ".join(df.columns)
    marcadores = ", ".join("?" * len(df.columns))
    atualiza = ", ".join(f"{c}=excluded.{c}" for c in df.columns if c != "video_id")
    con.executemany(
        f"INSERT INTO videos ({colunas}) VALUES ({marcadores}) "
        f"ON CONFLICT(video_id) DO UPDATE SET {atualiza}",
        df.itertuples(index=False, name=None),
    )
    con.commit()


if __name__ == "__main__":
    df = pd.read_csv("data/processed/videos.csv")
    with sqlite3.connect("data/videos.db") as con:
        criar_tabela(con)
        carregar(df, con)
        print(con.execute("SELECT COUNT(*) FROM videos").fetchone())