from flask import Flask, render_template, request, send_file
import os
from datetime import datetime, timedelta
import piexif
from zipfile import ZipFile

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def change_exif_time(input_path, output_path, dt):
    exif_dict = piexif.load(input_path)
    time_str = dt.strftime("%Y:%m:%d %H:%M:%S").encode()

    exif_dict["0th"][piexif.ImageIFD.DateTime] = time_str
    exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = time_str
    exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = time_str

    piexif.insert(piexif.dump(exif_dict), output_path)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        start_time_str = request.form["start_time"]
        start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M")

        files = request.files.getlist("photos")

        processed_files = []
        current_time = start_time

        for file in files:
            filename = file.filename
            input_path = os.path.join(UPLOAD_FOLDER, filename)
            output_path = os.path.join(PROCESSED_FOLDER, filename)

            file.save(input_path)
            change_exif_time(input_path, output_path, current_time)

            processed_files.append(output_path)
            current_time += timedelta(minutes=1)

        zip_path = os.path.join(PROCESSED_FOLDER, "photos_with_new_time.zip")
        with ZipFile(zip_path, "w") as zipf:
            for f in processed_files:
                zipf.write(f, os.path.basename(f))

        return send_file(zip_path, as_attachment=True)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
