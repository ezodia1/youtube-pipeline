-- 1. Visão geral por canal (sem lives)
SELECT
    canal,
    COUNT(*) AS videos,
    ROUND(AVG(views)) AS views_medias,
    ROUND(AVG(taxa_engajamento) * 100, 2) AS engajamento_pct
FROM videos
WHERE is_live = 0
GROUP BY canal
ORDER BY views_medias DESC;

-- 2. Shorts vs vídeo longo por canal (sem lives)
SELECT
    canal,
    CASE WHEN is_short = 1 THEN 'Short' ELSE 'Longo' END AS formato,
    COUNT(*) AS videos,
    ROUND(AVG(views)) AS views_medias,
    ROUND(AVG(taxa_engajamento) * 100, 2) AS engajamento_pct
FROM videos
WHERE is_live = 0
GROUP BY canal, is_short
ORDER BY canal, formato;

-- 3. Evolução por ano (sem lives)
SELECT
    strftime('%Y', publicado_em) AS ano,
    COUNT(*) AS videos,
    ROUND(AVG(views)) AS views_medias
FROM videos
WHERE is_live = 0
GROUP BY ano
ORDER BY ano;

-- 4. Top 10 vídeos por views (sem lives)
SELECT canal, titulo, views, is_short
FROM videos
WHERE is_live = 0
ORDER BY views DESC
LIMIT 10;