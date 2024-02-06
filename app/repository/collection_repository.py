import chromadb
from chromadb.utils import embedding_functions

class CollectionRepository:
    def __init__(
        self,
        path: str,
    ):
        self.path = path
        self.embed_model = "all-MiniLM-L6-v2"

        self.embedding_func = embedding_functions.DefaultEmbeddingFunction(
        )

        self.client = chromadb.PersistentClient(path = path)
   
    def create_collection(self, collection_name: str):
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_func)
    
    def add(self, documents: list[str]):
        self.collection.add(
            documents=documents,
            ids=[f"id{i}" for i in range(len(documents))]
        )
    def get(self, query: str):
        query_results = self.collection.query(
            query_texts=[query],
            n_results=3,
        )

        return query_results
