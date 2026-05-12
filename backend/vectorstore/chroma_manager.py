import os
import shutil
from typing import List
from git import Repo
import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter

class ChromaManager:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self.collection = self.client.get_or_create_collection(
            name="codebase",
            embedding_function=self.embedding_fn
        )

    def clone_repository(self, repo_url: str, local_path: str):
        """Clones a GitHub repository to a local path."""
        if os.path.exists(local_path):
            shutil.rmtree(local_path)
        Repo.clone_from(repo_url, local_path)

    def index_repository(self, repo_path: str):
        """Indexes the repository content into ChromaDB."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )

        documents = []
        metadatas = []
        ids = []

        for root, _, files in os.walk(repo_path):
            # Skip hidden files and directories
            if any(part.startswith('.') for part in root.split(os.sep)):
                continue

            for file in files:
                if file.endswith(('.py', '.js', '.html', '.css', '.md', '.txt')):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, repo_path)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        chunks = text_splitter.split_text(content)
                        for i, chunk in enumerate(chunks):
                            documents.append(chunk)
                            metadatas.append({"path": relative_path})
                            ids.append(f"{relative_path}_{i}")
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")

        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

    def search(self, query: str, n_results: int = 5):
        """Searches the indexed codebase for relevant snippets."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results
