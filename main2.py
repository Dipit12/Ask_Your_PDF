from flask import Flask, request, render_template, redirect, url_for, flash
import os
import fitz  # PyMuPDF
import requests

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'your_secret_key'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

openai_api_key = "YOUR_OPENAI_KEY"

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    pdf_document = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    pdf_document.close()
    return text

def get_openai_response(prompt):
    """Get a response from OpenAI's API."""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 150
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        response_data = response.json()
        return response_data
    except requests.exceptions.RequestException as e:
        print(f"Request Exception: {e}")
        return None

def chunk_text(text, max_chunk_size):
    """Chunks text into smaller pieces based on the max_chunk_size."""
    chunks = []
    while len(text) > max_chunk_size:
        chunk = text[:max_chunk_size]
        chunks.append(chunk)
        text = text[max_chunk_size:]
    if text:
        chunks.append(text)
    return chunks

def truncate_text(text, max_words):
    """Truncates text to a maximum number of words."""
    words = text.split()
    if len(words) > max_words:
        return ' '.join(words[:max_words]) + '...'
    return text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        return redirect(url_for('ask_questions', filename=file.filename))
    return redirect(request.url)

@app.route('/ask/<filename>', methods=['GET', 'POST'])
def ask_questions(filename):
    if request.method == 'POST':
        question = request.form['question']
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Extract text from the PDF
        pdf_text = extract_text_from_pdf(file_path)


        max_chunk_size = 4000  # Increased to reduce number of API calls

        # Chunk the text if necessary
        text_chunks = chunk_text(pdf_text, max_chunk_size)

        responses = []
        found_answer = False

        for chunk in text_chunks:
            # Prepare the prompt for each chunk
            prompt = f"Based on the following text from a PDF document, answer the question concisely in about 50 words. If the information is not present, respond with 'NOT_FOUND'.\n\nText: {chunk}\n\nQuestion: {question}"

            # Get the response from OpenAI
            response_data = get_openai_response(prompt)
            if response_data:
                try:
                    answer = response_data['choices'][0]['message']['content'].strip()
                    if answer != "NOT_FOUND":
                        found_answer = True
                        responses.append(answer)
                except (KeyError, IndexError) as e:
                    print(f"Parsing Error: {e}")
            else:
                print("Error occurred while generating the answer.")


            if found_answer:
                break

        # Combine answers and truncate
        if found_answer:
            combined_answer = " ".join(responses)
            final_answer = truncate_text(combined_answer, 200)  # Limit to 200 words
        else:
            final_answer = "Details for this question aren't mentioned in the PDF."

        return render_template('ask.html', filename=filename, question=question, answer=final_answer)

    return render_template('ask.html', filename=filename)

if __name__ == '__main__':
    app.run(debug=True)