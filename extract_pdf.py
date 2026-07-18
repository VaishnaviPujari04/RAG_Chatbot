from pypdf import PdfReader
import re

reader = PdfReader("notes.pdf")

full_text = ""
for page in reader.pages:
    text = page.extract_text()
    full_text += text + " "

# Clean up: collapse any run of whitespace (spaces, newlines, tabs) into a single space
cleaned_text = re.sub(r'\s+', ' ', full_text).strip()

print(cleaned_text[:1000])
print(f"\n\nTotal characters after cleaning: {len(cleaned_text)}")