from requests_html import HTMLSession
import re

url = "https://www.coursehero.com/Ifainesse-What-mine-Alasterd-the-How-I-haile-Lad"
params = {"d": "www.coursehero.com"}

session = HTMLSession()
response = session.get(url, params=params)

# Render JavaScript (wait for page to finish loading)
response.html.render(timeout=20, sleep=5)

# Save rendered HTML for inspection
with open("rendered_output.html", "w", encoding="utf-8") as f:
    f.write(response.html.html)

# Extract tokens from rendered HTML
pattern = re.compile(r'["\'](token|previous_token)["\']\s*:\s*["\']?([a-zA-Z0-9_\-\.]+)["\']?', re.IGNORECASE)
matches = pattern.findall(response.html.html)

if matches:
    for name, value in matches:
        print(f"{name}: {value}")
else:
    print("No tokens found.")