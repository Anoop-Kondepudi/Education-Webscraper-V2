# Install required: pip install tls_client
from tls_client import Session
import time

def brainly_scraper():
    cookies = {
        # Critical DataDome protection
        "datadome": "HKD9t92sDhTp3u66z9~fxZxwNfdyQ3ahmLBvcrd6AknDbbRatvlh6zEqeB6oHyqzomknnP_l1XK9d8cC_~e_1LTBRAdqO6ucqJf~_WxWMQsyn2MPkuQUfIpJU0Emz6rm",
        # Session identifier
        "Zadanepl_cookie[Token][Guest]": "PMMzuLaoUhL7TiR6txs5K2R2CjHhStuFQ02ZeIe7OyeeaKAmxz82qkkAPxYgonCyYJDWCVpVFnerbSf5",
        # Privacy compliance
        "_swb_consent_": "eyJvcmdhbml6YXRpb25Db2RlIjoiYnJhaW5seSIsInByb3BlcnR5Q29kZSI6IndlYnNpdGVfc21hcnRfdGFnIiwiZW52aXJvbm1lbnRDb2RlIjoicHJvZHVjdGlvbiIsImp1cmlzZGljdGlvbkNvZGUiOiJ0eCIsImlkZW50aXRpZXMiOnsic3diX3dlYnNpdGVfc21hcnRfdGFnIjoiOGUxYzhiZWMtYTQyOC00ZmI0LTlkODAtNGQ0NTZhNjczZTdjIn0sInB1cnBvc2VzIjp7ImFuYWx5dGljcyI6eyJsZWdhbEJhc2lzQ29kZSI6ImNvbnNlbnRfb3B0b3V0In0sImJlaGF2aW9yYWxfYWR2ZXJ0aXNpbmciOnsibGVnYWxCYXNpc0NvZGUiOiJjb25zZW50X29wdG91dCJ9LCJlc3NlbnRpYWxfc2VydmljZXMiOnsibGVnYWxCYXNpc0NvZGUiOiJkaXNjbG9zdXJlIn19LCJjb2xsZWN0ZWRBdCI6MTczOTQ4MTkyN30%3D"
    }

    headers = {
        "authority": "brainly.com",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "priority": "u=0, i",
        "sec-ch-ua": '"Chromium";v="125", "Not.A/Brand";v="24", "Google Chrome";v="125"',
        "sec-ch-ua-arch": '"arm"',
        "sec-ch-ua-bitness": '"64"',
        "sec-ch-ua-full-version-list": '"Chromium";v="125.0.6422.76", "Not.A/Brand";v="24.0.0.0", "Google Chrome";v="125.0.6422.76"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-ch-ua-platform-version": '"14.5.0"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    }

    # Configure TLS fingerprint
    session = Session(
        client_identifier="chrome_125",
        random_tls_extension_order=True,
        ja3_string="771,4865-4867-4866-49195-49199-52393-52392-49196-49200-49162-49161-49171-49172-51-57-47-53-10,0-23-65281-10-11-35-16-5-51-43-13-45-28-21,29-23-24-25-256-257,0",
        h2_settings={
            "HEADER_TABLE_SIZE": 65536,
            "MAX_CONCURRENT_STREAMS": 1000,
            "INITIAL_WINDOW_SIZE": 6291456,
            "MAX_HEADER_LIST_SIZE": 262144
        },
        h2_settings_order=["HEADER_TABLE_SIZE", "MAX_CONCURRENT_STREAMS", "INITIAL_WINDOW_SIZE", "MAX_HEADER_LIST_SIZE"],
        supported_signature_algorithms=["ECDSAWithP256AndSHA256", "PSSWithSHA256", "PKCS1WithSHA256"],
        supported_versions=["GREASE", "1.3", "1.2"],
        key_share_curves=["X25519", "P256"]
    )

    # Human-like delay
    time.sleep(1.2)
    
    response = session.get(
        "https://brainly.com/question/21951123",
        headers=headers,
        cookies=cookies,
        timeout_seconds=15
    )

    # Verification
    if "Answer verified by Brainly" in response.text:
        return response.text.split('data-testid="answer-content"')[1].split('</div>')[0]
    return f"Blocked (Status {response.status_code})"

print(brainly_scraper())