import requests
import json

# Configuration
api_key = "CAP-BF3A913B93C1406DB8D4772118D2E44694DF0EB9DD657FF38C5A5C30712159C7"
website_url = "https://www.coursehero.com/"
reese_url = "https://www.coursehero.com/Ifainesse-What-mine-Alasterd-the-How-I-haile-Lad"
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0'

session = requests.Session()

def get_reese84_solution():
    """Get reese84 solution from Capsolver API"""
    payload = {
        "clientKey": api_key,
        "task": {
            "type": "AntiImpervaTaskProxyLess",
            "reeseScriptUrl": reese_url,
            "websiteURL": website_url
        }
    }
    
    print("Sending task to Capsolver...")
    res = requests.post("https://api.capsolver.com/createTask", json=payload)
    
    # Save raw create task response
    with open("capsolver_create_task_response.txt", "w") as file:
        file.write(res.text)
    
    # Save formatted JSON response
    with open("capsolver_create_task.json", "w") as file:
        file.write(json.dumps(res.json(), indent=4))
    
    resp = res.json()
    task_id = resp.get("taskId")
    if not task_id:
        print("Failed to create task:", res.text)
        return None
    
    print(f"Got taskId: {task_id} / Getting result...")
    
    while True:
        payload = {"clientKey": api_key, "taskId": task_id}
        res = requests.post("https://api.capsolver.com/getTaskResult", json=payload)
        
        # Save raw get task result response
        with open("capsolver_get_result_response.txt", "w") as file:
            file.write(res.text)
        
        # Save formatted JSON response
        with open("capsolver_get_result.json", "w") as file:
            file.write(json.dumps(res.json(), indent=4))
        
        resp = res.json()
        status = resp.get("status")
        
        if status == "ready":
            solution = resp.get("solution", "")
            # Save the solution as raw text
            with open("capsolver_solution.txt", "w") as file:
                if isinstance(solution, dict):
                    file.write(json.dumps(solution))
                else:
                    file.write(str(solution))
            
            # Save the formatted JSON solution
            with open("capsolver_solution.json", "w") as file:
                file.write(json.dumps(solution, indent=4))
                
            # Save the reese84Payload separately
            if "reese84Payload" in solution:
                with open("reese84_payload.txt", "w") as file:
                    file.write(solution["reese84Payload"])
                    
            # Save the userAgent separately
            if "userAgent" in solution:
                with open("user_agent.txt", "w") as file:
                    file.write(solution["userAgent"])
                    
            return solution
            
        if status == "failed" or resp.get("errorId"):
            print("Solve failed! response:", res.text)
            return None

def post_reese_payload(payload, user_agent):
    """Post the payload to get the reese84 token"""
    post_url = reese_url
    if "?" not in post_url:
        post_url = f"{post_url}?d=www.coursehero.com"
    
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
        "user-agent": user_agent
    }
    
    # Save the request headers
    with open("reese_request_headers.txt", "w") as file:
        file.write(json.dumps(headers, indent=4))
    
    # Save the payload being sent
    with open("reese_request_payload.txt", "w") as file:
        file.write(payload)
    
    resp = session.post(post_url, headers=headers, data=payload, verify=False)
    
    # Save the raw response
    with open("reese_post_response.txt", "w") as file:
        file.write(resp.text)
    
    if resp.status_code != 200:
        print("post reese84-payload failed:", resp.status_code, resp.text)
        return None
    
    data = resp.json()
    
    # Save the formatted JSON response
    with open("reese_post_response.json", "w") as file:
        file.write(json.dumps(data, indent=4))
    
    token = data.get('token')
    
    if not token:
        print("post reese84-payload failed:", resp.status_code, resp.text)
        return None
    
    # Save reese84 token
    with open("reese84_token.txt", "w") as file:
        file.write(token)
    
    return token

def main():
    # Step 1: Get the solution from Capsolver
    print("Step 1: Getting solution from Capsolver...")
    solution = get_reese84_solution()
    if not solution:
        return
    
    # Step 2: Post the payload to get the reese84 token
    print("Step 2: Posting payload to get reese84 token...")
    reese84_token = post_reese_payload(solution["reese84Payload"], solution["userAgent"])
    if not reese84_token:
        return
    
    print("Success! Reese84 token obtained:", reese84_token[:30] + "..." if len(reese84_token) > 30 else reese84_token)
    print("All data has been saved to text files.")

if __name__ == '__main__':
    main()
