from uuid import uuid4

from .generate_pii import fake_emails

email_2_session = {email: [str(uuid4()) for _ in range(1, 10)] for email in fake_emails}


def get_session_for_email(email):
    return email_2_session.get(email, [str(uuid4())])
