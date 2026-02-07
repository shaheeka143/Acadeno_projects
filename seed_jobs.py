from app import app, db, Job

jobs_data = [
    ("AI Research Intern", "python, deep learning, research", "OpenAI Labs", "Bangalore",
     "https://openai.com/careers"),

    ("Computer Vision Intern", "opencv, deep learning", "VisionTech", "Hyderabad",
     "https://www.visiontech.com/careers"),

    ("Data Analyst Intern", "sql, excel, powerbi", "Accenture", "Bangalore",
     "https://www.accenture.com/in-en/careers"),

    ("AI Intern", "python, ai", "Microsoft", "Hyderabad",
     "https://careers.microsoft.com"),
]

with app.app_context():
    db.session.query(Job).delete()
    for j in jobs_data:
        db.session.add(Job(
            title=j[0],
            skills=j[1],
            company=j[2],
            location=j[3],
            apply_link=j[4]
        ))
    db.session.commit()

print("Jobs inserted.")
