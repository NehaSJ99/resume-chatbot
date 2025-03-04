from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from gemini_logic import get_resume_response
import traceback


app = Flask(__name__, static_folder="static", template_folder="templates")  
CORS(app)  # ✅ Allow frontend requests from other websites

# ✅ Serve the chat UI when accessing "/"
@app.route('/')
def serve_chat_ui():
    return render_template("index.html")  # Serves the HTML page

# ✅ API Endpoint for Gemini
@app.route("/api/gemini", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"reply": "⚠️ Please provide a valid message in JSON format."}), 400

    user_message = data["message"].strip()
    if not user_message:
        return jsonify({"reply": "⚠️ Message cannot be empty."}), 400

    try:
        reply_text = get_resume_response(user_message)
        return jsonify({"reply": reply_text})

    except Exception as e:
        print("❌ ERROR in /api/gemini:", str(e))
        traceback.print_exc()  # ✅ Print full error details
        return jsonify({"error": f"❌ Internal Server Error: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # ✅ Render dynamically assigns a PORT
    app.run(host="0.0.0.0", port=port, debug=True)
