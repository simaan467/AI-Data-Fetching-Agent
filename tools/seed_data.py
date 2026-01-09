import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.vectordb import vectorDB


def seed_vector_db():
    vdb = vectorDB()
    seed_documents = [
        {
    "text": "Hyderabad is the capital of Telangana and known for biryani.",
    "source": "local_knowledge"
        },
        {
    "text": "Mumbai is the financial capital of India.",
    "source": "local_knowledge"
        },
        {
    "text": "Java is a statically typed programming language used in enterprise development.",
    "source": "local_knowledge"
        }
        ]
    vdb.add_documents(seed_documents)
    print(f"seeing vector db with {len(seed_documents)} documents added.")

if __name__ == "__main__":
    seed_vector_db()