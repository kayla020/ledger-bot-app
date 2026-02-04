import os
import threading
from flask import Flask, jsonify
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Health check server
health_app = Flask(__name__)
health_status = {"ready": False, "slack_connected": False, "llm_connected": False}

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

# Get model name from environment or use default
# Wealthsimple LiteLLM uses AWS Bedrock model names
MODEL_NAME = os.environ.get("LITELLM_MODEL", "bedrock-claude-4.5-sonnet")

# Health check endpoints
@health_app.route('/health', methods=['GET'])
def health():
    """Liveness probe - is the app alive?"""
    return jsonify({"status": "healthy"}), 200

@health_app.route('/ready', methods=['GET'])
def ready():
    """Readiness probe - is the app ready to serve?"""
    if health_status["ready"] and health_status["slack_connected"]:
        return jsonify(health_status), 200
    else:
        return jsonify(health_status), 503

def run_health_server():
    """Run the health check server on a separate thread"""
    port = int(os.environ.get("HEALTH_PORT", "8080"))
    health_app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

# Handle mentions
@slack_app.event("app_mention")
def handle_mention(event, say, client):
    user_question = event["text"]
    channel = event["channel"]
    ts = event["ts"]

    try:
        # Send immediate acknowledgment
        thinking_msg = client.chat_postMessage(
            channel=channel,
            thread_ts=ts,
            text=":hourglass_flowing_sand: Thinking..."
        )
    except Exception as e:
        print(f"Error posting thinking message (mention): {e}")
        # Can't post to channel, silently fail
        return

    try:
        # Call LiteLLM
        response = llm_client.chat.completions.create(
            model=MODEL_NAME,
            max_tokens=2000,
            messages=[
                {"role": "system", "content": KNOWLEDGE_BASE},
                {"role": "user", "content": user_question}
            ]
        )

        # Get response content and truncate if too long
        response_text = response.choices[0].message.content

        # Slack limit is 40,000 chars, but be conservative
        # With max_tokens=2000, response should be ~8000 chars max
        # Use 10,000 to be extra safe
        MAX_MESSAGE_LENGTH = 10000
        if len(response_text) > MAX_MESSAGE_LENGTH:
            response_text = response_text[:MAX_MESSAGE_LENGTH] + "\n\n...\n\n_(Response truncated due to length. Please ask a more specific question.)_"

        # Update with actual response
        client.chat_update(
            channel=channel,
            ts=thinking_msg["ts"],
            text=response_text
        )
    except Exception as e:
        # Handle errors gracefully
        error_message = f"❌ Sorry, I encountered an error: `{str(e)[:500]}`\n\n"
        error_message += "This is usually temporary. Please try again in a moment, or reach out to #bor-write-eng if the issue persists."

        try:
            client.chat_update(
                channel=channel,
                ts=thinking_msg["ts"],
                text=error_message
            )
        except Exception as update_error:
            print(f"Error updating error message: {update_error}")

        print(f"Error handling mention: {e}")

# Handle direct messages
@slack_app.event("message")
def handle_message(event, say, client):
    # Ignore bot's own messages
    if event.get("bot_id"):
        return

    user_question = event["text"]
    channel = event["channel"]

    try:
        # Send immediate acknowledgment
        thinking_msg = client.chat_postMessage(
            channel=channel,
            text=":hourglass_flowing_sand: Thinking..."
        )
    except Exception as e:
        print(f"Error posting thinking message (DM): {e}")
        # Can't post to channel, silently fail
        return

    try:
        # Call LiteLLM
        response = llm_client.chat.completions.create(
            model=MODEL_NAME,
            max_tokens=2000,
            messages=[
                {"role": "system", "content": KNOWLEDGE_BASE},
                {"role": "user", "content": user_question}
            ]
        )

        # Get response content and truncate if too long
        response_text = response.choices[0].message.content

        # Slack limit is 40,000 chars, but be conservative
        # With max_tokens=2000, response should be ~8000 chars max
        # Use 10,000 to be extra safe
        MAX_MESSAGE_LENGTH = 10000
        if len(response_text) > MAX_MESSAGE_LENGTH:
            response_text = response_text[:MAX_MESSAGE_LENGTH] + "\n\n...\n\n_(Response truncated due to length. Please ask a more specific question.)_"

        # Update with actual response
        client.chat_update(
            channel=channel,
            ts=thinking_msg["ts"],
            text=response_text
        )
    except Exception as e:
        # Handle errors gracefully
        error_message = f"❌ Sorry, I encountered an error: `{str(e)[:500]}`\n\n"
        error_message += "This is usually temporary. Please try again in a moment, or reach out to #bor-write-eng if the issue persists."

        try:
            client.chat_update(
                channel=channel,
                ts=thinking_msg["ts"],
                text=error_message
            )
        except Exception as update_error:
            print(f"Error updating error message: {update_error}")

        print(f"Error handling message: {e}")

if __name__ == "__main__":
    # Start health check server in background thread
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    print(f"🏥 Health check server running on port {os.environ.get('HEALTH_PORT', '8080')}")

    # Note: Skip startup LLM test - will verify on first real request
    # This allows bot to start even if model name needs adjustment
    print(f"📋 Using model: {MODEL_NAME}")
    print("⏭️  Skipping startup LLM test - will verify on first message")

    # Print environment variables for debugging
    print(f"SLACK_APP_TOKEN: {os.environ.get('SLACK_APP_TOKEN', 'NOT SET')}")
    print(f"SLACK_BOT_TOKEN: {os.environ.get('SLACK_BOT_TOKEN', 'NOT SET')}")
    print(f"LITELLM_DEVELOPER_KEY: {os.environ.get('LITELLM_DEVELOPER_KEY', 'NOT SET')}")

    # Start Socket Mode
    handler = SocketModeHandler(slack_app, os.environ["SLACK_APP_TOKEN"])
    health_status["slack_connected"] = True
    health_status["ready"] = True
    print("⚡️ Ledger Bot is running in Socket Mode!")
    handler.start()
