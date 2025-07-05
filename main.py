from dotenv import load_dotenv
import os
import chainlit as cl
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

# Load Gemini API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Setup OpenAI-compatible Gemini client
client = AsyncOpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
model_name = "gemini-1.5-flash"

@cl.on_chat_start
async def on_chat_start():
    # Ask user for translation language
    response = await cl.AskUserMessage(
        content="👋 Hello! Which language would you like me to translate into?"
    ).send()

    if response and "output" in response:
        selected_language = response.get("output", "").strip().capitalize()
    else:
        selected_language="None"

    if selected_language:
        cl.user_session.set("target_lang", selected_language)
        await cl.Message(
            content=f"✅ Great! I’ll translate all future messages to **{selected_language}**. Type something!"
        ).send()
    else:
        await cl.Message(content="⚠️ No language selected. Please refresh and try again.").send()


@cl.on_message
async def on_message(message: cl.Message):
    target_lang = cl.user_session.get("target_lang", "Urdu")
    user_input = message.content

    thinking_message = cl.Message(content="🤔 Thinking...")
    await thinking_message.send()

    # Prepare Gemini-compatible messages
    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": f"You are a helpful assistant. Your ONLY task is to translate anything the user sends into {target_lang}. NEVER respond in English or do anything else."},
        {"role": "user", "content": user_input},
    ]

    # Call Gemini via OpenAI-compatible API
    response = await client.chat.completions.create(
        model=model_name,
        messages=messages,
    )

    translated = response.choices[0].message.content

    thinking_message.content = f"🌐 Translation in **{target_lang}**:\n\n{translated}"
    await thinking_message.update()