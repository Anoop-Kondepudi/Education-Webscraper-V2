import requests
import re
import mimetypes
import random
import string
import capsolver
import base64
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Put in tutor question link here
link = 'https://www.coursehero.com/tutors-problems/Computer-Science/65960998-1-what-formulas-do-I-need-to-use-to-complete-step-e-2-what/'

def recaptcha():
    try:
        capsolver.api_key = "CAP-93BF0B9A68800E2D4F3CF7B585853A90"  # add capsolver id
        solution = capsolver.solve({
            "type": "ReCaptchaV2EnterpriseTaskProxyLess",
            "websiteURL": "https://www.coursehero.com",
            "websiteKey": "6Lee8D4bAAAAAC3mq6sHfelhKEZJEk667GmJOy4m",
            "anchor": "",
            "apiDomain": "www.recaptcha.net",
            "pageAction": "login"
        })
        return solution['gRecaptchaResponse']
    except Exception as e:
        print("Error solving recaptcha:", e)
        return 500

session = requests.Session()

proxies = {
    'http': 'http://lho7SIZFaRh9:1inYc0RRMvYs@144.229.117.13:1337',  # add your proxies
    'https': 'http://lho7SIZFaRh9:1inYc0RRMvYs@144.229.117.13:1337'  # add your proxies
}

useragent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'  # add user agent

# -------------------------------------------------------
# Updated Incapsula endpoint using RapidAPI instead of hwclutch.com
# -------------------------------------------------------
url = "https://imperva-incapsula-reese84.p.rapidapi.com/solve"
payload = {
    "scriptUrl": "https://www.coursehero.com",  # adjust the scriptUrl if needed
    "userAgent": useragent
}
headers_incap = {
    "x-rapidapi-key": "dad96ecfd5msh31bbd311c70f48ap1ae593jsna24d1a6e1d32",
    "x-rapidapi-host": "imperva-incapsula-reese84.p.rapidapi.com",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers_incap)
post_data = response.json()['postdata']
# -------------------------------------------------------

headers = {
    "Accept": "application/json; charset=utf-8",
    "Content-Type": "text/plain; charset=utf-8",
    "Origin": "https://www.coursehero.com",
    "Referer": "https://www.coursehero.com/",
    "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
    "sec-ch-ua-mobile": "?0",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "upgrade-insecure-requests": "1",
    "user-agent": useragent
}

# Using the post_data obtained from the updated endpoint
response = session.post('https://www.coursehero.com/Ifainesse-What-mine-Alasterd-the-How-I-haile-Lad?d=www.coursehero.com',
                        headers=headers, data=post_data, proxies=proxies)
response_json = response.json()
reese84_token = response_json["token"]

session.cookies.set("reese84", reese84_token, domain='www.coursehero.com', path='/', secure=True)

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'no-cache',
    'Dnt': '1',
    'Referer': 'https://www.coursehero.com/',
    'sec-ch-ua': "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': useragent
}

response = session.get('https://www.coursehero.com/login/?login_user_type=&ref=login', headers=headers, proxies=proxies)
print(response)

recaptcha_token = 500
while recaptcha_token == 500:
    recaptcha_token = recaptcha()

data = {
    'password': 'pzkudvqxdt@ibolinva.com',  # ch account
    'email': 'pzkudvqxdt@ibolinva.com',       # ch account
    'submit': 'true',
    'remember_me': '1',
    'g-recaptcha-response': recaptcha_token
}

headers = {
    'accept': 'application/json',
    # 'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://www.coursehero.com',
    'priority': 'u=1, i',
    'referer': 'https://www.coursehero.com/login/?login_user_type=&ref=login',
    'sec-ch-ua': "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': useragent,
    'x-newrelic-id': 'Ug8CUVVbGwIDUlVUBgkGVg=='
}

response = session.post('https://www.coursehero.com/ajax/login.php', headers=headers, data=data, proxies=proxies)

if response.status_code == 200:
    if "https://www.coursehero.com/tutors-problems/" in link:
        documentID = re.findall("/(.+?)-.*?/", link)[1]
        
        resp = session.get('https://www.coursehero.com/api/v1/users/unlocks/uploads/', headers=headers, proxies=proxies, verify=False)
        unlocksJSON = resp.json()

        if unlocksJSON['unlocks_remaining'] > 0:
            resp = session.get("https://www.coursehero.com/api/v1/questions/{}/".format(documentID), headers=headers, proxies=proxies, verify=False)
            
            if resp.status_code == 200:
                documentCheck = resp.json()
                if documentCheck['question']['derived_question_status'] != "Cancelled" or documentCheck['question']['derived_question_status'] != "Requires Edit":
                    resp = session.post("https://www.coursehero.com/api/v1/users/unlocks/content/question/id/{}/".format(documentID), headers=headers, proxies=proxies, verify=False)
                    unlockTutorQ = resp.json()

                    resp = session.get("https://www.coursehero.com/api/v1/questions/{}/".format(documentID), headers=headers, proxies=proxies, verify=False)
                    
                    if resp.status_code == 200:
                        getDocument = resp.json()
                        answer = None
                        question = ""
                        questionAttachmentHTML = ""
                        answerAttachmentHTML = ""
                        for thread in getDocument['threads']:
                            if thread['type'] == "question":
                                question = thread['display_text'].replace("\\", '')
                                if len(thread['attachment']) > 0:
                                    questionID = thread['question_id']
                                    for attachment in thread['attachment']:
                                        attachmentID = attachment['question_attachment_id']
                                        attachmentFileName = attachment['users_filename']
                                        resp = session.get("https://www.coursehero.com/pdf/attachment/{aID}/?question_id={qID}"
                                                           .format(aID=attachmentID, qID=questionID), headers=headers, proxies=proxies, verify=False)
                                        print(attachmentID)
                                        print(questionID)
                                        if resp.status_code == 200:
                                            extension = mimetypes.guess_extension(resp.headers.get('content-type', ''))
                                            if extension is None:
                                                extension = '.xlsx'
                                                
                                            documentFile = 'attachment{}'.format(extension)
                                            documentContent = resp.content
                                            contentType = resp.headers.get('content-type', '')
                                            if contentType.startswith('image/'):
                                                base64_image = base64.b64encode(documentContent).decode('utf-8')
                                                image_extension = extension[1:]
                                                image_tag = f'<img src="data:image/{image_extension};base64,{base64_image}" alt="{attachmentFileName}" />'
                                                questionAttachmentHTML += image_tag
                                            elif contentType == 'application/pdf':
                                                base64_pdf = base64.b64encode(documentContent).decode('utf-8')
                                                pdf_tag = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="600" height="400" alt="{attachmentFileName}"></iframe>'
                                                questionAttachmentHTML += pdf_tag
                                            else:
                                                questionAttachmentHTML += '<form action="{}" method="get" target="_blank"><button class="btn"><i class="fa fa-download"></i> Download {}</button></form>'.format(documentFile, attachmentFileName)
                            elif thread['type'] == "answer":
                                answer = thread['display_text'].replace("\\", '')
                                if len(thread['attachment']) > 0:
                                    questionID = thread['question_id']
                                    for attachment in thread['attachment']:
                                        attachmentID = attachment['question_attachment_id']
                                        attachmentFileName = attachment['users_filename']
                                        resp = session.get("https://www.coursehero.com/pdf/attachment/{aID}/?question_id={qID}"
                                                           .format(aID=attachmentID, qID=questionID), headers=headers, proxies=proxies, verify=False)
                                        if resp.status_code == 200:
                                            extension = mimetypes.guess_extension(resp.headers.get('content-type', ''))
                                            if extension is None:
                                                extension = '.xlsx'
                                            documentFile = 'attachment{}'.format(extension)
                                            documentContent = resp.content
                                            contentType = resp.headers.get('content-type', '')
                                            if contentType.startswith('image/'):
                                                base64_image = base64.b64encode(documentContent).decode('utf-8')
                                                image_extension = extension[1:]
                                                image_tag = f'<img src="data:image/{image_extension};base64,{base64_image}" alt="{attachmentFileName}" />'
                                                answerAttachmentHTML += image_tag
                                            elif contentType == 'application/pdf':
                                                base64_pdf = base64.b64encode(documentContent).decode('utf-8')
                                                pdf_tag = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="600" height="400" alt="{attachmentFileName}"></iframe>'
                                                answerAttachmentHTML += pdf_tag
                                            else:
                                                answerAttachmentHTML += '<form action="{}" method="get" target="_blank"><button class="btn"><i class="fa fa-download"></i> Download {}</button></form>'.format(documentFile, attachmentFileName)

                        if answer is not None:
                            startingHTML = ("<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width, initial-scale=1'>"
                                            "<link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'>"
                                            "<style>.collapsible { background-color: #777; color: white; cursor: pointer; padding: 18px; width: 100%; border: none; text-align: left; outline: none; font-size: 15px; }"
                                            ".active, .collapsible:hover { background-color: #555; }"
                                            ".content { padding: 0 18px; display: none; overflow: hidden; background-color: #f1f1f1; }"
                                            ".btn { background-color: DodgerBlue; border: none; color: white; padding: 12px 30px; cursor: pointer; font-size: 20px; }"
                                            ".btn:hover { background-color: RoyalBlue; }</style></head><body>"
                                            "<h2>CH Tutor Question</h2><p>Question:</p><button type='button' class='collapsible'>Open Question</button>"
                                            "<div class='content'>")
                            answerHTML = "</div><p>Answer & Explanation</p><button type='button' class='collapsible'>Open Answer</button><div class='content'>"
                            endingHTML = ("</div><script>var coll = document.getElementsByClassName('collapsible');var i;"
                                          "for (i = 0; i < coll.length; i++) { coll[i].addEventListener('click', function() {"
                                          "this.classList.toggle('active'); var content = this.nextElementSibling;"
                                          "if (content.style.display === 'block') { content.style.display = 'none'; } else {"
                                          "content.style.display = 'block'; } });}</script></body></html>")
                            html = startingHTML + question + questionAttachmentHTML + answerHTML + answer + answerAttachmentHTML + endingHTML                                    
                            with open("answer.html", "w", encoding='utf-8') as f:
                                f.write(html)
                            print('unlocked')
                        else:
                            print('not answered')
                else:
                    print('not answered')
