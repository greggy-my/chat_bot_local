from db.vector_db import VectorDB
from models import embed_text

if __name__ == "__main__":
    db = VectorDB()
    if db.check_connection() is not None:
        db.get_collection(collection_name='habr')

    embeddings = embed_text(["Framework Javascript"])
    answer = db.query_current_collection(query_embeddings=embeddings)
    print(answer)
    print(answer["documents"])
    print(answer["documents"][0]) #лист ближайших 3х
