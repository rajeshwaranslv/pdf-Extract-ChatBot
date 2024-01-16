import os
import re
import PyPDF2
import tkinter as tk
from tkinter import scrolledtext, filedialog

class PDFChatbotUI:
    def _init_(self, master):
        self.master = master
        master.title("PDF Chatbot")

        self.text_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=80, height=20)
        self.text_area.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self.label = tk.Label(master, text="Search Word:")
        self.label.grid(row=1, column=0, padx=10, pady=10)

        self.entry = tk.Entry(master, width=40)
        self.entry.grid(row=1, column=1, padx=10, pady=10)

        self.upload_button = tk.Button(master, text="Upload PDF", command=self.upload_pdf)
        self.upload_button.grid(row=2, column=0, padx=10, pady=10)

        self.search_button = tk.Button(master, text="Search", command=self.search_word)
        self.search_button.grid(row=2, column=1, pady=10)

        # Initialize chatbot components
        self.init_chatbot()

    def init_chatbot(self):
        # Initialize documents_data as an empty list
        self.documents_data = []

    def extract_text_from_pdf(self, pdf_path):
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ''
            for page_num in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page_num].extract_text()
            return text

    def upload_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            text_content = self.extract_text_from_pdf(file_path)
            title = re.sub(r'\.pdf$', '', os.path.basename(file_path))  # Extract title without '.pdf'
            self.documents_data.append((len(self.documents_data) + 1, title, text_content))
            self.text_area.insert(tk.END, f"PDF '{title}' uploaded.\n")

    def search_word(self):
        search_word = self.entry.get()
        if not self.documents_data or not search_word:
            return

        found_in_any_pdf = any(search_word.lower() in document_data[2].lower() for document_data in self.documents_data)

        if found_in_any_pdf:
            self.text_area.insert(tk.END, f"Success! The word '{search_word}' is present in at least one PDF.\n")
        else:
            self.text_area.insert(tk.END, f"The word '{search_word}' is not present in any uploaded PDF.\n")

if _name_ == "_main_":
    root = tk.Tk()
    app = PDFChatbotUI(root)
    root.mainloop()