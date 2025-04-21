#!/usr/bin/env python3
import os
import sys
import time

# Set of diagnostic scripts to run
DIAGNOSTIC_SCRIPTS = [
    "proxy_tester.py",       # Check if proxy is working
    "hwclutch_discover.py",  # Check if hwclutch domain is up and which endpoints work
    "hwclutch_tester.py",    # Test the hwclutch/incap endpoint specifically
    "hwclutch_alternative.py" # Try alternative API configurations
]

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(text):
    """Print a formatted header"""
    width = 80
    print("\n" + "=" * width)
    print(text.center(width))
    print("=" * width + "\n")

def run_script(script_name):
    """Run a Python script and wait for it to complete"""
    print_header(f"Running {script_name}")
    
    # Check if script exists
    if not os.path.exists(script_name):
        print(f"Error: {script_name} not found.")
        return False
    
    # Run the script
    exit_code = os.system(f"{sys.executable} {script_name}")
    
    if exit_code != 0:
        print(f"\nScript {script_name} returned exit code {exit_code}")
    
    input("\nPress Enter to continue to the next diagnostic...\n")
    return exit_code == 0

def main():
    clear_screen()
    print_header("CourseHero Script Diagnostic Tool")
    
    print("This tool will run a series of diagnostics to determine why the original script is failing.")
    print("Each diagnostic will provide specific information to help identify the problem.")
    print("\nYou will need to review the output of each diagnostic and press Enter to continue to the next one.")
    
    input("\nPress Enter to begin...\n")
    
    # Run each diagnostic script in order
    for script in DIAGNOSTIC_SCRIPTS:
        clear_screen()
        run_script(script)
    
    # Final summary and recommendations
    clear_screen()
    print_header("Diagnostic Summary")
    
    print("Based on the diagnostics that have been run, here are the possible issues:")
    print()
    print("1. The hwclutch.com service may be down or have changed its API")
    print("   - If the hwclutch_discover.py script showed the domain is unreachable")
    print("   - If the hwclutch_tester.py script couldn't connect to the /incap endpoint")
    print()
    print("2. The proxy configuration may be invalid or expired")
    print("   - If the proxy_tester.py script showed failures with the proxy")
    print("   - If connections worked without the proxy but failed with it")
    print()
    print("3. The API format or key may have changed")
    print("   - If hwclutch_alternative.py found a working configuration different from the original")
    print()
    print("Recommended solutions:")
    print("1. If hwclutch.com is down, you'll need to find an alternative service or method")
    print("2. If the proxy is invalid, update the proxy configuration in the original script")
    print("3. If the API has changed, update the API key or request format based on what worked")
    print()
    
    print("To modify the original script based on these findings:")
    print("1. Open zelly_unlock_original.py")
    print("2. Update the proxy settings if they're not working")
    print("3. If hwclutch.com is completely down, you may need a different approach")
    print("4. If hwclutch.com works with different parameters, update the API call")
    
    print("\nDiagnostic process complete.\n")

if __name__ == "__main__":
    main() 