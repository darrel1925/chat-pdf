import json
from flask import Flask, request, Response
from flask_cors import CORS

from services.thread_service import thread_service

app = Flask(__name__)
CORS(app)


# -----Thread-----
SEND_MESSAGE = "/v1/thread/send-message"
SEND_MESSAGE_V2 = "/v2/thread/send-message"

@app.get("/")
def health():
    return "Hello World"
    
@app.post(SEND_MESSAGE)
def send_message_to_model():
    params = request.json
    try:
        model_response = thread_service.send_message_to_model(params=params)
        return {"resp": model_response, "status": 200}

    except Exception as e:
        return {"resp": str(e), "status": 500}
    
@app.post(SEND_MESSAGE_V2)
def send_message_to_model_with_streaming():
    params = request.json
    try:
        thread_service.send_message_to_model_with_streaming(params=params)
        return {"resp": "success", "status": 200}

    except Exception as e:
        return {"resp": str(e), "status": 500}


@app.get('/stream')
def stream_response():
    def generate():
        # thread_id = request.args.get('thread_id') 
        # message = request.args.get('message')

        params = {"thread_id": "thread_aYVuUpHCU5XLfNwyJrEovkIE", "message": "Tell me a joke!"}
        stream = thread_service.send_message_to_model_with_streaming(params=params)
        
        for chunk in stream:
            if chunk.choices[0].finish_reason != None:
                print("Finished")
                yield f"data: {json.dumps({'end_of_stream': True})}\n\n"
                break
            
            string = chunk.choices[0].delta.content
            data = {"message": f"{string}"}
            yield f"data: {json.dumps(data)}\n\n"

    return Response(response=generate(), mimetype='text/event-stream')


if __name__ == "__main__":
    app.run(port=8000)