import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from questions.models import *

def create_mock_data():
    # Create IOE Stream
    stream, _ = Streams.objects.get_or_create(stream_name='IOE')
    
    # Subjects and Syllabus (matches your JSON structure)
    subjects = [
        {
            "name": "English",
            "chapters": [
                {"name": "Reading Passage", "mark1": 0, "mark2": 4},
                {"name": "Grammar", "mark1": 10, "mark2": 0},
                {"name": "Vocabulary", "mark1": 2, "mark2": 0},
                {"name": "Phonemes and Stress", "mark1": 2, "mark2": 0}
            ]
        },
        {
            "name": "Maths",
            "chapters": [
                {"name": "Set and Function", "mark1": 1, "mark2": 1},
                {"name": "Algebra", "mark1": 2, "mark2": 4},
                {"name": "Trigonometry", "mark1": 1, "mark2": 2},
                {"name": "Coordinate Geometry", "mark1": 2, "mark2": 4},
                {"name": "Calculus", "mark1": 3, "mark2": 4},
                {"name": "Vectors", "mark1": 1, "mark2": 1}
            ]
        },
        {
            "name": "Physics",
            "chapters": [
                {"name": "Mechanics", "mark1": 2, "mark2": 4},
                {"name": "Heat and Thermodynamics", "mark1": 2, "mark2": 1},
                {"name": "Wave and Optics", "mark1": 2, "mark2": 3},
                {"name": "Electricity and Magnetism", "mark1": 2, "mark2": 4},
                {"name": "Modern Physics and Electronics", "mark1": 2, "mark2": 3}
            ]
        },
        {
            "name": "Chemistry",
            "chapters": [
                {"name": "Physical Chemistry", "mark1": 6, "mark2": 3},
                {"name": "Inorganic Chemistry", "mark1": 3, "mark2": 1},
                {"name": "Organic Chemistry", "mark1": 3, "mark2": 0}
            ]
        }
    ]

    for sub in subjects:
        # Create Subject
        subject, _ = Subjects.objects.get_or_create(subject_name=sub["name"])
        
        for chap in sub["chapters"]:
            # Create Chapter
            chapter, _ = Chapters.objects.get_or_create(
                sub_id=subject,
                chapter_name=chap["name"]
            )
            
            # Create Topic
            topic, _ = Topics.objects.get_or_create(
                topic_name=f"{chap['name']} Basics",
                chapter=chapter
            )
            
            # Create Questions for mark1 (1-mark questions)
            for i in range(1, chap["mark1"] + 1):
                # Create Question
                question = Questions.objects.create(
                    question=f"{sub['name']} {chap['name']} 1-mark Q{i}",
                    options=["Option A", "Option B", "Option C", "Option D"],
                    answer="Option A"
                )
                
                # Create Hero Question
                HeroQuestions.objects.create(
                    topic=topic,
                    question=question,
                    answer={"correct": "Option A"},
                    stream=stream,
                    marks=1
                )
            
            # Create Questions for mark2 (2-mark questions)
            for i in range(1, chap["mark2"] + 1):
                # Create Question
                question = Questions.objects.create(
                    question=f"{sub['name']} {chap['name']} 2-mark Q{i}",
                    options=["True/False", "Short Answer", "Explanation"],
                    answer="True/False"
                )
                
                # Create Hero Question
                HeroQuestions.objects.create(
                    topic=topic,
                    question=question,
                    answer={"correct": "True/False"},
                    stream=stream,
                    marks=2
                )

    print("Mock data created successfully!")

if __name__ == '__main__':
    create_mock_data()