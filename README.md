# LinkedIn AI Content Agent

A local AI workflow for generating technical LinkedIn posts from current AI and engineering signals.

The project gathers topics from news feeds, Reddit, Hacker News, GitHub Trending, and arXiv, ranks them for a technical audience, writes a concise LinkedIn post, reviews and scores it, optionally generates a companion image, and stores the result for later review.

Posting to LinkedIn is intentionally disabled. The app is built around a human approval step before anything is published.

## Features

- Multi-source trend collection from NewsData, Currents, Reddit, GitHub Trending, arXiv, and Hacker News
- LangGraph workflow for topic selection, post drafting, review, scoring, image decisions, and memory storage
- Local LLM generation through Ollama
- Hugging Face image generation through the `fal-ai` provider
- Streamlit dashboard for previewing, editing, downloading, and approving posts
- CLI mode for generating and saving a post from the terminal
- Post memory to reduce repeated topics
- Evaluation metrics for quality, human tone, specificity, CTA quality, and source validity

## Project Structure

```text
.
|-- app.py                    # Streamlit dashboard entry point
|-- main.py                   # CLI entry point
|-- agent/                    # LangGraph orchestration
|   |-- graph.py              # Workflow definition and routing
|   `-- model_router.py       # Reserved for future model routing
|-- sources/                  # Trend collection and filtering
|   |-- aggregator.py         # Combines all content sources
|   |-- trend_fetcher.py      # Normalizes, filters, and deduplicates trends
|   `-- adapters/             # Individual source adapters
|-- content/                  # Topic planning and content strategy
|   |-- trend_ranker.py       # Scores and ranks topics
|   |-- topic_selector.py     # Picks one topic while avoiding repeats
|   `-- content_type_selector.py
|-- writing/                  # Post generation, review, and scoring
|   |-- post_writer.py
|   |-- reviewer.py
|   |-- scorer.py
|   |-- post_cleaner.py
|   |-- contrarian_insight.py
|   |-- insight_compressor.py
|   `-- voice_profile.md
|-- media/                    # Image decisions and generation
|   |-- visual_decider.py
|   |-- image_prompt.py
|   `-- image_generator.py
|-- evaluation/               # Deterministic quality metrics and history
|   |-- metrics.py
|   `-- store.py
|-- storage/                  # Memory persistence
|   `-- memory_store.py
|-- data/                     # Generated posts and post memory
|-- images/                   # Generated images from CLI runs
`-- approved_posts/           # Posts and images saved from the dashboard
```

## Requirements

- Python 3.10+
- Ollama installed and running locally
- Local Ollama models:
  - `mistral`
  - `qwen2.5:7b`
- API keys for optional/remote sources:
  - NewsData API key
  - Currents API key
  - Hugging Face token for image generation
- Optional Neon/Postgres database URL for deployed persistent memory

Pull the Ollama models before running the app:

```powershell
ollama pull mistral
ollama pull qwen2.5:7b
```

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
NEWS_API_KEY=your_newsdata_key
CURRENTS_API_KEY=your_currents_key
HF_TOKEN=your_huggingface_token
NVIDIA_API_KEY=your_nvidia_api_key
DATABASE_URL=postgresql://user:password@host.neon.tech/dbname?sslmode=require
MEMORY_RETENTION_DAYS=30
```

The app can still collect some sources without paid API keys, but the NewsData and Currents fetchers will skip/fail if their keys are missing. If `DATABASE_URL` is set, post memory, evaluations, and ranked trend cache are stored in Postgres. If it is missing, the app falls back to local JSON files under `data/`.
`MEMORY_RETENTION_DAYS` controls how long generated post memory is kept before old records are automatically removed. It defaults to 30 days.

## Run the Streamlit App

```powershell
streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal.

In the dashboard you can:

- Generate a new post
- Review the selected topic and reasoning chain
- Edit the final post before approval
- Download the post
- Download the generated image
- Save an approved post to `approved_posts/`
- Inspect quality metrics and evaluation history
- Inspect saved memory and raw LangGraph state

The **Post to LinkedIn** button is disabled by design.

## Run from the CLI

```powershell
python main.py
```

The CLI prints the final post, saves it to `data/post_<timestamp>.txt`, and saves a generated image to `images/post_image.png` when image generation succeeds.

## How the Agent Works

The workflow is defined in `agent/graph.py`:

1. Fetch trends from all configured sources.
2. Rank trends for a technical AI audience.
3. Select one topic while avoiding recently used topics.
4. Choose a content type such as `TREND_ANALYSIS`, `TECH_BREAKDOWN`, `BUILD_LOG`, `HOT_TAKE`, or `PROJECT_SHOWCASE`.
5. Generate a contrarian or non-obvious insight.
6. Compress the insight into a concise engineering takeaway.
7. Draft the LinkedIn post.
8. Review and clean the post.
9. Score the result.
10. Retry writing if the score is below 7, up to 3 attempts.
11. Evaluate the final post with deterministic metrics.
12. Decide whether an image is useful.
13. Generate an image prompt and image when needed.
14. Save the final state to memory.

## Persistence

- With `DATABASE_URL`, generated post history is stored in the `post_memory` table.
- With `DATABASE_URL`, post evaluation history is stored in the `evaluations` table.
- With `DATABASE_URL`, ranked trend cache is stored in the `trend_cache` table.
- Without `DATABASE_URL`, `data/post_memory.json` stores generated post history.
- Without `DATABASE_URL`, `data/evaluations.json` stores post evaluation history.
- `data/post_<timestamp>.txt` stores CLI-generated posts.
- `images/post_image.png` stores the latest CLI-generated image.
- `approved_posts/post_<timestamp>.txt` stores dashboard-approved posts.
- `approved_posts/latest_image.png` stores the latest dashboard image preview.

The database tables are created automatically on first app run.
Post memory older than `MEMORY_RETENTION_DAYS` is automatically removed whenever memory is loaded.

## Content Sources

The source adapters live in `sources/adapters/`:

- `google_news_tool.py` uses the NewsData API.
- `currents_news.py` uses the Currents API.
- `reddit_tool.py` reads the `r/artificial` RSS feed.
- `github_trending_tool.py` scrapes GitHub Trending.
- `arxiv_tool.py` reads the arXiv `cs.AI` feed.
- `hackernews_tool.py` reads Hacker News top stories and filters AI-related posts.

## Notes

- The generated writing is constrained to avoid hashtags, raw URLs, hype language, fake personal experience, and generic calls to action.
- Discussion sources such as Reddit and Hacker News are treated as signals, not verified news.
- Image generation requires `HF_TOKEN`; failures are shown in the app and do not stop post generation.
- The project currently has no automated LinkedIn publishing integration.

## Evaluation Metrics

Each generated post is evaluated and saved to the configured database, or to `data/evaluations.json` when no database is configured.

Tracked metrics include:

- `evaluation_score`: average of clarity, human tone, specificity, source validity, and CTA quality
- `clarity_score`: penalizes long/awkward structure, banned phrases, raw URLs, and hashtags
- `human_tone_score`: penalizes generic CTAs, template language, and AI/corporate phrasing
- `specificity_score`: rewards concrete technical terms and numeric detail
- `source_faithfulness_score`: checks whether the final source line matches the selected source
- `cta_quality_score`: penalizes generic engagement endings
- supporting counts such as word count, question count, banned phrase count, generic CTA count, and raw URL count

## Benchmark Workflow

Use this process to create resume-ready numbers:

1. Run the app and generate 10 to 20 posts before a prompt change.
2. Save the average metrics from the Evaluation tab.
3. Improve the prompts, reviewer, or cleaner.
4. Generate another 10 to 20 posts.
5. Compare before vs after:
   - Average evaluation score
   - Average human tone score
   - Generic CTA rate
   - Source validity rate
   - Average retry count

Example resume bullet:

```text
Built a LangGraph-based AI content agent with an evaluation layer tracking post quality, human tone, specificity, source validity, generic CTA rate, and retry count across generated samples.
```

## Troubleshooting

If post generation fails, check that Ollama is running and that both required models are installed.

If news fetching fails, verify `NEWS_API_KEY` and `CURRENTS_API_KEY` in `.env`.

If image generation fails, verify `HF_TOKEN` and your Hugging Face account/provider access.

If the Streamlit dashboard fails with an import error, reinstall dependencies:

```powershell
pip install -r requirements.txt
```
