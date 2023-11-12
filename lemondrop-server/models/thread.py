import boto3
import uuid
from enum import Enum
from typing import Dict, Any, List, Optional
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, ListAttribute, MapAttribute, BooleanAttribute
from openai.types.beta.threads import ThreadMessage, MessageContentText
from openai.types.beta import Thread as OpenAIThread
from openai.types.beta.threads.runs import RunStep
from openai.types.beta.threads.run import Run
from clients.open_ai_client import open_ai_client as client
from utils.time_utils import current_time_ms
s3 = boto3.resource('s3')

class Role(Enum):
    Assistant = "assistant"
    System = "system"
    User  = "user"


class Text(MapAttribute):
    value = UnicodeAttribute()
    annotations = ListAttribute(of=UnicodeAttribute, default=[])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "annotations": self.annotations,
        }

    @staticmethod
    def from_dict(text_dict: Dict[str, Any]) -> 'Text':
        return Text(
            value=text_dict["value"],
            annotations=text_dict["annotations"],
        )

# class Content(MapAttribute):
#     type = UnicodeAttribute(default="text")
#     text = Text()

#     def to_dict(self) -> Dict[str, Any]:
#         return {
#             "type": self.type,
#             "text": self.text.to_dict(),
#         }
    
#     @staticmethod
#     def from_dict(content_dict: Dict[str, Any]) -> 'Content':
#         return Content(
#             type=content_dict["type"],
#             text=Text.from_dict(content_dict["text"]),
#         )
    
class Message(MapAttribute):
    """
    Represents a user's text or any files the user uploads.
    """
    id = UnicodeAttribute()
    content = UnicodeAttribute()
    created_at_ms = NumberAttribute()
    is_hidden = BooleanAttribute(default=False)
    role = UnicodeAttribute()
    thread_id = UnicodeAttribute()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "created_at_ms": self.created_at_ms,
            "is_hidden": self.is_hidden,
            "role": self.role,
        }

    @staticmethod
    def from_dict(message_dict: Dict[str, Any]) -> 'Message':
        return Message(
            id=message_dict["id"],
            content=message_dict["content"],
            created_at_ms=message_dict["created_at_ms"],
            is_hidden=message_dict["is_hidden"],
            role=message_dict["role"],
            thread_id=message_dict["thread_id"],
        )
    
    @staticmethod
    def create_message(text: str, role: str, thread_id: str, is_hidden: bool = False) -> 'Message':
        msg = Message(
            id=str(uuid.uuid4()),
            content=text,
            created_at_ms=current_time_ms(),
            is_hidden=is_hidden,
            role=role,
            thread_id=thread_id,
        )

        return msg

class Thread(Model):
    """ 
    Represents a conversation with a user. Pass any user-specific context and files by creating Messages.
    """
    open_ai_thread: Optional[OpenAIThread] = None
    assistant_id = client.get_assistant().id

    class Meta:
        table_name = 'Thread'

    created_at_ms = NumberAttribute()
    id = UnicodeAttribute(hash_key=True)
    messages = ListAttribute(of=Message)
    user_id = UnicodeAttribute(default="") # Empty if user is not logged in

    def to_dict(self) -> Dict[str, Any]:
        return {
            'created_at_ms': self.created_at_ms,
            'id': self.id,
            'messages': [message.to_dict() for message in self.messages],
            'user_id': self.user_id,
        }

    
    @staticmethod
    def from_dict(thread_dict: Dict[str, Any]) -> 'Thread':
        return Thread(
            created_at_ms=thread_dict['created_at_ms'],
            id=thread_dict['id'],
            messages=[Message.from_dict(message) for message in thread_dict.get("messages", [])],
            user_id=thread_dict['user_id'],
        )

    
    @classmethod
    def get(cls, hash_key, range_key=None, consistent_read=False, **kwargs):
        """
        Fetches Dynamo object and assigns OpenAI Thread to instance
        """
        dynamo_thread: 'Thread' = super(Thread, cls).get(hash_key, range_key=range_key, consistent_read=consistent_read, **kwargs)

        open_ai_thread: OpenAIThread = client.get_thread(thread_id=dynamo_thread.id)
        dynamo_thread.open_ai_thread: OpenAIThread = open_ai_thread

        return dynamo_thread

    
    @staticmethod
    def create() -> None:
        """
        Creates a new thread in Dynamo and OpenAI
        """
        open_ai_thread: OpenAIThread = client.create_thread()
        new_thread: Thread = Thread(
            created_at_ms=current_time_ms(),
            id=open_ai_thread.id,
            messages=[],
        )
        new_thread.open_ai_thread: OpenAIThread = open_ai_thread
        new_thread.save()

        return new_thread

    # def send_message(self, content: str) -> Message:
    #     """
    #     Sends a message to the thread. Returns the model's response.
    #     """
    #     # Add a message to the thread
    #     self._add_message(content=content)

    #     # Updates OpenAI's thread state from to ensure the thread is in sync.
    #     self.open_ai_thread = client.get_thread(thread_id=self.id)

    #     # Create a run used to get the model's response to the user's message
    #     run: Run = client.create_run(thread_id=self.id)

    #     # Waits for the model to respond to the user's most recent message.
    #     client.wait_for_run(thread_id=self.id, run_id=run.id)

    #     # Get models response
    #     return self.get_message_from_run(run_id=run.id)
    
    
    # def get_message_from_run(self, run_id: str) -> Message or None:
    #     """
    #     Gets a message from OpenAI.
    #     """
    #     message_id: str = client.get_message_id_from_run(thread_id=self.id, run_id=run_id)
    #     thread_message: ThreadMessage = client.get_message(thread_id=self.id, message_id=message_id)
    #     message: Message = self._add_message(content=thread_message.content[0].text.value, role=Role.Assistant)
    #     return message    
    
    
    def add_message(self, content: str, role: Role = Role.User) -> Message:
        """
        Adds a message to the Dynamo and OpenAI.
        """
        message: Message = Message.create_message(
            text=content,
            role=role.value,
            thread_id=self.id,
        )

        self.update(
            actions=[
                Thread.messages.set((Thread.messages | []).append([message]))
            ]
        )

        return message

    @property
    def stripped_messages(self) -> List[Dict[str, Any]]:
        """
        Returns messages without additional parameters for OpenAI.
        """
        return [{"content": message.content, "role": message.role} for message in self.messages if not message.is_hidden]

    # def save_document_text_to_s3(self, document_text: str) -> None:
    #     Message.create_message("Here is my PDF:\n\n " + document_text, Role.User, is_hidden=True)
    #     self._add_message(content=Message)
    #     s3.Object('lemondrop-ai', f'public/documents/{self.id}.txt').put(Body=document_text)


    def get_document_text_from_s3(self) -> str:
        return s3.Object('lemondrop-ai', f'public/documents/{self.id}.txt').get()['Body'].read().decode('utf-8')
