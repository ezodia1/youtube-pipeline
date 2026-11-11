# Pipeline de Dados do YouTube

Pipeline de dados de ponta a ponta que coleta métricas públicas de vídeos de canais de Valorant no YouTube, trata os dados e os disponibiliza em um banco SQLite para análise de desempenho por formato (Short vs vídeo longo).

## Objetivo

Construir uma pipeline simples, organizada e reproduzível: extrair dados da API, guardar a resposta original, padronizar e validar, persistir em tabela consultável e responder perguntas com SQL e pandas.

## Fonte dos dados

- **YouTube Data API v3**, apenas dados públicos de canais públicos.
- Canais analisados: @OniquisZ (~9,9 mil inscritos), @lulavlr (~50 mil), @Nicksvava (~80 mil) e @buraclone (~240 mil). A lista fica em `config/channels.json`.
- Foram coletados 4.964 vídeos, dos quais 3.268 não são lives.

## Arquitetura

```mermaid
flowchart LR
    A[YouTube Data API v3] --> B[extract.py]
    B --> C[(data/raw: JSON bruto)]
    C --> D[transform.py]
    D --> E[(data/processed: CSV)]
    E --> F[load.py]
    F --> G[(SQLite: data/videos.db)]
    G --> H[SQL e analise.py]
```

| Etapa | Arquivo | O que faz |
|---|---|---|
| Extração | `src/extract.py` | Consulta a API com paginação e salva a resposta original em JSON |
| Área bruta | `data/raw/` | Respostas originais com data/hora da coleta, para rastreabilidade e reprocessamento |
| Transformação | `src/transform.py` | Achata o JSON, converte tipos, trata nulos, remove duplicatas e cria colunas |
| Carga | `src/load.py` | Grava no SQLite com upsert (carga incremental, sem duplicar) |
| Consumo | `sql/queries.sql`, `src/analise.py` | Consultas SQL e análise com pandas |

## Tabela final: `videos`

| Coluna | Descrição |
|---|---|
| `video_id` | ID do vídeo (chave primária) |
| `canal_id`, `canal` | Identificação do canal |
| `titulo` | Título do vídeo |
| `publicado_em` | Data de publicação (ISO 8601, UTC) |
| `views`, `likes`, `comentarios` | Métricas públicas (podem ser nulas se o canal as ocultar) |
| `coletado_em` | Momento da coleta |
| `is_live` | 1 se o vídeo foi uma transmissão ao vivo |
| `duracao_seg` | Duração em segundos |
| `is_short` | 1 se durou até 180 s e não foi live |
| `taxa_engajamento` | (likes + comentários) / views |

## Como executar

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

1. Crie um arquivo `.env` na raiz com `YOUTUBE_API_KEY=sua_chave` (veja `.env.example`).
2. Rode as etapas, na raiz do projeto:

```powershell
python src/extract.py
python src/transform.py
python src/load.py
python src/analise.py
```

As pastas `data/raw` e `data/processed` são criadas automaticamente.

## Decisões e premissas

- **Short:** a API não informa se o vídeo é Short. Foi usado o critério de duração de até 180 s, sem ser live.
- **Lives:** são marcadas na coluna `is_live`, e não removidas. As análises as excluem com `WHERE is_live = 0`, porque duração e engajamento delas são de outra natureza.
- **Carga incremental:** o `video_id` é chave primária e a carga usa upsert, então rodar a pipeline de novo atualiza as métricas sem duplicar linhas.
- **Credenciais:** a chave fica no `.env`, fora do Git.

## Resultados

Mediana de views por vídeo (excluindo lives):

| Canal | Longo | Short |
|---|---|---|
| @buraclone | 47.671 | **117.603** |
| @Nicksvava | **24.316** | 5.554 |
| @OniquisZ | **2.680** | 1.278 |
| @lulavlr | **16.448** | 13.686 |

- Não há um formato que sempre vença: o vídeo longo tem mediana maior em 3 dos 4 canais, e o @buraclone, que publica quase só Shorts, é a exceção.
- A média de views dos Shorts é muito maior que a mediana (os 10 vídeos mais vistos da base são Shorts do @buraclone), por isso a comparação usa a mediana.

## Limitações

- Quatro canais de um mesmo nicho, então os resultados não se generalizam.
- Vídeos mais antigos tiveram mais tempo para acumular views.
- A classificação de Short é uma aproximação por duração.
- A API só entrega métricas públicas, sem alcance ou tempo de exibição.

## Evolução futura

Agendamento diário com Apache Airflow, migração para PostgreSQL, testes de qualidade de dados, registro de execuções e dashboard.