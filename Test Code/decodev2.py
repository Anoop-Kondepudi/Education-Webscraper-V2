import re

def extract_tokens_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    print("[*] File loaded.")

    # 1. Find obfuscated array
    array_match = re.search(r'var\s+(_0x[a-f0-9]+)\s*=\s*\[(.*?)\];', html, re.DOTALL)
    string_list = []
    array_var = None
    if array_match:
        array_var = array_match.group(1)
        raw_array = array_match.group(2)
        string_list = [s.strip().strip('"').strip("'") for s in raw_array.split(',')]
        print(f"[+] Found obfuscated array: {array_var} with {len(string_list)} values.")

    # 2. Look for token: some_var (literal reference)
    token_key_ref = re.search(r"'token'\s*:\s*([_0x[a-f0-9]+)", html)
    if not token_key_ref:
        print("[x] No 'token' variable reference found.")
        return

    token_var = token_key_ref.group(1)
    print(f"[+] Found token assigned to variable: {token_var}")

    # 3. Look for: var token_var = 'actual_value';
    var_def = re.search(rf"var\s+{re.escape(token_var)}\s*=\s*['\"]([^'\"]+)['\"]", html)
    if var_def:
        token_value = var_def.group(1)
        print(f"[✓] Resolved token: {token_var} = {token_value}")
    else:
        print(f"[x] Could not resolve value of {token_var}")

# Run it
if __name__ == "__main__":
    extract_tokens_from_file("coursehero_page.html")
