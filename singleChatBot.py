import os
import re
import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import tkinter as tk
from tkinter import scrolledtext, filedialog
import scipy.sparse

class PDFChatbotUI:
    def _init_(self, master):
        self.master = master
        master.title("PDF Chatbot")

        self.text_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=80, height=20)
        self.text_area.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self.label = tk.Label(master, text="User:")
        self.label.grid(row=1, column=0, padx=10, pady=10)

        self.entry = tk.Entry(master, width=40)
        self.entry.grid(row=1, column=1, padx=10, pady=10)

        self.upload_button = tk.Button(master, text="Upload PDF", command=self.upload_pdf)
        self.upload_button.grid(row=2, column=0, padx=10, pady=10)

        self.search_button = tk.Button(master, text="Search", command=self.search_terms)
        self.search_button.grid(row=2, column=1, pady=10)

        # Initialize chatbot components
        self.init_chatbot()

    def init_chatbot(self):
        # Initialize documents_data as an empty list
        self.documents_data = []
        self.document_vectors = None
        self.vectorizer = None

    def extract_text_from_pdf(self, pdf_path):
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ''
            for page_num in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page_num].extract_text()
            return text

    def vectorize_text(self, texts):
        if not self.vectorizer:
            self.vectorizer = TfidfVectorizer()
            self.document_vectors = self.vectorizer.fit_transform(texts)
        else:
            vectors = self.vectorizer.transform(texts)
            self.document_vectors = scipy.sparse.vstack([self.document_vectors, vectors])
        return self.document_vectors

    def find_most_relevant_document(self, query_vector):
        query_vector_2d = query_vector.reshape(1, -1)  # Convert query_vector to 2D
        similarities = cosine_similarity(query_vector_2d, self.document_vectors).flatten()
        most_similar_index = similarities.argmax()
        return most_similar_index, similarities[most_similar_index]

    def upload_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            text_content = self.extract_text_from_pdf(file_path)
            title = re.sub(r'\.pdf$', '', os.path.basename(file_path))  # Extract title without '.pdf'
            self.documents_data.append((len(self.documents_data) + 1, title, text_content))

            # Vectorize the uploaded document and store the vectors
            self.vectorize_text([doc[2] for doc in self.documents_data])

            # Display the vectorized data in the text area
            self.text_area.insert(tk.END, f"Vectorized Data for {title}:\n")
            for i, feature in enumerate(self.vectorizer.get_feature_names_out()):
                self.text_area.insert(tk.END, f"{feature}: {self.document_vectors[-1, i]}\n")
            self.text_area.insert(tk.END, "\n")

    def search_terms(self):
        search_query = self.entry.get()
        if not self.documents_data or not search_query:
            return

        # Vectorize the search query
        search_query_vector = self.vectorizer.transform([search_query])

        # Display search results in the text area
        self.text_area.insert(tk.END, f"Search Results for '{search_query}':\n")
        for i, document_data in enumerate(self.documents_data):
            document_title = document_data[1]
            similarity = cosine_similarity(search_query_vector, self.document_vectors[i])[0, 0]
            self.text_area.insert(tk.END, f"Document '{document_title}': Similarity = {similarity}\n")

        self.text_area.insert(tk.END, "\n")

if _name_ == "_main_":
    root = tk.Tk()
    app = PDFChatbotUI(root)
    root.mainloop()