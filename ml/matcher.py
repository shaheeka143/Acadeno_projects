from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def match_jobs(resume_text, jobs, threshold=5):
    if not resume_text or not jobs:
        return []

    job_texts = [
        f"{job.title} {job.skills} {job.company} {job.location}"
        for job in jobs
    ]

    corpus = [resume_text] + job_texts

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform(corpus)

    similarities = cosine_similarity(tfidf[0:1], tfidf[1:])[0]

    results = []
    for job, score in zip(jobs, similarities):
        percent = round(score * 100, 2)
        if percent >= threshold:
            results.append({
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "score": percent,
                "apply_link": job.apply_link
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results
