import re

# Path to your local HTML file
file_path = "/Users/anoopkondepudi/Downloads/[FREE] What patterns do you notice in the time series plot of average annual airfare from 2004 to 2018_ A. - brainly.com(2).html"
output_file = "clean_button_structure.txt"  # Output file to store results

# Read the HTML file
with open(file_path, "r", encoding="utf-8") as file:
    html_content = file.read()

# Find the #answer-switch button and its closest parent div (limiting extra content)
match = re.search(
    r'(<div[^>]*>.*?(<button[^>]*id=["\']answer-switch["\'][^>]*>.*?</button>).*?</div>)',
    html_content,
    re.DOTALL
)

if match:
    parent_div = match.group(1)  # Full div containing the button
    button_html = match.group(2)  # Only the button itself
else:
    parent_div = "❌ No parent div found for #answer-switch."
    button_html = "❌ #answer-switch button NOT found."

# Save results to a file
with open(output_file, "w", encoding="utf-8") as out_file:
    out_file.write("✅ Extracted #answer-switch Button:\n")
    out_file.write(button_html + "\n\n")
    out_file.write("🔍 Closest Parent Div:\n")
    out_file.write(parent_div + "\n")

print(f"✅ Saved refined button data to: {output_file}")