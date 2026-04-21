import os
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename  # ADD THIS
import uuid                                  # ADD THIS
from ai import analyze_apple

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


def allowed_file(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/inspect", methods=["POST"])
def inspect():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Only JPG, PNG, and WEBP are allowed."}), 400

    file.seek(0, 2)
    file_size = file.tell()
    file.seek(0)

    if file_size > MAX_FILE_SIZE_BYTES:
        return jsonify({"error": f"File too large. Maximum size is {MAX_FILE_SIZE_MB}MB."}), 400

    # CHANGED: safe unique filename instead of original
    ext = secure_filename(file.filename).rsplit(".", 1)[1].lower()
    safe_filename = f"{uuid.uuid4().hex}.{ext}"
    image_path = os.path.join(UPLOAD_FOLDER, safe_filename)

    file.save(image_path)

    try:
        result = analyze_apple(image_path)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(image_path):
            os.remove(image_path)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)