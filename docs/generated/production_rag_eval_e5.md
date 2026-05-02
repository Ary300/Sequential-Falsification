# Production RAG Eval (E5 Rerank)

This rerun keeps live Wikipedia search but replaces the weak TF-IDF+SVD reranker with multilingual E5 dense reranking.

- top-1 gold hit rate: `0.15`
- top-1 conflict hit rate: `0.05`
- top-5 both-hit rate: `0.1`
- mean retrieval latency: `2.783` s
- mean rerank latency: `5.4811` s
- throughput: `0.121` q/s

