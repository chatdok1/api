import os
import shutil
import cv2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from qreader import QReader
import requests
from tempfile import NamedTemporaryFile
import uvicorn

# Set environment variables to avoid warnings
os.environ['MPLCONFIGDIR'] = "/tmp/matplotlib"
os.makedirs("/tmp/matplotlib", exist_ok=True)

# Ensure Matplotlib uses the specified directory
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend to avoid GUI dependencies

app = FastAPI()

# Define the request model
class ImageUrlRequest(BaseModel):
    image_url: HttpUrl


@app.post("/process-qrcode/")
async def process_qrcode(request: ImageUrlRequest):
    """
    Download an image from the provided URL, process it to detect QR codes,
    and return the decoded text.
    """
    image_url = request.image_url

    # Create a temporary directory to store the downloaded image
    with NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        temp_image_path = tmp_file.name

        try:
            # Download the image
            response = requests.get(image_url, stream=True)
            response.raise_for_status()

            # Save the image to the temp file
            with open(temp_image_path, "wb") as f:
                shutil.copyfileobj(response.raw, f)

            # Initialize the QReader and process the image
            qreader = QReader()
            image = cv2.cvtColor(cv2.imread(temp_image_path), cv2.COLOR_BGR2RGB)
            decoded_text = qreader.detect_and_decode(image=image)

            # Remove the temporary image file
            os.unlink(temp_image_path)

            if decoded_text:
                return {"qr_text": decoded_text[0]}
            else:
                raise HTTPException(status_code=404, detail="No QR code detected in the image.")

        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=400, detail=f"Failed to download the image: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing the image: {e}")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
