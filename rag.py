from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

index = None
documents = []


def build_index(text_chunks):
    global index, documents

    documents = text_chunks
    embeddings = model.encode(text_chunks)

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings))


def retrieve(query, k=3):
    global index, documents

    if index is None:
        return ["No data indexed yet"]

    query_embedding = model.encode([query])
    D, I = index.search(np.array(query_embedding), k)

    return [documents[i] for i in I[0]]