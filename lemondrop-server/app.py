import json
from flask import Flask, request, Response
from flask_cors import CORS

from services.thread_service import thread_service

app = Flask(__name__)
CORS(app)


# -----Thread-----
STREAM_URL = '/stream'

@app.get("/")
def health():
    return "Hello World"

@app.route(STREAM_URL, methods=["GET"])
def stream_response():
    """Endpoint for streaming responses."""
    thread_id, message = request.args.get('thread_id'), request.args.get('message') 
    params = {"thread_id": thread_id, "message": message}
    return Response(thread_service.stream_generator(params=params), mimetype='text/event-stream')


if __name__ == "__main__":
    app.run(port=8000)