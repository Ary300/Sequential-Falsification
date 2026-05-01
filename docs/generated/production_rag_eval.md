# Production-Style RAG Evaluation

This note upgrades the earlier retrieval probes into a more deployable pipeline: live Wikipedia search as the first stage, then lexical BM25 and a dense-ish TF-IDF+SVD reranker over the candidate pool.
It is still not a full commercial production stack, but it is a real end-to-end retrieval system with latency and throughput accounting.

## Headline

- BM25 top-1 gold hit rate: `0.1`
- BM25 top-1 conflict hit rate: `0.0`
- BM25 top-5 both-hit rate: `0.1`
- Hybrid top-1 gold hit rate: `0.1`
- Hybrid top-1 conflict hit rate: `0.0`
- Hybrid top-5 both-hit rate: `0.1`
- Mean live retrieval latency: `3.3208` s
- P50 / P90 live retrieval latency: `0.4683` / `1.5182` s
- Mean rerank latency: `0.0119` s
- Throughput: `0.3001` queries/s

## Example queries

### 1

- Question: Which of the following are present in Nymphaea nouchali var. caerulea: apomorphine, aporphine, or neither?
- Gold answers: `['Apomorphine', 'Aporphine']`
- Conflict answers: `['Aporphine']`
- BM25 top-k:
- Hybrid top-k:

### 2

- Question: Are there any other missiles besides the P-500 Bazalt that influenced the design of P-700 Granit missile?
- Gold answers: `['No.', 'Yes.']`
- Conflict answers: `['Yes.']`
- BM25 top-k:
- Hybrid top-k:

### 3

- Question: Did the formation of the grooves on Phobos occur as a single event?
- Gold answers: `['No.', 'Yes.']`
- Conflict answers: `['Yes.']`
- BM25 top-k:
  - score `4.7962` gold `True` conflict `False`: Ariel (moon) occultations <span class="searchmatch">of</span> Uranus&#039;s moons become possible. <span class="searchmatch">A</span> number <span class="sea...
  - score `4.6712` gold `True` conflict `False`: 2018 in science Astronomers conclude that the many <span class="searchmatch">grooves</span> <span class="searchmatch">on</span> <span class="searchmatch">Pho...
  - score `4.5037` gold `True` conflict `False`: Aeolis quadrangle behind. Since <span class="searchmatch">the</span> ridges <span class="searchmatch">occur</span> in locations with clay, these <span class=...
  - score `3.4295` gold `True` conflict `False`: Climate of Mars more predictable than that <span class="searchmatch">of</span> Earth. If an <span class="searchmatch">event</span> <span class="searchmatch">...
  - score `2.5811` gold `True` conflict `False`: Solar System April 2024. One <span class="searchmatch">of</span> <span class="searchmatch">the</span> most striking features <span class="searchmatch">of</sp...
- Hybrid top-k:
  - hybrid `3.5096` bm25 `4.6712` dense `0.0711` gold `True` conflict `False`: 2018 in science Astronomers conclude that the many <span class="searchmatch">grooves</span> <span class="searchmatch">on</span> <span class="searchmatch">Pho...
  - hybrid `0.8504` bm25 `4.7962` dense `0.0074` gold `True` conflict `False`: Ariel (moon) occultations <span class="searchmatch">of</span> Uranus&#039;s moons become possible. <span class="searchmatch">A</span> number <span class="sea...
  - hybrid `0.8255` bm25 `4.5037` dense `0.0134` gold `True` conflict `False`: Aeolis quadrangle behind. Since <span class="searchmatch">the</span> ridges <span class="searchmatch">occur</span> in locations with clay, these <span class=...
  - hybrid `-0.8250` bm25 `3.4295` dense `-0.0004` gold `True` conflict `False`: Climate of Mars more predictable than that <span class="searchmatch">of</span> Earth. If an <span class="searchmatch">event</span> <span class="searchmatch">...
  - hybrid `-1.2607` bm25 `2.5811` dense `0.0085` gold `True` conflict `False`: Solar System April 2024. One <span class="searchmatch">of</span> <span class="searchmatch">the</span> most striking features <span class="searchmatch">of</sp...

### 4

- Question: Did Bishop Heber meet D’Oyly in the 1840s in Patna ?
- Gold answers: `['Yes', 'No']`
- Conflict answers: `['No']`
- BM25 top-k:
- Hybrid top-k:

### 5

- Question: What year did President Oler take the stand in court?
- Gold answers: `['President Oler took the stand in 1911', 'President Oler appeard in court in the 1890s']`
- Conflict answers: `['President Oler appeard in court in the 1890s']`
- BM25 top-k:
  - score `1.8434` gold `False` conflict `False`: James Baldwin 2013). &quot;On James Baldwin&quot;. <span class="searchmatch">The</span> New York Review of Books. Retrieved July 6, 2017. <span class="search...
  - score `1.5075` gold `False` conflict `False`: Timeline of the Joe Biden presidency (2021 Q3) getaway plans shift by <span class="searchmatch">the</span> day&quot;. Associated Press. Retrieved August 16, ...
- Hybrid top-k:
  - hybrid `0.0000` bm25 `1.8434` dense `-0.0446` gold `False` conflict `False`: James Baldwin 2013). &quot;On James Baldwin&quot;. <span class="searchmatch">The</span> New York Review of Books. Retrieved July 6, 2017. <span class="search...
  - hybrid `0.0000` bm25 `1.5075` dense `0.0737` gold `False` conflict `False`: Timeline of the Joe Biden presidency (2021 Q3) getaway plans shift by <span class="searchmatch">the</span> day&quot;. Associated Press. Retrieved August 16, ...

## Read

- This is the strongest honest retrieval-side system result in the repo so far because it includes live retrieval, reranking, and latency accounting in one place.
- The numbers should be read as deployment-style evidence, not as a replacement for the benchmark-centered theorem matrix.
