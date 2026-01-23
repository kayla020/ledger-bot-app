import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def load_knowledge_base():
    """Load the knowledge base content from file"""
    knowledge_base_path = os.path.join(os.path.dirname(__file__), "knowledge_base.txt")
    try:
        with open(knowledge_base_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        # Fallback if file doesn't exist
        return """You are Ledger Bot, an AI assistant that helps teams understand and integrate with the GL Publisher and ledger system.

Answer questions clearly and concisely. If you're not sure, say so."""

# Initialize Slack app (no signing secret needed for Socket Mode)
slack_app = App(token=os.environ["SLACK_BOT_TOKEN"])

# Initialize LiteLLM client with staging endpoint
llm_client = OpenAI(
    api_key=os.environ["LITELLM_DEVELOPER_KEY"],
    base_url="https://llm.ws2.staging.w10e.com/api/v2",
    default_headers={"X-LiteLLM-Dev-Key": os.environ["LITELLM_DEVELOPER_KEY"]}
)

# Load knowledge base
KNOWLEDGE_BASE = load_knowledge_base()

# Handle mentions
@slack_app.event("app_mention")
def handle_mention(event, say, client):
    user_question = event["text"]
    channel = event["channel"]
    ts = event["ts"]

    # Send immediate acknowledgment
    thinking_msg = client.chat_postMessage(
        channel=channel,
        thread_ts=ts,
        text=":hourglass_flowing_sand: Thinking..."
    )

    # Call LiteLLM
    response = llm_client.chat.completions.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2000,
        messages=[
            {"role": "system", "content": KNOWLEDGE_BASE},
            {"role": "user", "content": user_question}
        ]
    )

    # Update with actual response
    client.chat_update(
        channel=channel,
        ts=thinking_msg["ts"],
        text=response.choices[0].message.content
    )

# Handle direct messages
@slack_app.event("message")
def handle_message(event, say, client):
    # Ignore bot's own messages
    if event.get("bot_id"):
        return

    user_question = event["text"]
    channel = event["channel"]

    # Send immediate acknowledgment
    thinking_msg = client.chat_postMessage(
        channel=channel,
        text=":hourglass_flowing_sand: Thinking..."
    )

    # Call LiteLLM
    response = llm_client.chat.completions.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2000,
        messages=[
            {"role": "system", "content": KNOWLEDGE_BASE},
            {"role": "user", "content": user_question}
        ]
    )

    # Update with actual response
    client.chat_update(
        channel=channel,
        ts=thinking_msg["ts"],
        text=response.choices[0].message.content
    )

if __name__ == "__main__":
    # Start Socket Mode
    handler = SocketModeHandler(slack_app, os.environ["SLACK_APP_TOKEN"])
    print("⚡️ Ledger Bot is running in Socket Mode!")
    handler.start()
