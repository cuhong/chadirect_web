import os
import ssl
import urllib

from django.conf import settings

from slack import WebClient
from slack.errors import SlackApiError
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
# response = urllib.request.urlopen(requests, data=data.encode('utf-8'), context=context)
client = WebClient(token="xoxb-374502713361-1872663431362-MQkrz8v5GcMFMg4yldfPD7bC")

try:
    response = client.chat_postMessage(
        channel='#휴대전화보험-운영',
        text="Hello world!")
    assert response["message"]["text"] == "Hello world!"
except SlackApiError as e:
    a = e
    # You will get a SlackApiError if "ok" is False
    assert e.response["ok"] is False
    assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
    print(f"Got an error: {e.response['error']}")


from slacker import Slacker

slack = Slacker("fEQ1M3WOgaLtOXL1aO37BGRb", incoming_webhook_url="https://hooks.slack.com/services/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")

# Send a message to #general channel
slack.chat.post_message('#휴대전화보험-운영', 'Hello fellow slackers!')