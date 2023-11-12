from typing import Dict, Any
from models.thread import Thread, Message
from clients.open_ai_client import open_ai_client
import json

class ThreadService:
    def send_message_to_model(self, params: Dict[str, Any]) -> "Stream":
        message = params.get("message")
        thread_id = params.get("thread_id")

        if not all([message, thread_id]):
            raise Exception(f"Missing required fields param={params}")
        
        try:
            print("Trying to get thread")
            thread: Thread = Thread.get(hash_key=thread_id)
        except Thread.DoesNotExist:
            print("Thread does not exist. Creating new thread.")
            thread: Thread = Thread.create()
        
        # Add message to Dynamo
        thread.add_message(content=message)

        return open_ai_client.send_message_to_model(thread=thread)
    
    def stream_generator(self, params: Dict[str, any]):
        """Generates streaming response."""        
        stream = self.send_message_to_model(params=params)

        for chunk in stream:
            try:
                if chunk.choices[0].finish_reason is not None:
                    yield f"data: {json.dumps({'end_of_stream': True})}\n\n"
                    break

                content = chunk.choices[0].delta.content
                yield f"data: {json.dumps({'message': content})}\n\n"
            except Exception as e:
                print(f"Error in stream: {e}")
                break


thread_service = ThreadService()