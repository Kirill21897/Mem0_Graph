# config.py
import os
from dotenv import load_dotenv

load_dotenv()

MEM0_CONFIG = {
    "vector_store": {
        "provider": "chroma",
        "config": {
            "collection_name": "mem0graph_vectors",
            "path": "./chroma_db"
        }
    },
    
    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": "bolt://localhost:7687",
            "username": "neo4j",
            "password": "password123"
        }
    },
    
    # LLM: OpenAI (но через OpenRouter благодаря OPENAI_BASE_URL)
    "llm": {
        "provider": "openai",
        "config": {
            "model": "openai/gpt-4o-mini"
            # base_url и api_key берется из .env автоматически!
        }
    },
    
    "embedder": {
        "provider": "huggingface",
        "config": {
            "model": "sentence-transformers/all-MiniLM-L6-v2",
            "embedding_dims": 384
        }
    }
}