import capsolver

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
        token = solution['gRecaptchaResponse']
        print("Recaptcha Token:", token)
        return token
    except Exception as e:
        print("Error solving recaptcha:", e)
        return 500
    
    recaptcha()