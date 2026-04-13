import urllib.request
import os

os.makedirs("models", exist_ok=True)

# CORRECT WORKING URLs
urls = [
    ("https://raw.githubusercontent.com/opencv/opencv_3rdparty/8afa57abc8229d611c4937165d20e2a2d9fc5a12/deploy.prototxt", "deploy.prototxt"),
    ("https://github.com/opencv/opencv_3rdparty/raw/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel", "res10_300x300_ssd_iter_140000.caffemodel")
]

for url, filename in urls:
    filepath = os.path.join("models", filename)
    if not os.path.exists(filepath):
        print(f"Downloading {filename}...")
        try:
            urllib.request.urlretrieve(url, filepath)
            print(f"✅ Downloaded {filename}")
        except Exception as e:
            print(f"❌ Failed to download {filename}: {e}")
    else:
        print(f"✓ {filename} already exists")