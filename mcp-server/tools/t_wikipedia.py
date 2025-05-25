import wikipedia

def search_wikipedia(query: str, top_k: int = 3):
    titles = wikipedia.search(query, results=top_k)
    results = []
    for title in titles:
        try:
            summary = wikipedia.summary(title, sentences=2, auto_suggest=False)
            page = wikipedia.page(title, auto_suggest=False)
            results.append({
                "title": page.title,
                "summary": summary,
                "url": page.url
            })
        except Exception as e:
            results.append({"title": title, "error": str(e)})
    return results
