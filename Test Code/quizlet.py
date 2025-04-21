import requests
from bs4 import BeautifulSoup as scrapy
from urllib.parse import urlparse
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, request, send_from_directory
import os
import json

#app flask mak api function
app = Flask(__name__)

# Create the ThreadPoolExecutor outside the fast_download function.
executor = ThreadPoolExecutor()


@app.route('/', methods=['GET'])
def home():
  return """<!DOCTYPE html>
<html>
<head>
    <style>
        /* CSS styles */
        body {
            font-family: Arial, sans-serif;
            background-color: #f2f2f2;
            margin: 0;
            padding: 20px;
        }

        h1 {
            color: #333;
            font-size: 24px;
        }

        p {
            color: #666;
            font-size: 16px;
        }

        .container {
            max-width: 600px;
            margin: 0 auto;
            background-color: #fff;
            border-radius: 4px;
            padding: 30px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }

        .api-link {
            color: #007bff;
            text-decoration: none;
        }

        .api-link:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>How to Use this API?</h1>
        <p>
            To use the API, make a GET request to the following URL:
            <br>
            <a href="https://webpage.com/apii?url=(pdf_url)" class="api-link">https://webpage.com/apii?url=(pdf_url)</a>
        </p>
        <p>
            Replace "(pdf_url)" in the URL with the actual URL of the PDF file you want to retrieve data from.
        </p>
    </div>
</body>
</html>
"""


def quizlet(url):
  try:
    cookies = {
        '__cf_bm': 'Kc4X5pu.VRyQJ0wwke_xwdHVCc9IfTMpK1GU10.O1fg-1743981118-1.0.1.1-zQymxotp7s1iO_BgWpN2FhrOMdh9_Xc5vKBdOh4x.zP9Qv_OxF2wX1NQQT0AYrPyQ51pIv.pHXYNxwv28f0Feqml7XlgTLtJb_wBHlSslLc',
        '_cfuvid': 'eevGiKSWm4P7b_jxB5X9YQVW.ZopVJGa94z7VpRAJQU-1743979832400-0.0.1.1-604800000',
        '_ga': 'GA1.1.123676442.1733531507',
        '_ga_BGGDEZ0S21': 'GS1.1.1734587916.5.0.1734587916.0.0.0',
        '_ga_VG8TWT63ZN': 'GS1.1.1734587916.5.0.1734587916.0.0.0',
        '_px3': '9d26e0be8a664e81ad47a01169cba6f2ea1fc30b05e0dbd511667af9e4aad52f:I9DG1OfwR6EpR36GqSbpPPbt/PogQ7ll/D4A5bXBjGpufIyCF+xXqW0xzKAVlSd5yKRAxkY8569HOw5kaAa8fw==:1000:QEVmpxg2+n4vnhp2DUIdSas7YGE8zc8HDF2B1/SaPEKU3VFUXnv1lh0izUtxdGmLiO+GeJILb1zUVjjpWb4+lDYppkTZ1aQc2COJzpJm7+jWXBMeJef/7/jm+LGPQTglv3RUd5faLVbZG2gWKtMBBgNx9taIaPzvGKMHjMi7jp+9URXTmviLYgmPmBN9GVcBr8O7leWKeDx8GevnCdmCOfAjHCZQz1s8LMKyJiGBUhM=',
        '_pxvid': '9e1e7d65-b432-11ef-bbe7-73f2dc2a26da',
        'ab.storage.deviceId.6f8c2b67-8bd5-42f6-9c5f-571d9701f693': '%7B%22g%22%3A%221b298de1-3a86-2ed9-7e8d-92be3b9c1eff%22%2C%22c%22%3A1695839297783%2C%22l%22%3A1743979835110%7D',
        'ab.storage.sessionId.6f8c2b67-8bd5-42f6-9c5f-571d9701f693': '%7B%22g%22%3A%2206e4570e-205e-34c4-c47e-71c5b0a1eaa9%22%2C%22e%22%3A1743982278989%2C%22c%22%3A1743979835109%2C%22l%22%3A1743980478989%7D',
        'ab.storage.userId.6f8c2b67-8bd5-42f6-9c5f-571d9701f693': '%7B%22g%22%3A%22178535731%22%2C%22c%22%3A1741623539373%2C%22l%22%3A1743979835111%7D',
        'OptanonConsent': 'isGpcEnabled=0&datestamp=Thu+Jun+13+2024+14%3A11%3A59+GMT-0700+(Pacific+Daylight+Time)&version=202310.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=7b2f484e-0478-4cc5-b604-de14c54698cc&interactionCount=1&landingPath=https%3A%2F%2Fquizlet.com%2F534472604%2Fsilicon-valley-high-school-spanish-2-part-1-unit-2-flash-cards%2F&GPPCookiesCount=1&groups=C0001%3A1%2CN01%3A1%2CC0002%3A1%2CC0004%3A1',
        'OTGPPConsent': 'DBABBg~BUoAAAKA.QA',
        'qltj': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzM4NCJ9.eyJ2cmYiOjAsInN1YiI6IjE3ODUzNTczMSIsInNpcCI6IjE3My4xNi4xNDkuMTI0IiwiaXNzIjoicXVpemxldC5jb20iLCJlbSI6Implbm50ZWxAaG90bWFpbC5jb20iLCJjdHMiOjE1OTQ2OTU0NjQsImF1ZCI6InYzIiwiYWNjIjoyfQ.qaJPIHm5bk_DwYS2hlyNFEC8D5Y_HCNhOJLJmBcStIS2aAUJeZLxP0UT3vfPwuUz',
        'sp': 'a73271cc-1e39-426a-8427-68ffa59f1bee',
        '_pxhd': 'e5c469c2f571680edc25049bfe44faee97cb1b9fdc79b469ed6e79bb66e9e6d4:9e1e7d65-b432-11ef-bbe7-73f2dc2a26da',
        '_sp_id.424b': '04588bd2-8fcf-4d3b-ab79-03d6aeac176b.1695839215.17.1743980570.1741873877.7f4754f6-28f7-46f9-b702-59f0dc4518bb.757355e5-a8ce-4c68-a574-9f1cc8729871.183d5219-71b1-41c8-9c31-833a89fa6ba2.1743979834193.21',
        '_sp_ses.424b': '*',
        'app_session_id': '9c5d5a6e-b4da-4eaa-843e-66a50d5fe9f6',
        'days_since_last_visit': '14',
        'fs': 'so3lgo',
        'has_seen_logged_in_home_page_timestamp': '1743979834705',
        'is_side_nav_expanded': 'false',
        'OneTrustWPCCPAGoogleOptOut': 'false',
        'qi5': '8bn5bbtyuwzi%3AL3mGaT623.EmjOqNryNB',
        'qlts': '1_KayNFupJMCdfrhaTDt345Nuz34M60h5nMly3cCC-Ij5MzCk-YWg0IatTdlm9dwmct8B6ItxPxjqwNw',
        'qtkn': 'udCtGA8csTQkPKqkTEr8vN',
        'session_landing_page': 'StudyFeed%2FlatestActivity',
        'set_has_seen_study_reengagement': 'true',
        'set_num_visits_per_set': '6',
        'usprivacy': '1YNN',
    }

    headers = {
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-arch': '""',
        'sec-ch-ua-platform': '"macOS"',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-full-version-list': '"Google Chrome";v="119.0.6045.163", "Chromium";v="119.0.6045.163", "Not?A_Brand";v="24.0.0.0"',
        'dnt': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://quizlet.com/',
        'accept-language': 'en-US,en;q=0.9',
    }

    response = requests.get(
        url,
        cookies=cookies,
        headers=headers,
    )
    print(response.status_code)
    #print(response.text)
    soup = scrapy(response.content, 'html.parser')
    if 'https://quizlet.com/explanations/questions/' in url:
      answerhtml = soup.find('div', '</div>', class_="QuestionDetailsPage")
    elif 'https://quizlet.com/explanations/textbook-solutions/' in url:
      answerhtml = soup.find('div', '</div>', class_="ExerciseDetailPage")
    url_head = "https://nx.aba.vg/quizlet/head/head.html"
    head = requests.get(url_head)
    souphead = scrapy(head.content, 'html.parser')
    headhtml = str(souphead.prettify())
    if answerhtml is None:
      return '<p>Please try again later</p>'
    else:
      answerhtmlfile = f'<html>{headhtml}<body></body>{answerhtml}</html>'
      return answerhtmlfile
  except Exception as e:
    print(f"An error occurred: {e}")


@app.route('/apii', methods=['GET'])
def process_slideshare_api():
  try:
    with app.app_context():
      url = request.args.get('url')
      if url:
        result = quizlet(url)
        return result
      else:
        return "Error: Missing 'url' parameter.", 400
  except Exception as e:
    print(f"An error occurred: {e}")


if __name__ == '__main__':
  app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))