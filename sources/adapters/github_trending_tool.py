import requests
from datetime import datetime, timedelta, timezone


def fetch_github_trending():
    since = (
        datetime.now(timezone.utc) - timedelta(days=30)
    ).date().isoformat()

    url = "https://api.github.com/search/repositories"

    queries = [
        f"topic:llm language:python pushed:>{since}",
        f"topic:artificial-intelligence language:python pushed:>{since}",
        f"topic:machine-learning language:python pushed:>{since}",
    ]

    repos = []

    for query in queries:
        response = requests.get(
            url,
            params={
                "q": query,
                "sort": "updated",
                "order": "desc",
                "per_page": 5,
            },
            timeout=10,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "LinkedIn-AI-Content-Agent",
            }
        )
        response.raise_for_status()

        for repo in response.json().get("items", []):
            repo_path = repo.get("full_name", "")
            if not repo_path:
                continue

            repos.append({
                "source": "GitHub",
                "source_type": "github",
                "title": repo_path,
                "summary": repo.get("description") or "GitHub AI repository",
                "url": repo.get("html_url", f"https://github.com/{repo_path}"),
                "language": repo.get("language", ""),
                "stars": repo.get("stargazers_count", 0),
                "published_at": repo.get("updated_at", ""),
            })

            if len(repos) >= 5:
                return repos

    return repos
