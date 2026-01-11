import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

#initializing chroma
DATA_DIR = "local_vector_db"

class vectorDB:
    def __init__(self):
        # using a small embedding model
        self.embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # create folder if not present
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

        # create chroma database
        try:
            self.db = Chroma(
                persist_directory=DATA_DIR,
                embedding_function=self.embeddings
            )
        except Exception as err:
            print("Error making database:", err)
            self.db = None

    def add_documents(self, documents):
        # documents is list of dicts with "text" and "source"
        text_list = []
        meta_list = []

        for d in documents:
            text_list.append(d["text"])
            meta_list.append({"source": d["source"]})

        try:
            self.db.add_texts(texts=text_list, metadatas=meta_list)
            self.db.persist()
        except Exception as err:
            print("Error adding docs:", err)

    def query(self, query_text, k=4):
        try:
            results = self.db.similarity_search(query_text, k=1)
            return results
        except Exception as err:
            print("Search error:", err)
            return None
