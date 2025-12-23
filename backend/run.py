import os

host = os.getenv("HOST", "127.0.0.1")  # Default to localhost
port = int(os.getenv("PORT", 8000))

uvicorn.run("main:app", host=host, port=port, reload=(os.getenv("ENV") == "development"))