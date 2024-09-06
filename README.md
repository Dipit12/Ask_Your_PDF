# PDF Question Answering Application

This is a Flask web application that allows users to upload a PDF file and ask questions about its content. The application extracts text from the uploaded PDF, processes it in chunks, and utilizes OpenAI's GPT-3.5 Turbo model to provide concise answers based on the extracted text.

## Features

- **PDF Upload**: Users can upload a PDF file from their local system.
- **Text Extraction**: Extracts text from the uploaded PDF using PyMuPDF (`fitz`).
- **Chunked Processing**: Breaks down the extracted text into manageable chunks for efficient processing.
- **AI-Powered Answers**: Uses OpenAI's GPT-3.5 Turbo model to answer questions based on the PDF content.
- **Error Handling**: Gracefully handles errors such as missing files, invalid uploads, and API errors.
- **Truncated Responses**: Limits the length of the response to a maximum number of words to ensure concise answers.

## Getting Started

### Prerequisites

- **Python 3.7+**: Make sure you have Python installed.
- **Flask**: A web framework for Python.
- **PyMuPDF (`fitz`)**: A library to handle PDF extraction.
- **OpenAI API Key**: Required to interact with OpenAI's GPT-3.5 Turbo model.
