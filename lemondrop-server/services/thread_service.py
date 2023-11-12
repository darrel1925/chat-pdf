from typing import Dict, Any
from models.thread import Thread, Message
from clients.open_ai_client import open_ai_client
class ThreadService:
    def send_message_to_model(self, params: Dict[str, Any]) -> bool:
        message = params.get("message")
        thread_id = params.get("thread_id")

        if not all([message, thread_id]):
            raise Exception(f"Missing required fields param={params}")
        
        thread: Thread = Thread.get(hash_key=thread_id)
        model_reply: Message = thread.send_message(content=message).to_dict()
        return model_reply
    
    def send_message_to_model_with_streaming(self, params: Dict[str, Any]) -> "Stream":
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

        return open_ai_client.send_message_to_model_v2(thread=thread)


thread_service = ThreadService()