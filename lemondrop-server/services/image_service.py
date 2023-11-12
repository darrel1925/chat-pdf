# lemondrop.ai

import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from clients.open_ai_client import open_ai_client as client

PRE_INSTRUCTIONS = "I am going to scan a PDF and show you the output. Please tell me what the text represent, and a few short sentences about it."


def prompt_gpt(text: str) -> str:
    """
    Prompts the GPT-3 engine with the given text and returns the response.
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            # {"role": "user", "content": "Summarize this in a few lines please:\n\n" + text},
            {"role": "user", "content":  text},
        ],
    )

    return response.choices[0].message.content

def get_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts text from the PDF at the given path using Tesseract.
    """
    pages = convert_from_path(pdf_path, 400)
    text = ""
    for i, page in enumerate(pages):
        text += pytesseract.image_to_string(page)
        if i > 1:
            break
    return text


def summarize_image(image_path: str) -> str:
    """
    Summarizes the image at the given path using GPT-3.
    """

    text = get_text_from_pdf(image_path)
    # print(text.lower())
    return prompt_gpt(text)
