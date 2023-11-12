from time import sleep 
from openai import OpenAI
from openai.types.beta.assistant import Assistant
from openai.types.beta.threads import ThreadMessage, MessageContentText
from openai.types.beta.threads.runs import RunStep
from openai.types.beta.threads.run import Run
from openai.pagination import SyncCursorPage
from openai.types.beta import Thread as OpenAIThread
from utils.constants import OPEN_AI_SECRET_KEY, OPEN_AI_ORGANIZATION_ID
from utils.constants import OPEN_AI_MODEL


class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=OPEN_AI_SECRET_KEY,
            organization=OPEN_AI_ORGANIZATION_ID,
        )

    def send_message_to_model(self, thread: 'Thread') -> None:
        """
        Sends a message to the model and returns the model's response.
        """

        # Add a message to the thread
        response: 'Stream' = self.client.chat.completions.create(
            messages=thread.stripped_messages,
            model=OPEN_AI_MODEL,
            stream=True,
        )
        return response

open_ai_client = OpenAIClient()
