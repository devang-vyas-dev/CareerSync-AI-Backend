import requests
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

# YOUR TEST USER
email = "test@test.com"  # <-- put your test email here
password = "Test@12345"  # <-- put your password here

headers = {
    "apikey": key,
    "Content-Type": "application/json"
}

# This is the direct Supabase Auth API call
response = requests.post(
    f"{url}/auth/v1/token?grant_type=password",
    headers=headers,
    json={"email": email, "password": password}
)

print(response.status_code)
print(response.text)

if response.status_code == 200:
    data = response.json()
    print("\n--- SUCCESS ---")
    print("ACCESS TOKEN:", data["access_token"])
    print("USER ID:", data["user"]["id"])
else:
    print("\nFailed. Check email/password in Supabase > Authentication > Users")