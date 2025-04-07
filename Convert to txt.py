import os
import fitz  # PyMuPDF

# Paths
pdf_folder = 'data/pdf_files2'
txt_folder = 'data/txt_files'

# Create output folder if it doesn't exist
if not os.path.exists(txt_folder):
    os.makedirs(txt_folder)

# Loop through all PDFs
for filename in os.listdir(pdf_folder):
    if filename.endswith('.pdf'):
        pdf_path = os.path.join(pdf_folder, filename)
        txt_filename = os.path.splitext(filename)[0] + '.txt'
        txt_path = os.path.join(txt_folder, txt_filename)
        
        try:   # Open the PDF
            doc = fitz.open(pdf_path)
        
            # Extract text
            text = ""
            for page in doc:
                text += page.get_text()
            
            # Save text to file
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            print(f"✅ Converted: {filename} ➔ {txt_filename}")

        except Exception as e:
            print(f"⚠️ Failed to process {filename}: {e}")

print("\n🎯 Finished converting all PDFs to TXT files!")