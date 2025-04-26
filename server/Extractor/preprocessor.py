import re
import string
import requests
import cv2
import numpy as np
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk

class Preprocessing:
    def __init__(self, pdf_path, endpoint, api_key):
        self.pdf_path = pdf_path
        self.endpoint = endpoint
        self.api_key = api_key
        self.full_text = ""
        self.code_blocks = []
        self.essay_blocks = []

    def is_scanned_pdf(self):
        try:
            reader = PdfReader(self.pdf_path)
            text = reader.pages[0].extract_text()
            return not bool(text and text.strip())
        except Exception as e:
            print(f"Error checking PDF: {e}")
            return True

    def preprocess_image(self, image):
        image = np.array(image)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 3)
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        return thresh

    def ocr_with_microsoft(self, image_bytes):
        ocr_url = f"{self.endpoint}/vision/v3.2/ocr"
        headers = {
            'Ocp-Apim-Subscription-Key': self.api_key,
            'Content-Type': 'application/octet-stream'
        }
        response = requests.post(ocr_url, headers=headers, data=image_bytes)
        response.raise_for_status()
        analysis = response.json()

        extracted_text = ""
        for region in analysis.get("regions", []):
            for line in region.get("lines", []):
                line_text = " ".join([word['text'] for word in line['words']])
                extracted_text += line_text + "\n"
        return extracted_text

    def extract_text(self):
        if self.is_scanned_pdf():
            print("Scanned PDF detected.")
            images = convert_from_path(self.pdf_path, dpi=300)
            text = ""
            for img in images:
                processed_img = self.preprocess_image(img)
                is_blank = np.mean(processed_img) > 250
                if is_blank:
                    continue
                _, img_encoded = cv2.imencode('.png', processed_img)
                img_bytes = img_encoded.tobytes()
                text += self.ocr_with_microsoft(img_bytes) + "\n"
            self.full_text = text
        else:
            print("Digital PDF detected. Extracting directly...")
            reader = PdfReader(self.pdf_path)
            texts = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    texts.append(page_text)
            self.full_text = "\n".join(texts)

    def preprocess_text(self):
        lines = self.full_text.split('\n')
        current_block = []
        is_code = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if self.looks_like_code(line):
                if not is_code:
                    if current_block:
                        self.essay_blocks.append('\n'.join(current_block))
                        current_block = []
                    is_code = True
                current_block.append(line)
            else:
                if is_code:
                    if current_block:
                        self.code_blocks.append('\n'.join(current_block))
                        current_block = []
                    is_code = False
                current_block.append(line)

        if current_block:
            (self.code_blocks if is_code else self.essay_blocks).append('\n'.join(current_block))

        processed_essays = [self.nlp_preprocess(essay) for essay in self.essay_blocks]

        return {
            "code_blocks": self.code_blocks,
            "essay_blocks": processed_essays
        }

    @staticmethod
    def looks_like_code(line):
        code_keywords = ['def', 'class', 'if', 'for', 'while', 'return', 'printf', 'scanf', 'cin', 'cout', '#include', 'public', 'private', 'static']
        if any(kw in line for kw in code_keywords):
            return True
        if re.search(r'[{}();=<>*/+-]', line):
            return True
        if line.startswith(('    ', '\t')):
            return True
        return False

    @staticmethod
    def nlp_preprocess(text):
        lemmatizer = WordNetLemmatizer()
        stop_words = set(stopwords.words('english'))

        sentences = sent_tokenize(text)
        cleaned_sentences = []

        for sentence in sentences:
            tokens = word_tokenize(sentence.lower())
            filtered = [
                lemmatizer.lemmatize(w) for w in tokens
                if w.isalpha() and w not in stop_words
            ]
            cleaned_sentences.append(' '.join(filtered))

        return cleaned_sentences
    
    def main(self,pdf_path):
        endpoint = "https://my-vision7.cognitiveservices.azure.com/"
        api_key = "9OAx2JdVAcTrk84PIfulSii3zWzgARA33Yt4hVPDT47qMQy5jZcrJQQJ99BDACGhslBXJ3w3AAAFACOGkb1o"
        processor = Preprocessing(pdf_path,endpoint, api_key)
        processor.extract_text()
        results = processor.preprocess_text()
        return processor.code_blocks,processor.essay_blocks
    
