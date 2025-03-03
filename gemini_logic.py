import os
import faiss
import numpy as np
from docx import Document
import dotenv
import google.generativeai as genai
from sentence_transformers import SentenceTransformer

# ✅ Load environment variables
dotenv.load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ✅ Configure Google Gemini API key
genai.configure(api_key=GEMINI_API_KEY)

# ✅ Load the resume document and extract text
def load_document(doc_path):
    doc = Document(doc_path)
    return " ".join([para.text.strip() for para in doc.paragraphs if para.text.strip()])

# ✅ Initialize FAISS index and store/retrieve embeddings
def create_or_load_faiss_index(sentences, model, index_path="models/faiss_index.bin"):
    embedding_dim = model.get_sentence_embedding_dimension()
    
    # ✅ If FAISS index already exists, load it (DO NOT RECOMPUTE)
    if os.path.exists(index_path):
        print("✅ Loading precomputed FAISS index...")
        return faiss.read_index(index_path), None  

    print("🔄 Computing FAISS index for the first time...")
    embeddings = model.encode(sentences, convert_to_numpy=True)
    index = faiss.IndexFlatL2(embedding_dim)
    index.add(embeddings)
    
    # ✅ Save the FAISS index to disk for future use
    faiss.write_index(index, index_path)
    print("💾 FAISS index saved to disk.")

    return index, embeddings

# ✅ Retrieve relevant information from resume
def retrieve_context(query, sentences, index, model, k=5):
    query_embedding = model.encode([query], convert_to_numpy=True)
    distances, indices = index.search(query_embedding, k)

    print(f"🔍 Query: {query}")
    print(f"📊 FAISS Retrieved Indices: {indices}")
    print(f"📏 FAISS Distances: {distances}")

    if len(indices) == 0 or len(indices[0]) == 0:
        print("⚠️ No results found for query:", query)
        return "⚠️ No relevant information found in the resume for this query."

    return " ".join([sentences[i] for i in indices[0] if i < len(sentences)])

# ✅ Load and Initialize Models
# ✅ Load and Initialize Models
resume_text = load_document("data/Neha_Jagtap_Resume.docx")
sentences = resume_text.split(". ")

# ✅ Initialize FAISS but LOAD if already computed
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
faiss_index, _ = create_or_load_faiss_index(sentences, embedding_model)

# ✅ Initialize Google Gemini
gemini_model = genai.GenerativeModel("gemini-2.0-flash")

# ✅ Generate structured response using Gemini
def get_resume_response(query):
    context = retrieve_context(query, sentences, faiss_index, embedding_model)

    if not context.strip():
        return "⚠️ The requested information is not available in Neha's professional background. Let me know if you are looking for something specific."

    prompt = f"""
    You are Neha Jagtap's AI assistant, helping recruiters and professionals learn about her experience.

    **Relevant Resume Context:**
    {context}

    **User's Question:** {query}

    **Instructions:**
    - Provide a **complete and structured response**.
    - Do **not cut off the response** mid-sentence.
    - If the response is long, **return in full sentences** rather than truncating.
    """

    print(f"🛠️ Debugging: Sending Prompt to Gemini:\n{prompt}\n")

    try:
        response = gemini_model.generate_content(prompt)

        print(f"✅ Gemini Response: {response.text}")
        return response.text.strip()
    
    except Exception as e:
        print("❌ ERROR in Gemini API Call:", str(e))
        traceback.print_exc()  # ✅ Print full error stack trace
        return "⚠️ Error: Unable to retrieve response from AI."



