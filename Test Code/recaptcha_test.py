import capsolver

def get_recaptcha_token():
    try:
        # Set your capsolver API key
        capsolver.api_key = "CAP-BF3A913B93C1406DB8D4772118D2E44694DF0EB9DD657FF38C5A5C30712159C7"
        
        # Request a solution for the reCAPTCHA challenge using the provided parameters
        solution = capsolver.solve({
            "type": "ReCaptchaV2EnterpriseTaskProxyLess",
            "websiteURL": "https://www.coursehero.com",
            "websiteKey": "6Lee8D4bAAAAAC3mq6sHfelhKEZJEk667GmJOy4m",
            "apiDomain": "www.recaptcha.net",
            "pageAction": "login"
        })
        
        # Extract the reCAPTCHA token from the solution
        token = solution.get("gRecaptchaResponse")
        print("Recaptcha Token:", token)
        return token

    except Exception as e:
        print("Error getting recaptcha token:", e)
        return None

if __name__ == "__main__":
    get_recaptcha_token()
