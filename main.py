#main is used to run the app for local testing app is imported from the app/app.py file with the api named as app (app.app:app)
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app="app.app:app", host="0.0.0.0", port=8000)