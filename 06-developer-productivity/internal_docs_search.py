#!/usr/bin/env python3
"""
================================================================================
INTERNAL DOCS SEARCH ENGINE
================================================================================

RESUME BULLET POINT:
"Built an internal docs search engine that aggregates scattered documentation
into a unified search experience, reducing time spent finding information."

Author: DevOps Engineer | Version: 1.0.0
================================================================================
"""

import argparse
import json
import re
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class Document:
    """Searchable document"""
    id: str
    title: str
    source: str  # wiki, readme, runbook, etc.
    content: str
    url: str
    last_updated: datetime


@dataclass
class SearchResult:
    """Search result with relevance"""
    document: Document
    score: float
    snippet: str


class DocsSearchEngine:
    """Unified search across internal documentation"""
    
    def __init__(self):
        self.documents: List[Document] = []
        self.index: Dict[str, List[str]] = {}  # word -> doc_ids
    
    def load_documents(self) -> List[Document]:
        """Load documents from various sources (simulated)"""
        self.documents = [
            Document("doc1", "API Authentication Guide", "wiki", 
                    "How to authenticate with our API. Use OAuth2 tokens...", 
                    "/wiki/api-auth", datetime.now()),
            Document("doc2", "Deployment Runbook", "runbook",
                    "Steps for deploying to production. First, run tests...",
                    "/runbooks/deploy", datetime.now()),
            Document("doc3", "Database Schema", "readme",
                    "Our PostgreSQL database schema includes users, orders...",
                    "/repos/db/README.md", datetime.now()),
            Document("doc4", "Kubernetes Setup", "wiki",
                    "Setting up local Kubernetes with minikube...",
                    "/wiki/k8s-setup", datetime.now()),
            Document("doc5", "Incident Response Process", "runbook",
                    "When an incident occurs, first acknowledge in PagerDuty...",
                    "/runbooks/incident", datetime.now()),
            Document("doc6", "API Rate Limiting", "wiki",
                    "Our API has rate limits. 1000 requests per minute...",
                    "/wiki/rate-limits", datetime.now()),
        ]
        self._build_index()
        return self.documents
    
    def _build_index(self):
        """Build search index"""
        for doc in self.documents:
            words = re.findall(r'\w+', (doc.title + " " + doc.content).lower())
            for word in set(words):
                if word not in self.index:
                    self.index[word] = []
                self.index[word].append(doc.id)
    
    def search(self, query: str, limit: int = 5) -> List[SearchResult]:
        """Search documents"""
        query_words = re.findall(r'\w+', query.lower())
        scores: Dict[str, float] = {}
        
        for word in query_words:
            matching_docs = self.index.get(word, [])
            for doc_id in matching_docs:
                scores[doc_id] = scores.get(doc_id, 0) + 1
        
        results = []
        for doc_id, score in sorted(scores.items(), key=lambda x: -x[1])[:limit]:
            doc = next(d for d in self.documents if d.id == doc_id)
            snippet = doc.content[:100] + "..."
            results.append(SearchResult(doc, score / len(query_words), snippet))
        
        return results
    
    def get_stats(self) -> Dict:
        """Get search engine stats"""
        return {
            "total_documents": len(self.documents),
            "indexed_words": len(self.index),
            "by_source": {},
        }


def print_results(results: List[SearchResult], query: str):
    """Print search results"""
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           INTERNAL DOCS SEARCH                               ║
╠══════════════════════════════════════════════════════════════╣
║  Query: "{query}"{' ':<(48 - len(query))}║
║  Results Found: {len(results):<43}║
╠══════════════════════════════════════════════════════════════╣
║  RESULTS:                                                    ║""")
    
    for i, result in enumerate(results, 1):
        score = f"{result.score:.0%}"
        print(f"║    {i}. [{result.document.source}] {result.document.title:<30}{score:>5} ║")
        print(f"║       {result.document.url:<52}║")
    
    if not results:
        print(f"║    No results found{' ':<40}║")
    
    print("╚══════════════════════════════════════════════════════════════╝")


def main():
    parser = argparse.ArgumentParser(description="Internal Docs Search")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--search", type=str, default="API authentication")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()
    
    print("=" * 60)
    print("   INTERNAL DOCS SEARCH ENGINE")
    print("=" * 60)
    
    engine = DocsSearchEngine()
    engine.load_documents()
    
    stats = engine.get_stats()
    print(f"\n📚 Indexed {stats['total_documents']} documents, {stats['indexed_words']} unique terms")
    
    print(f"\n🔍 Searching: \"{args.search}\"")
    results = engine.search(args.search, args.limit)
    
    print_results(results, args.search)
    
    return 0


if __name__ == "__main__":
    exit(main())
