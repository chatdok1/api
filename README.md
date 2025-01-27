# To be able to successful run you need 
## Install qrcode dependencies
`sudo apt update`

`sudo apt install libgl1`

`sudo apt-get install libzbar0`

## Local Testing

To try the application on your local machine:

### Install the requirements

`pip install -r requirements.txt`

### Start the application

`uvicorn main:app --reload`

### Example call

http://127.0.0.1:8000/

## Next Steps

To learn more about FastAPI, see [FastAPI](https://fastapi.tiangolo.com/).
