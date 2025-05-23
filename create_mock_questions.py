import os
import django
from django.utils import timezone
import random # For selecting questions

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from questions.models import * # Assuming your models are Streams, Subjects, Chapters, Topics, Questions, HeroQuestions

# --- REALISTIC QUESTION BANK ---
# Structure:
# {
#   "Subject Name": {
#     "Chapter Name": [
#       {
#         "q": "Question text?",
#         "o": ["Option A", "Option B", "Option C", "Option D"],
#         "a": 0, # Index of the correct option in "o"
#         "m": 1 # Marks for this question (1 or 2)
#       },
#       ... more questions for this chapter
#     ]
#   }
# }

question_bank = {
    "English": {
        "Reading Passage": [
            {
                "q": "What is the main idea of a passage that discusses the effects of deforestation?",
                "o": ["The benefits of planting new trees", "The causes of deforestation", "The negative impacts of cutting down forests", "The history of forestry"],
                "a": 2, "m": 2
            },
            {
                "q": "If a text describes an event as 'momentous', it means the event was:",
                "o": ["Insignificant", "Brief", "Of great importance", "Forgotten"],
                "a": 2, "m": 1
            },
            {
                "q": "The word 'ubiquitous' most nearly means:",
                "o": ["Rare", "Present everywhere", "Hidden", "Complex"],
                "a": 1, "m": 1
            },
            {
                "q": "What can be inferred if a character in a story is described as 'pensive'?",
                "o": ["They are angry", "They are joyful", "They are deep in thought", "They are tired"],
                "a": 2, "m": 2
            }
        ],
        "Grammar": [
            {
                "q": "Which of the following sentences is grammatically correct?",
                "o": ["They is going to the park.", "She don't like ice cream.", "He plays football very well.", "We was happy."],
                "a": 2, "m": 1
            },
            {
                "q": "Identify the adjective in the sentence: 'The quick brown fox jumps over the lazy dog.'",
                "o": ["jumps", "quick", "fox", "over"],
                "a": 1, "m": 1
            },
            {
                "q": "What is the past participle of the verb 'to eat'?",
                "o": ["Ate", "Eaten", "Eating", "Eats"],
                "a": 1, "m": 1
            },
            {
                "q": "Choose the correct pronoun: 'My brother and ___ went to the store.'",
                "o": ["me", "I", "myself", "mine"],
                "a": 1, "m": 1
            }
        ],
        "Vocabulary": [
            {
                "q": "A synonym for 'ephemeral' is:",
                "o": ["Eternal", "Temporary", "Strong", "Beautiful"],
                "a": 1, "m": 1
            },
            {
                "q": "An antonym for 'benevolent' is:",
                "o": ["Kind", "Generous", "Malevolent", "Friendly"],
                "a": 2, "m": 1
            }
        ],
        "Phonemes and Stress": [
            {
                "q": "Which word has a different vowel sound than the others: 'cat', 'hat', 'bat', 'car'?",
                "o": ["cat", "hat", "bat", "car"],
                "a": 3, "m": 1
            },
            {
                "q": "Where is the primary stress in the word 'important'?",
                "o": ["im-POR-tant", "IM-por-tant", "im-por-TANT", "None of the above"],
                "a": 0, "m": 1
            }
        ]
    },
    "Maths": {
        "Set and Function": [
            {
                "q": "If A = {1, 2, 3} and B = {3, 4, 5}, what is A ∪ B?",
                "o": ["{3}", "{1, 2, 4, 5}", "{1, 2, 3, 4, 5}", "{1, 2, 3, 3, 4, 5}"],
                "a": 2, "m": 1
            },
            {
                "q": "If f(x) = 2x + 1, what is f(3)?",
                "o": ["5", "6", "7", "8"],
                "a": 2, "m": 1
            },
            {
                "q": "If A = {a, b, c} and B = {c, d, e}, what is A ∩ B?",
                "o": ["{a, b, d, e}", "{c}", "{a, b, c, d, e}", "{}"],
                "a": 1, "m": 2
            }
        ],
        "Algebra": [
            {
                "q": "Solve for x: 3x - 7 = 14",
                "o": ["x = 3", "x = 7", "x = 21/3", "x = 5"],
                "a": 1, "m": 1 # x = 7
            },
            {
                "q": "What are the roots of the quadratic equation x² - 5x + 6 = 0?",
                "o": ["(2, 3)", "(-2, -3)", "(1, 6)", "(-1, -6)"],
                "a": 0, "m": 2
            },
            {
                "q": "Simplify: (x^2 * y^3) / (x * y)",
                "o": ["x * y^2", "x^3 * y^4", "x / y^2", "y^2 / x"],
                "a": 0, "m": 2
            },
            {
                "q": "If a + b = 10 and a - b = 4, what is the value of 'a'?",
                "o": ["3", "6", "7", "14"],
                "a": 2, "m": 1 # 2a = 14 => a=7
            }
        ],
        "Trigonometry": [
            {
                "q": "What is the value of sin(30°)?",
                "o": ["1", "0.5", "sqrt(3)/2", "0"],
                "a": 1, "m": 1
            },
            {
                "q": "If cos(θ) = 0.8 and θ is acute, what is sin(θ)? (Hint: sin²θ + cos²θ = 1)",
                "o": ["0.2", "0.6", "0.36", "0.75"],
                "a": 1, "m": 2 # sin²θ = 1 - 0.64 = 0.36 => sin(θ) = 0.6
            }
        ],
        "Coordinate Geometry": [
            {
                "q": "What is the distance between points (1, 2) and (4, 6)?",
                "o": ["3", "4", "5", "7"],
                "a": 2, "m": 2 # sqrt((4-1)² + (6-2)²) = sqrt(3² + 4²) = sqrt(9+16) = sqrt(25) = 5
            },
            {
                "q": "What is the slope of the line passing through (0,0) and (2,4)?",
                "o": ["1", "2", "0.5", "4"],
                "a": 1, "m": 1
            }
        ],
        "Calculus": [
            {
                "q": "What is the derivative of x² with respect to x?",
                "o": ["x", "2x", "x³/3", "2"],
                "a": 1, "m": 1
            },
            {
                "q": "What is the integral of 2x dx?",
                "o": ["x² + C", "2x² + C", "x + C", "2 + C"],
                "a": 0, "m": 2
            },
            {
                "q": "Find the limit of (x^2 - 1)/(x - 1) as x approaches 1.",
                "o": ["0", "1", "2", "Undefined"],
                "a": 2, "m": 2 # (x-1)(x+1)/(x-1) = x+1 -> 2
            }
        ],
        "Vectors": [
            {
                "q": "If vector A = (3, 4) and vector B = (1, 2), what is A + B?",
                "o": ["(2, 2)", "(4, 6)", "(3, 8)", "(4, 8)"],
                "a": 1, "m": 1
            },
            {
                "q": "What is the dot product of A=(2,1) and B=(3,-4)?",
                "o": ["10", "2", "-2", "6"],
                "a": 1, "m": 2 # 2*3 + 1*(-4) = 6 - 4 = 2
            }
        ]
    },
    "Physics": {
        "Mechanics": [
            {
                "q": "Which of Newton's laws is also known as the law of inertia?",
                "o": ["First Law", "Second Law", "Third Law", "Law of Gravitation"],
                "a": 0, "m": 1
            },
            {
                "q": "A force of 10 N acts on a body of mass 2 kg. What is the acceleration produced?",
                "o": ["0.2 m/s²", "2 m/s²", "5 m/s²", "20 m/s²"],
                "a": 2, "m": 2 # F=ma => a = F/m = 10/2 = 5
            },
            {
                "q": "Work done is zero if the angle between force and displacement is:",
                "o": ["0°", "45°", "90°", "180°"],
                "a": 2, "m": 1
            }
        ],
        "Heat and Thermodynamics": [
            {
                "q": "Which mode of heat transfer does not require a medium?",
                "o": ["Conduction", "Convection", "Radiation", "Evaporation"],
                "a": 2, "m": 1
            },
            {
                "q": "The first law of thermodynamics is a statement of:",
                "o": ["Conservation of energy", "Conservation of mass", "Conservation of momentum", "Entropy increase"],
                "a": 0, "m": 2
            }
        ],
        "Wave and Optics": [
            {
                "q": "The phenomenon of light bending around corners is called:",
                "o": ["Reflection", "Refraction", "Diffraction", "Interference"],
                "a": 2, "m": 1
            },
            {
                "q": "A concave lens always forms a:",
                "o": ["Real, inverted image", "Virtual, erect, diminished image", "Real, erect image", "Virtual, inverted image"],
                "a": 1, "m": 2
            }
        ],
        "Electricity and Magnetism": [
            {
                "q": "Ohm's Law is given by:",
                "o": ["V = IR", "P = VI", "V = I/R", "I = VR"],
                "a": 0, "m": 1
            },
            {
                "q": "The SI unit of magnetic flux density is:",
                "o": ["Weber", "Tesla", "Henry", "Farad"],
                "a": 1, "m": 1
            },
            {
                "q": "Three resistors of 2Ω, 3Ω, and 6Ω are connected in parallel. What is their equivalent resistance?",
                "o": ["11Ω", "1Ω", "0.91Ω", "6Ω"],
                "a": 1, "m": 2 # 1/R = 1/2 + 1/3 + 1/6 = (3+2+1)/6 = 6/6 = 1 => R = 1Ω
            }
        ],
        "Modern Physics and Electronics": [
            {
                "q": "Who is credited with the discovery of the electron?",
                "o": ["Rutherford", "Bohr", "J.J. Thomson", "Chadwick"],
                "a": 2, "m": 1
            },
            {
                "q": "A P-type semiconductor is created by doping with:",
                "o": ["Pentavalent impurities", "Trivalent impurities", "Tetravalent impurities", "Noble gases"],
                "a": 1, "m": 2
            }
        ]
    },
    "Chemistry": {
        "Physical Chemistry": [
            {
                "q": "What is the pH of a neutral solution at 25°C?",
                "o": ["0", "1", "7", "14"],
                "a": 2, "m": 1
            },
            {
                "q": "Avogadro's number is approximately:",
                "o": ["6.022 x 10^20", "6.022 x 10^23", "3.141 x 10^10", "1.602 x 10^-19"],
                "a": 1, "m": 1
            },
            {
                "q": "For an exothermic reaction, ΔH is:",
                "o": ["Positive", "Negative", "Zero", "Variable"],
                "a": 1, "m": 2
            }
        ],
        "Inorganic Chemistry": [
            {
                "q": "Which of the following is a noble gas?",
                "o": ["Oxygen", "Nitrogen", "Hydrogen", "Helium"],
                "a": 3, "m": 1
            },
            {
                "q": "The chemical formula for common salt is:",
                "o": ["KCl", "NaCl", "CaCl2", "MgO"],
                "a": 1, "m": 1
            }
        ],
        "Organic Chemistry": [
            {
                "q": "What is the general formula for alkanes?",
                "o": ["CnH2n", "CnH2n+2", "CnH2n-2", "CnHn"],
                "a": 1, "m": 1
            },
            {
                "q": "Which functional group characterizes alcohols?",
                "o": ["-COOH (Carboxyl)", "-CHO (Aldehyde)", "-OH (Hydroxyl)", "-CO- (Ketone)"],
                "a": 2, "m": 1
            }
        ]
    }
}


def create_mock_data_v2():
    # Create IOE Stream
    stream, _ = Streams.objects.get_or_create(stream_name='IOE')

    # Subjects and Syllabus (matches your JSON structure for defining chapter counts)
    subjects_structure = [
        {
            "name": "English",
            "chapters": [
                {"name": "Reading Passage", "mark1": 2, "mark2": 2}, # Request 2 1-mark, 2 2-mark
                {"name": "Grammar", "mark1": 2, "mark2": 1},
                {"name": "Vocabulary", "mark1": 2, "mark2": 0},
                {"name": "Phonemes and Stress", "mark1": 2, "mark2": 0}
            ]
        },
        {
            "name": "Maths",
            "chapters": [
                {"name": "Set and Function", "mark1": 2, "mark2": 1},
                {"name": "Algebra", "mark1": 2, "mark2": 2},
                {"name": "Trigonometry", "mark1": 1, "mark2": 1},
                {"name": "Coordinate Geometry", "mark1": 1, "mark2": 1},
                {"name": "Calculus", "mark1": 1, "mark2": 2},
                {"name": "Vectors", "mark1": 1, "mark2": 1}
            ]
        },
        {
            "name": "Physics",
            "chapters": [
                {"name": "Mechanics", "mark1": 2, "mark2": 1},
                {"name": "Heat and Thermodynamics", "mark1": 1, "mark2": 1},
                {"name": "Wave and Optics", "mark1": 1, "mark2": 1},
                {"name": "Electricity and Magnetism", "mark1": 2, "mark2": 1},
                {"name": "Modern Physics and Electronics", "mark1": 1, "mark2": 1}
            ]
        },
        {
            "name": "Chemistry",
            "chapters": [
                {"name": "Physical Chemistry", "mark1": 2, "mark2": 1},
                {"name": "Inorganic Chemistry", "mark1": 2, "mark2": 0}, # Updated for available questions
                {"name": "Organic Chemistry", "mark1": 2, "mark2": 0}  # Updated for available questions
            ]
        }
    ]

    question_counter = 0

    for sub_data in subjects_structure:
        subject_name = sub_data["name"]
        subject, _ = Subjects.objects.get_or_create(subject_name=subject_name)
        print(f"\nProcessing Subject: {subject_name}")

        subject_chapters_in_bank = question_bank.get(subject_name, {})

        for chap_data in sub_data["chapters"]:
            chapter_name = chap_data["name"]
            chapter, _ = Chapters.objects.get_or_create(
                sub_id=subject,
                chapter_name=chapter_name
            )
            print(f"  Processing Chapter: {chapter_name}")

            # Create a generic Topic for this chapter if it doesn't exist
            topic, _ = Topics.objects.get_or_create(
                topic_name=f"{chapter_name} General", # Or make topics more specific
                chapter=chapter
            )

            # Get questions for this specific chapter from the bank
            chapter_questions_from_bank = subject_chapters_in_bank.get(chapter_name, [])
            
            # Filter questions by marks and shuffle for randomness
            questions_mark1_available = [q for q in chapter_questions_from_bank if q["m"] == 1]
            random.shuffle(questions_mark1_available)
            
            questions_mark2_available = [q for q in chapter_questions_from_bank if q["m"] == 2]
            random.shuffle(questions_mark2_available)

            # --- Create Questions for mark1 ---
            num_mark1_to_create = chap_data["mark1"]
            
            # Take at most the number of available questions or the number requested
            actual_mark1_to_create = min(num_mark1_to_create, len(questions_mark1_available))
            
            for i in range(actual_mark1_to_create):
                q_data = questions_mark1_available[i]
                
                # Check if this exact question text already exists to prevent duplicates
                # (Optional, but good for avoiding identical questions if script is run multiple times with same bank)
                existing_question = Questions.objects.filter(question=q_data["q"]).first()
                if existing_question:
                    question = existing_question
                else:
                    question = Questions.objects.create(
                        topic = topic,
                        question=q_data["q"],
                        options=q_data["o"],
                        answer={"correct": q_data["o"][q_data["a"]]} # Store the text of the correct option
                    )
                
                HeroQuestions.objects.get_or_create(
                    topic=topic,
                    question=question,
                    stream=stream,
                    marks=1,
                    defaults={'created_at': timezone.now(), 'updated_at': timezone.now()} # Add if your model has these
                )
                question_counter += 1
            if actual_mark1_to_create < num_mark1_to_create:
                 print(f"    Warning: Requested {num_mark1_to_create} 1-mark questions for {chapter_name}, but only {actual_mark1_to_create} were available in bank.")


            # --- Create Questions for mark2 ---
            num_mark2_to_create = chap_data["mark2"]
            actual_mark2_to_create = min(num_mark2_to_create, len(questions_mark2_available))

            for i in range(actual_mark2_to_create):
                q_data = questions_mark2_available[i]
                
                existing_question = Questions.objects.filter(question=q_data["q"]).first()
                if existing_question:
                    question = existing_question
                else:
                    question = Questions.objects.create(
                        topic = topic,
                        question=q_data["q"],
                        options=q_data["o"],
                        answer={"correct": q_data["o"][q_data["a"]]}
                    )
                
                HeroQuestions.objects.get_or_create(
                    topic=topic,
                    question=question,
                    stream=stream,
                    marks=2,
                    defaults={'created_at': timezone.now(), 'updated_at': timezone.now()}
                )
                question_counter += 1
            if actual_mark2_to_create < num_mark2_to_create:
                 print(f"    Warning: Requested {num_mark2_to_create} 2-mark questions for {chapter_name}, but only {actual_mark2_to_create} were available in bank.")


    print(f"\nMock data creation process finished. Total questions processed/created: {question_counter}")

if __name__ == '__main__':
    # Optional: Clear existing data if you want a fresh start each time
    # Be CAREFUL with this in production or if you have data you want to keep
    # Streams.objects.all().delete()
    # Subjects.objects.all().delete()
    # Chapters.objects.all().delete()
    # Topics.objects.all().delete()
    # Questions.objects.all().delete() # This will cascade delete HeroQuestions if ForeignKey is set to CASCADE
    # HeroQuestions.objects.all().delete() # Or delete separately
    # print("Cleared existing data.")
    print("Script starting...") # Add this for debugging
    create_mock_data_v2()
    print("Script finished.") 