import os
import faiss
import numpy as np
import docx
import dotenv
from flask import Flask, request, jsonify
from google.generativeai import GenerativeModel
from sentence_transformers import SentenceTransformer

# Load environment variables
dotenv.load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Load the document and extract text
def load_document(doc_path):
    doc = docx.Document(doc_path)
    return " ".join([para.text for para in doc.paragraphs if para.text.strip()])

# Initialize FAISS index and store/retrieve embeddings
def create_or_load_faiss_index(sentences, model, index_path="models/faiss_index.bin"):
    embedding_dim = model.get_sentence_embedding_dimension()
    if os.path.exists(index_path):
        index = faiss.read_index(index_path)
        return index, None  # Load existing index
    else:
        embeddings = model.encode(sentences, convert_to_numpy=True)
        index = faiss.IndexFlatL2(embedding_dim)
        index.add(embeddings)
        faiss.write_index(index, index_path)  # Save the index
        return index, embeddings

# Retrieve top-k relevant sentences
def retrieve_context(query, sentences, index, model, k=3):
    query_embedding = model.encode([query], convert_to_numpy=True)
    distances, indices = index.search(query_embedding, k)
    return " ".join([sentences[i] for i in indices[0]])

# Initialize API & models
app = Flask(__name__)
resume_text = load_document("data/Neha_Jagtap_Resume.docx")
sentences = resume_text.split(". ")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

faiss_index, _ = create_or_load_faiss_index(sentences, embedding_model)

# Initialize Google Gemini API
gemini_model = GenerativeModel("gemini-1.0", api_key=GEMINI_API_KEY)

@app.route("/ask", methods=["POST"])
def ask_question():
    user_query = request.json.get("query")
    context = retrieve_context(user_query, sentences, faiss_index, embedding_model)
    response = gemini_model.generate_text(f"Based on the following resume context: {context}\n\nAnswer the question: {user_query}")
    return jsonify({"response": response.text})

if __name__ == "__main__":
    app.run(debug=True)
