from flask import Flask, request, jsonify
import pandas as pd
import base64
from io import BytesIO

app = Flask(__name__)


@app.route("/split-file", methods=["POST"])
def split_file():
    # Check if a file is included in the request
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]
    filename = file.filename

    # Determine file type and read accordingly
    if filename.endswith(".csv"):
        data = pd.read_csv(file)
        file_type = "csv"
    elif filename.endswith(".xlsx"):
        data = pd.read_excel(file)
        file_type = "excel"
    else:
        return (
            jsonify(
                {
                    "error": "Unsupported file format. Only CSV and Excel files are allowed."
                }
            ),
            400,
        )

    # Split the data into two halves
    total_rows = len(data)
    midpoint = total_rows // 2

    # Create two dataframes for the split parts
    split_1 = data.iloc[:midpoint]
    split_2 = data.iloc[midpoint:]

    # Encode split files in the original format
    output_files = []
    for idx, split_data in enumerate([split_1, split_2], start=1):
        buffer = BytesIO()

        # Save each split in its original format
        if file_type == "csv":
            split_data.to_csv(buffer, index=False)
        elif file_type == "excel":
            split_data.to_excel(buffer, index=False, engine="xlsxwriter")

        # Encode the buffer to base64
        buffer.seek(0)
        encoded_file = base64.b64encode(buffer.read()).decode("utf-8")
        output_files.append(
            {"filename": f"split_part_{idx}.{file_type}", "content": encoded_file}
        )

    # Return both files as base64 encoded strings
    return (
        jsonify(
            {"message": "File split into two parts successfully", "files": output_files}
        ),
        200,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
