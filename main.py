import os
import shutil
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
from qreader import QReader
import cv2
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

class ImageUrlRequest(BaseModel):
    image_url: HttpUrl

@app.get("/", response_class=JSONResponse)
async def index():
    """
    Serve a plain JSON response for the root route.
    """
    return {"message": "hello world"}

@app.get("/process-qrcode/", response_class=JSONResponse)
async def process_qrcode(image_url: HttpUrl = Query(...)):
    """
    Process the image URL provided as a query parameter, detect QR codes, and return the result in JSON format.
    """
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
                return {"success": True, "decoded_text": decoded_text[0]}
            else:
                return {"success": False, "message": "No QR code detected in the image."}

        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=400, detail=f"Failed to download the image: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing the image: {e}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
