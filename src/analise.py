import pandas as pd

df = pd.read_csv("data/processed/videos.csv")
df = df[~df["is_live"]]
df["formato"] = df["is_short"].map({True: "Short", False: "Longo"})

resumo = df.groupby(["canal", "formato"])["views"].agg(["count", "mean", "median"]).round()
print(resumo)