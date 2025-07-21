

### installation

```bash
playwright install
playwright install chromium

```

## scrape

```bash
cd web_crawler
python scraper.py
```

### embedder
- To test standlone embedding of json files

```bash
python -m rag.indexer.embedder
```


### indexer
- Embeds and upserts the embedings into vector store
    - configurable to use either R2R RAG APIs or Qdrant as the vector store
```bash
python -m rag.indexer.indexer
```

