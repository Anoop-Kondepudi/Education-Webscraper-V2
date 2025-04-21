import capsolver
import time
from datetime import datetime

def get_recaptcha_token():
    print(f"[{datetime.now()}] Solving reCAPTCHA...")
    
    try:
        # Set your CapSolver API key
        capsolver.api_key = "CAP-93BF0B9A68800E2D4F3CF7B585853A90"
        
        # Submit the captcha solving task
        solution = capsolver.solve({
            "type": "ReCaptchaV2EnterpriseTaskProxyLess",
            "websiteURL": "https://www.coursehero.com",
            "websiteKey": "6Lee8D4bAAAAAC3mq6sHfelhKEZJEk667GmJOy4m",
            "apiDomain": "www.recaptcha.net",
            "pageAction": "login"
        })
        
        # Extract and return the token
        token = solution['gRecaptchaResponse']
        print(f"[{datetime.now()}] Successfully obtained reCAPTCHA token!")
        print(f"\nToken: {token}\n")
        return token
        
    except Exception as e:
        print(f"[{datetime.now()}] Error solving captcha: {e}")
        return None

if __name__ == "__main__":
    token = get_recaptcha_token()
    
    if token:
        print("\nPayload example:")
        payload = f"""{{
  "email": "pzkudvqxdt@ibolinva.com",
  "password": "pzkudvqxdt@ibolinva.com",
  "submit": "true",
  "remember_me": "1",
  "g-recaptcha-response": "{token}",
  "login_type": "Email",
  "device_type": "desktop"
}}"""
        print(payload)
    else:
        print("Failed to get token. Please try again.")