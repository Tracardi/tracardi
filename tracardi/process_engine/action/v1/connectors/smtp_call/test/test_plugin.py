import os
from dotenv import load_dotenv

from tracardi.process_engine.action.v1.connectors.smtp_call.plugin import SmtpDispatcherAction
from tracardi_plugin_sdk.service.plugin_runner import run_plugin

load_dotenv()

init = {
    'source': {
        'id': '89905cda-6374-496f-9b66-3c1d740ffc41'
    },
    'message': {
        "send_to": os.getenv('TO'),
        "send_from": os.getenv('FROM'),
        "reply_to": "some@main.com",
        "title": "Title",
        "message": "Message: {{payload@test}}"
    }
}


payload = {"test": "Hello"}

result = run_plugin(SmtpDispatcherAction, init, payload)
print(result)
print(result.console.__dict__)
