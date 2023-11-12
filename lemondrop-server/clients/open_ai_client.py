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
    ASSISTANT_ID = "asst_3uiZ6b6mxOS5ggE4ZAEgQvzD"  
    def __init__(self):
        self.client = OpenAI(
            api_key=OPEN_AI_SECRET_KEY,
            organization=OPEN_AI_ORGANIZATION_ID,
        )
    
    def get_assistant(self) -> Assistant:
        return self.client.beta.assistants.retrieve(self.ASSISTANT_ID)
    
    def create_thread(self) -> OpenAIThread:
        return self.client.beta.threads.create()
    
    def get_thread(self, thread_id: str) -> OpenAIThread:
        return self.client.beta.threads.retrieve(thread_id)
    
    def get_message(self, thread_id: str, message_id: str) -> ThreadMessage:
        return self.client.beta.threads.messages.retrieve(thread_id=thread_id, message_id=message_id)
    
    def get_message_list(self, thread_id: str) -> SyncCursorPage:
        return self.client.beta.threads.messages.list(thread_id=thread_id)

    def add_message_to_thread(self, thread_id: str, role: str, content: str) -> ThreadMessage:
        return self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role=role,
            content=content,
        )

    def create_run(self, thread_id: str) -> RunStep:
        return self.client.beta.threads.runs.create(thread_id=thread_id, assistant_id=self.ASSISTANT_ID)
    
    def _get_run(self, thread_id: str, run_id: str) -> RunStep:
        return self.client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)

    def wait_for_run(self, thread_id: str, run_id: str) -> None:
        while True:
            run_status: Run = self._get_run(thread_id=thread_id, run_id=run_id)
            if run_status.status == 'completed':
                break
            elif run_status.status == 'failed':
                print("Run failed.")
                break
            
            print(f"[{run_status.status}] Waiting for model to respond...")
            sleep(2)

    def get_message_id_from_run(self, thread_id: str, run_id: str) -> SyncCursorPage:
        response: SyncCursorPage = self.client.beta.threads.runs.steps.list(thread_id=thread_id, run_id=run_id)
        step: RunStep = response.data[0]  # This data contains message id
        return step.step_details.message_creation.message_id
        

    def send_message_to_model_v2(self, thread: 'Thread') -> None:
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

        string = ""
        for chunk in response:
            string += chunk.choices[0].delta.content
            print(string)

open_ai_client = OpenAIClient()
