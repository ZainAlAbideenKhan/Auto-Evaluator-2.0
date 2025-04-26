
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def preprocess_text(text):
    return text.lower().strip()

def vectorize_texts(text_list):
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(text_list)
    return vectors

def calculate_similarity(vectors):
    similarity_matrix = cosine_similarity(vectors)
    return similarity_matrix

def detect_plagiarism(student_texts, target_student, threshold=0.9):
    all_students = list(student_texts.keys())
    
    if target_student not in all_students:
        return {}
    
    target_text = preprocess_text(student_texts[target_student])

    corpus = []
    other_students = []
    
    for student, text in student_texts.items():
        if student != target_student:
            corpus.append(preprocess_text(text))
            other_students.append(student)

    tfidf = vectorize_texts(corpus + [target_text])

    target_vector = tfidf[-1]
    others_vector = tfidf[:-1]

    similarities = cosine_similarity(target_vector, others_vector)[0]

    plagiarism_cases = []
    for idx, score in enumerate(similarities):
        if score > threshold:
            plagiarism_cases.append((other_students[idx], score))

    return {target_student: plagiarism_cases} if plagiarism_cases else {}

def detect_all_plagiarism(student_texts, threshold=0.9):
    all_cases = {}
    
    for student in student_texts.keys():
        cases = detect_plagiarism(student_texts, student, threshold)
        if cases:
            all_cases.update(cases)
    
    return all_cases
