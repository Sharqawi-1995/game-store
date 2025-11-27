import requests
from django.conf import settings


def verify_email(email):
    api_key = settings.EMAIL_API_KEY
    url = f"https://api.zerobounce.net/v2/validate?api_key={api_key}&email={email}"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        # Debugging
        print("ZeroBounce response:", data)

        # ZeroBounce returns status like: valid, invalid, catch-all, unknown, spamtrap, abuse, do_not_mail
        status = data.get("status", "").lower()

        # Accept only if status is 'valid'
        return status == "valid"

    except Exception as e:
        print("ZeroBounce API error:", e)
        # Fallback: simple regex check
        import re
        return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None
