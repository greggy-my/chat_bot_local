import typing
import chromadb
from transformers import pipeline


class VectorDB:

    def __init__(self, path: str = "chroma_db"):
        self.client = chromadb.PersistentClient(path=path)
        self.current_collection = None

    def check_connection(self) -> int:
        return self.client.heartbeat()

    def create_collection(self, collection_name: str, distance_method: str = "l2") -> None:
        try:
            self.current_collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": distance_method}
            )
        except ValueError:
            print(f'Collection {collection_name} already exists')
            self.get_collection(collection_name=collection_name)

    def get_collection(self, collection_name: str) -> None:
        try:
            self.current_collection = self.client.get_collection(name=collection_name)
        except Exception:
            print('Collection is not found in the db')
        else:
            print('Collection is found, current collection is changed')

    def delete_collection(self, collection_name: str) -> None:
        try:
            self.client.delete_collection(collection_name)
        except Exception:
            print('Collection is not found in the db')
        else:
            print('Collection is found, collection is deleted')

    def rename_current_collection(self, new_name: str) -> None:
        self.current_collection.modify(name=new_name)

    def add_documents_to_current_collection(self, text_documents: list[str], documents_metadata: list[dict],
                                            documents_ids: list[str], embeddings: list[list]) -> None:
        self.current_collection.add(
            documents=text_documents,
            embeddings=embeddings,
            metadatas=documents_metadata,
            ids=documents_ids
        )

    def query_current_collection(self, query_embeddings: list[list], n_results: int = 3, metadata_filter: dict = None,
                                 document_filter: dict = None) -> dict:
        if (metadata_filter and document_filter) is None:
            return self.current_collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                include=["documents", "distances", "metadatas"],
            )
        elif metadata_filter is None and document_filter is not None:
            return self.current_collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                include=["documents", "distances", "metadatas"],
                where_document=document_filter
            )
        elif metadata_filter is not None and document_filter is None:
            return self.current_collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                include=["documents", "distances", "metadatas"],
                where=metadata_filter
            )

    def clear_current_collection(self) -> None:
        self.current_collection = None


if __name__ == "__main__":
    db = VectorDB()
    if db.check_connection() is not None:
        print('In DB')
