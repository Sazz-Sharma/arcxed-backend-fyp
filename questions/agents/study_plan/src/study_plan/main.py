# #!/usr/bin/env python
# from random import randint

# from pydantic import BaseModel

# from crewai.flow import Flow, listen, start
# import warnings
# warnings.filterwarnings("ignore", category=SyntaxWarning)
# from study_plan.crews.question_generate.question_generate import QuestionGenerate
# from study_plan.crews.study_plan.study_plan import StudyPlan
# from study_plan.crews.explain_answer.explain_answer import ExplainAnswer
# from study_plan.crews.evaluate_user.evaluate_user import EvaluateUser


# class PoemState(BaseModel):
#     sentence_count: int = 1
#     poem: str = ""

# class xyz(BaseModel):
#     x:str = ""

# class abc(BaseModel):
#     a:str = ""

# class ExplainAnswerState(BaseModel):
#     h:str = ""

# class ExplainAnswer1(Flow[ExplainAnswerState]):
#     @start()
#     def explain_answer(self):
#         question= "Which element is most abundant in the Earth's crust?"
#         options= ["Oxygen", "Silicon", "Aluminum", "Iron"]
#         correct = "Oxygen"
#         print("Explaining answer")
#         result = (
#             ExplainAnswer()
#             .crew()
#             .kickoff(inputs={"question": question,
#                              "options": options,
#                              "correct": correct})
#         )
#         print("Explanation generated", result.raw)
#         self.state.h = result.raw

# class EvaluateUserState(BaseModel):
#     score: int = 0
#     evaluation: str = ""

# class EvaluateUser1(Flow[EvaluateUserState]):
#     @start()
#     def evaluate_user(self):
#         data= [
#   {
#     "attempted": 2,
#     "correct": 2,
#     "total_marks_possible": 2,
#     "marks_obtained": 2,
#     "accuracy_percentage": 100,
#     "score_percentage": 100,
#     "topic_id": 2,
#     "topic_name": "Grammar General"
#   },
#   {
#     "attempted": 2,
#     "correct": 1,
#     "total_marks_possible": 2,
#     "marks_obtained": 1,
#     "accuracy_percentage": 50,
#     "score_percentage": 50,
#     "topic_id": 4,
#     "topic_name": "Phonemes and Stress General"
#   },
#   {
#     "attempted": 1,
#     "correct": 0,
#     "total_marks_possible": 2,
#     "marks_obtained": 0,
#     "accuracy_percentage": 0,
#     "score_percentage": 0,
#     "topic_id": 6,
#     "topic_name": "Algebra General"
#   },
#   {
#     "attempted": 1,
#     "correct": 1,
#     "total_marks_possible": 2,
#     "marks_obtained": 2,
#     "accuracy_percentage": 100,
#     "score_percentage": 100,
#     "topic_id": 8,
#     "topic_name": "Coordinate Geometry General"
#   },
#   {
#     "attempted": 1,
#     "correct": 1,
#     "total_marks_possible": 1,
#     "marks_obtained": 1,
#     "accuracy_percentage": 100,
#     "score_percentage": 100,
#     "topic_id": 12,
#     "topic_name": "Heat and Thermodynamics General"
#   }
# ] #Demo data, Should be taken from frontend POST

#         print("Evaluating user")
#         type = input("Which one are you? (overall/subject/chapter/topic): ")
#         print(f"User type selected: {type}")
#         result = (
#             EvaluateUser()
#             .crew()
#             .kickoff(inputs={"type": type,
#                              "data": data})
#         )
#         print("Evaluation completed", result.raw)
#         self.state.score = randint(0, 10)  # Simulating a random score
#         self.state.evaluation = result.raw

# current_level = [
#         {
#             "Subject": "English",
#             "Chapters": {
#             "Reading Passage": 7,
#             "Grammar": 8,
#             "Vocabulary": 5,
#             "Phonemes and Stress": 3
#             }
#         },
#         {
#             "Subject": "Maths",
#             "Chapters": {
#             "Set and Function": 6,
#             "Algebra": 8,
#             "Trigonometry": 5,
#             "Coordinate Geometry": 7,
#             "Calculus": 4,
#             "Vectors": 3
#             }
#         },
#         {
#             "Subject": "Physics",
#             "Chapters": {
#             "Mechanics": 6,
#             "Heat and Thermodynamics": 5,
#             "Wave and Optics": 7,
#             "Electricity and Magnetism": 4,
#             "Modern Physics and Electronics": 3
#             }
#         },
#         {
#             "Subject": "Chemistry",
#             "Chapters": {
#             "Physical Chemistry": 6,
#             "Inorganic Chemistry": 4,
#             "Organic Chemistry": 3
#             }
#         }
#         ] #Demo current level of the user should be taken from the frontend POST

# class PoemFlow(Flow[PoemState]):

#     @start()
#     def generate_poem(self, current_level = current_level):
#         syllabus =[
#                 {"Subject": "English",
#         "Total_marks": 22,
#         "Number_of_questions": 18,
#         "Chapters":{
#             "Reading Passage":{"mark1":0, "mark2":4},
#             "Grammar":{"mark1":10, "mark2":0},
#             "Vocabulary":{"mark1":2, "mark2":0},
#             "Phonemes and Stress":{"mark1":2, "mark2":0}
#             }
#         },
#         {
#             "Subject": "Maths",
#             "Total_marks": 50,
#             "Number_of_questions": 25, 
#             "Chapters":{
#                 "Set and Function":{"mark1":1, "mark2":1},
#                 "Algebra":{"mark1":2, "mark2":4},
#                 "Trigonometry":{"mark1":1, "mark2":2},
#                 "Coordinate Geometry":{"mark1":2, "mark2":4},
#                 "Calculus":{"mark1":3, "mark2":4},
#                 "Vectors": {"mark1":1, "mark2":1}
#             }
#         },
#         {
#             "Subject": "Physics",
#             "Total_marks": 40,
#             "Number_of_questions": 25,
#             "Chapters":{
#                 "Mechanics":{"mark1":2, "mark2":4},
#                 "Heat and Thermodynamics":{"mark1":2, "mark2":1},
#                 "Wave and Optics":{"mark1":2, "mark2":3},
#                 "Electricity and Magnetism":{"mark1":2, "mark2":4},
#                 "Modern Physics and Electronics":{"mark1":2, "mark2":3}
#             }
#         },
#         {
#             "Subject": "Chemistry",
#             "Total_marks": 20,
#             "Number_of_questions": 16,
#             "Chapters":{
#                 "Physical Chemistry":{"mark1":6, "mark2":3},
#                 "Inorganic Chemistry":{"mark1":3, "mark2":1},
#                 "Organic Chemistry":{"mark1":3, "mark2":0}
#             }
#         }]
#         questions = [
#                 {
#                     "subject": "Chemistry",
#                     "question": "What is the difference between physical and chemical adsorption? Give an example of each.",
#                     "answer": "Physical adsorption is when gas particles are absorbed on a surface due to chemical bonds. Chemical adsorption happens due to physical forces like van der Waals. An example of physical is hydrogen on platinum. I might be mixing it though."
#                 },
#                 {
#                     "subject": "Chemistry",
#                     "question": "How does the rate of a reaction vary with temperature? Explain using the Arrhenius equation.",
#                     "answer": "When temperature increases, the reaction becomes slower because molecules move more. Arrhenius equation is something like k = A + Ea/RT, but I don’t remember how it works exactly."
#                 },
#                 {
#                     "subject": "Physics",
#                     "question": "Explain how a transformer works. Why can’t it be used with direct current?",
#                     "answer": "Transformer increases or decreases voltage using copper wires. It can't work with DC because DC has low voltage. I think AC is better because it's faster or something."
#                 },
#                 {
#                     "subject": "Physics",
#                     "question": "Calculate the potential energy stored in a capacitor of 10 μF charged to 100 V.",
#                     "answer": "I used U = CV². So 10 × 100² = 100000. I think the energy is 100000 joules, not sure if I need to divide by 2."
#                 },
#                 {
#                     "subject": "Maths",
#                     "question": "If f(x) = sin(x^2), find f'(x) using the chain rule.",
#                     "answer": "f'(x) = cos(x^2) × 2. I think the derivative of x² is 2 and we multiply with cos, but not totally sure about the order."
#                 },
#                 {
#                     "subject": "Maths",
#                     "question": "Find the area under the curve y = x^2 from x = 1 to x = 3.",
#                     "answer": "I added the values: 1² + 2² + 3² = 14. So area is 14 units². That’s how area works, right?"
#                 },
#                 {
#                     "subject": "English",
#                     "question": "Identify the main clause and subordinate clause in the sentence: 'The boy, who was wearing a red cap, ran across the field.'",
#                     "answer": "Subordinate clause: 'The boy ran across the field'. Main clause: 'who was wearing a red cap'. I get confused sometimes with these."
#                 },
#                 {
#                     "subject": "English",
#                     "question": "Choose the correct stress pattern for the word 'photograph' and use it in a sentence.",
#                     "answer": "I think the stress is on 'graph' like pho-TO-GRAPH. My sentence: 'I took a photograph in the morning'. But not sure about the stress part."
#                 }
#                 ]
        
            
#         print("Generating poem")
#         result = (
#             QuestionGenerate()
#             .crew()
#             .kickoff(inputs={"current_level": current_level,
#                              "syllabus": syllabus,})
#         )
#         question_generated = result.tasks_output[0].pydantic
        
#         results2 = (
#             StudyPlan()
#             .crew()
#             .kickoff(inputs={"current_level": current_level,
#                              "questions": questions,
#                              "syllabus": syllabus})
#         )
#         print("Poem generated", result.raw)
#         self.state.poem = result.raw

    

# syllabus =[
#                 {"Subject": "English",
#         "Total_marks": 22,
#         "Number_of_questions": 18,
#         "Chapters":{
#             "Reading Passage":{"mark1":0, "mark2":4},
#             "Grammar":{"mark1":10, "mark2":0},
#             "Vocabulary":{"mark1":2, "mark2":0},
#             "Phonemes and Stress":{"mark1":2, "mark2":0}
#             }
#         },
#         {
#             "Subject": "Maths",
#             "Total_marks": 50,
#             "Number_of_questions": 25, 
#             "Chapters":{
#                 "Set and Function":{"mark1":1, "mark2":1},
#                 "Algebra":{"mark1":2, "mark2":4},
#                 "Trigonometry":{"mark1":1, "mark2":2},
#                 "Coordinate Geometry":{"mark1":2, "mark2":4},
#                 "Calculus":{"mark1":3, "mark2":4},
#                 "Vectors": {"mark1":1, "mark2":1}
#             }
#         },
#         {
#             "Subject": "Physics",
#             "Total_marks": 40,
#             "Number_of_questions": 25,
#             "Chapters":{
#                 "Mechanics":{"mark1":2, "mark2":4},
#                 "Heat and Thermodynamics":{"mark1":2, "mark2":1},
#                 "Wave and Optics":{"mark1":2, "mark2":3},
#                 "Electricity and Magnetism":{"mark1":2, "mark2":4},
#                 "Modern Physics and Electronics":{"mark1":2, "mark2":3}
#             }
#         },
#         {
#             "Subject": "Chemistry",
#             "Total_marks": 20,
#             "Number_of_questions": 16,
#             "Chapters":{
#                 "Physical Chemistry":{"mark1":6, "mark2":3},
#                 "Inorganic Chemistry":{"mark1":3, "mark2":1},
#                 "Organic Chemistry":{"mark1":3, "mark2":0}
#             }
#         }] #Hard-codded should be hard-codded whenever the syllabus changes the admin will manually chnage the code. 

# questions = [
#                 {
#                     "subject": "Chemistry",
#                     "question": "What is the difference between physical and chemical adsorption? Give an example of each.",
#                     "answer": "Physical adsorption is when gas particles are absorbed on a surface due to chemical bonds. Chemical adsorption happens due to physical forces like van der Waals. An example of physical is hydrogen on platinum. I might be mixing it though."
#                 },
#                 {
#                     "subject": "Chemistry",
#                     "question": "How does the rate of a reaction vary with temperature? Explain using the Arrhenius equation.",
#                     "answer": "When temperature increases, the reaction becomes slower because molecules move more. Arrhenius equation is something like k = A + Ea/RT, but I don’t remember how it works exactly."
#                 },
#                 {
#                     "subject": "Physics",
#                     "question": "Explain how a transformer works. Why can’t it be used with direct current?",
#                     "answer": "Transformer increases or decreases voltage using copper wires. It can't work with DC because DC has low voltage. I think AC is better because it's faster or something."
#                 },
#                 {
#                     "subject": "Physics",
#                     "question": "Calculate the potential energy stored in a capacitor of 10 μF charged to 100 V.",
#                     "answer": "I used U = CV². So 10 × 100² = 100000. I think the energy is 100000 joules, not sure if I need to divide by 2."
#                 },
#                 {
#                     "subject": "Maths",
#                     "question": "If f(x) = sin(x^2), find f'(x) using the chain rule.",
#                     "answer": "f'(x) = cos(x^2) × 2. I think the derivative of x² is 2 and we multiply with cos, but not totally sure about the order."
#                 },
#                 {
#                     "subject": "Maths",
#                     "question": "Find the area under the curve y = x^2 from x = 1 to x = 3.",
#                     "answer": "I added the values: 1² + 2² + 3² = 14. So area is 14 units². That’s how area works, right?"
#                 },
#                 {
#                     "subject": "English",
#                     "question": "Identify the main clause and subordinate clause in the sentence: 'The boy, who was wearing a red cap, ran across the field.'",
#                     "answer": "Subordinate clause: 'The boy ran across the field'. Main clause: 'who was wearing a red cap'. I get confused sometimes with these."
#                 },
#                 {
#                     "subject": "English",
#                     "question": "Choose the correct stress pattern for the word 'photograph' and use it in a sentence.",
#                     "answer": "I think the stress is on 'graph' like pho-TO-GRAPH. My sentence: 'I took a photograph in the morning'. But not sure about the stress part."
#                 }
#                 ] #Demo-data but should be POST from the frontend

# class GenerateQuestion(Flow[abc]):
#     @start
#     def generate_question(self, current_level = current_level, syllabus = syllabus):
#         result = (
#                 QuestionGenerate()
#                 .crew()
#                 .kickoff(inputs={"current_level": current_level,
#                                 "syllabus": syllabus,})
#             )
#         # print("RAW:", result.raw)
#         # print("\n\n\nRESULT:", result)
#         # return result
    
    

# class MakeStudyPlan(Flow[xyz]):
#     @start
#     def make_studyplan(self, current_level = current_level, questions = questions, syllabus = syllabus):
#         results2 = (
#                 StudyPlan()
#                 .crew()
#                 .kickoff(inputs={"current_level": current_level,
#                                 "questions": questions,
#                                 "syllabus": syllabus})
#             )
#         return results2

# def kickoff():
#     print("Choose an option:")
#     print("1. Generate Question ")
#     print("2. Make study Plan")
#     print("3. Explain Answer")
#     print("4. Evaluate User")
#     choice = input("Enter your choice (1/2/3): ")

#     if choice == "1":
#         print("Generating question...")
#         question_flow = GenerateQuestion()
#         question_flow.kickoff()
#         # print(result.raw)
#     elif choice == "2":
#         print("Making study plan...")
#         studyplan_flow = MakeStudyPlan()
#         studyplan_flow.kickoff()
#     elif choice == "3":
#         print("Explaining answer...")
#         explain_flow = ExplainAnswer1()
#         explain_flow.kickoff()
#     elif choice == "4":
#         print("Evaluating user...")
#         evaluate_flow = EvaluateUser1()
#         evaluate_flow.kickoff()
#     else:
#         print("Invalid choice.")
    


# def plot():
#     poem_flow = PoemFlow()
#     poem_flow.plot()


# if __name__ == "__main__":
#     flow = PoemFlow()
#     flow.generate_poem()













# questions/agents/study_plan/src/study_plan/main.py

from random import randint
from pydantic import BaseModel
from crewai.flow import Flow, start # removed 'listen' as it's not used for API flows directly

import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)

# Assuming these imports correctly point to your crew definitions
# If 'study_plan' is the package name inside 'src', these should work if 'src' is in PYTHONPATH
# or if invoked correctly from the Django app structure.
from study_plan.crews.question_generate.question_generate import QuestionGenerate
from study_plan.crews.study_plan.study_plan import StudyPlan
from study_plan.crews.explain_answer.explain_answer import ExplainAnswer
from study_plan.crews.evaluate_user.evaluate_user import EvaluateUser

# --- Pydantic Models for Flow States ---
class BaseState(BaseModel): # Optional: A base state if common fields arise
    pass

class ExplainAnswerState(BaseState):
    explanation: str = ""

class EvaluateUserState(BaseState):
    evaluation: str = "" # score was random, evaluation is the main output

class GenerateQuestionState(BaseState):
    generated_questions: list = []

class MakeStudyPlanState(BaseState):
    study_plan_output: str = ""

# --- Hardcoded Syllabus Data (as per your requirement) ---
# This can be loaded from a JSON file or other config if it grows large
SYLLABUS = [
    {"Subject": "English",
     "Total_marks": 22,
     "Number_of_questions": 18,
     "Chapters": {
         "Reading Passage": {"mark1": 0, "mark2": 4},
         "Grammar": {"mark1": 10, "mark2": 0},
         "Vocabulary": {"mark1": 2, "mark2": 0},
         "Phonemes and Stress": {"mark1": 2, "mark2": 0}
     }
     },
    {
        "Subject": "Maths",
        "Total_marks": 50,
        "Number_of_questions": 25,
        "Chapters": {
            "Set and Function": {"mark1": 1, "mark2": 1},
            "Algebra": {"mark1": 2, "mark2": 4},
            "Trigonometry": {"mark1": 1, "mark2": 2},
            "Coordinate Geometry": {"mark1": 2, "mark2": 4},
            "Calculus": {"mark1": 3, "mark2": 4},
            "Vectors": {"mark1": 1, "mark2": 1}
        }
    },
    {
        "Subject": "Physics",
        "Total_marks": 40,
        "Number_of_questions": 25,
        "Chapters": {
            "Mechanics": {"mark1": 2, "mark2": 4},
            "Heat and Thermodynamics": {"mark1": 2, "mark2": 1},
            "Wave and Optics": {"mark1": 2, "mark2": 3},
            "Electricity and Magnetism": {"mark1": 2, "mark2": 4},
            "Modern Physics and Electronics": {"mark1": 2, "mark2": 3}
        }
    },
    {
        "Subject": "Chemistry",
        "Total_marks": 20,
        "Number_of_questions": 16,
        "Chapters": {
            "Physical Chemistry": {"mark1": 6, "mark2": 3},
            "Inorganic Chemistry": {"mark1": 3, "mark2": 1},
            "Organic Chemistry": {"mark1": 3, "mark2": 0}
        }
    }]

# --- Flow Definitions ---

class ExplainAnswerFlow(Flow[ExplainAnswerState]):
    @start()
    def explain_answer_task(self, question: str, options: list, correct_answer: str):
        print("Flow: Explaining answer")
        result = (
            ExplainAnswer()
            .crew()
            .kickoff(inputs={"question": question,
                             "options": options,
                             "correct": correct_answer})
        )
        print("Flow: Explanation generated", result.raw)
        self.state.explanation = result.raw
        return self.state # Return the state for the view to use

class EvaluateUserFlow(Flow[EvaluateUserState]):
    @start()
    def evaluate_user_task(self, evaluation_type: str, performance_data: list):
        print(f"Flow: Evaluating user for type: {evaluation_type}")
        result = (
            EvaluateUser()
            .crew()
            .kickoff(inputs={"type": evaluation_type,
                             "data": performance_data})
        )
        print("Flow: Evaluation completed", result.raw)
        self.state.evaluation = result.raw
        return self.state
import os
import json

class GenerateQuestionFlow(Flow[GenerateQuestionState]):
    @start()
    def generate_question_task(self, current_level: list, syllabus: list = None):
        if syllabus is None:
            syllabus = SYLLABUS

        print("Flow: Generating questions")
        
        crew_result = (
            QuestionGenerate()
            .crew()
            .kickoff(inputs={"current_level": current_level,
                             "syllabus": syllabus})
        )

        # --- Debugging crew_result ---
        print(f"DEBUG: Crew Kickoff Result Type: {type(crew_result)}")
        raw_output_data = None
        if hasattr(crew_result, 'raw') and crew_result.raw:
            print(f"DEBUG: Crew Result Raw is available. Length: {len(crew_result.raw)}")
            # crew_result.raw is usually a string representation of JSON
            try:
                raw_output_data = json.loads(crew_result.raw)
                print(f"DEBUG: Successfully parsed crew_result.raw into JSON.")
            except json.JSONDecodeError as e:
                print(f"ERROR: Failed to parse crew_result.raw as JSON. Error: {e}")
                print(f"DEBUG: Content of crew_result.raw that failed parsing: {crew_result.raw[:1000]}") # Print a sample
        else:
            print("WARNING: crew_result.raw is empty or not available.")
        
        # --- Check Pydantic output as a fallback if direct parsing of raw fails or is not preferred ---
        # This part is kept for completeness but parsing .raw is more direct if the structure is known.
        if not raw_output_data and hasattr(crew_result, 'pydantic_output') and crew_result.pydantic_output:
            print(f"DEBUG: Using crew_result.pydantic_output. Type: {type(crew_result.pydantic_output)}")
            raw_output_data = crew_result.pydantic_output # This should already be a Pydantic model or dict/list
            # If it's a Pydantic model, you might need .dict() or to access its attributes
            if hasattr(raw_output_data, 'dict'): # Common for Pydantic models
                 raw_output_data = raw_output_data.dict()


        extracted_questions_flat_list = []

        if raw_output_data and isinstance(raw_output_data, dict) and "diagnostic_questions" in raw_output_data:
            diagnostic_data = raw_output_data.get("diagnostic_questions", [])
            if isinstance(diagnostic_data, list):
                print(f"DEBUG: Found 'diagnostic_questions' list with {len(diagnostic_data)} subjects.")
                for subject_data in diagnostic_data:
                    subject_name = subject_data.get("subject")
                    chapter_questions_list = subject_data.get("chapter_questions", [])
                    if isinstance(chapter_questions_list, list):
                        for chapter_data in chapter_questions_list:
                            chapter_name = chapter_data.get("chapter")
                            questions_text_list = chapter_data.get("questions", [])
                            if isinstance(questions_text_list, list):
                                for q_text in questions_text_list:
                                    # Create a dictionary for each question that matches GeneratedQuestionDetailSerializer
                                    question_detail = {
                                        "subject": subject_name,
                                        "chapter": chapter_name,
                                        "question_text": q_text,
                                        # --- Populate other fields for GeneratedQuestionDetailSerializer if available ---
                                        # "question_type": "Descriptive", # Example, adjust as needed
                                        # "difficulty": "Medium",      # Example
                                        # "options": [],               # Example, if not MCQ
                                        # "correct_answer": ""         # Example
                                    }
                                    extracted_questions_flat_list.append(question_detail)
                            else:
                                print(f"WARNING: 'questions' in chapter '{chapter_name}' is not a list. Skipping.")
                    else:
                        print(f"WARNING: 'chapter_questions' in subject '{subject_name}' is not a list. Skipping.")
            else:
                 print(f"WARNING: 'diagnostic_questions' key exists but its value is not a list. Data: {diagnostic_data}")

        else:
            print("WARNING: Could not find 'diagnostic_questions' in the parsed output or parsed output is not a dict.")
            # You could add a fallback here to check crew_result.tasks_output[0].raw_output if needed
            # and parse that, but crew_result.raw should be the final aggregated output.

        self.state.generated_questions = extracted_questions_flat_list
        print(f"Flow: Questions generated (final count in state: {len(self.state.generated_questions)})")
        
        if self.state.generated_questions:
             print(f"Flow: First generated question (type): {type(self.state.generated_questions[0])}")
             print(f"Flow: First generated question (content): {self.state.generated_questions[0]}")
        else:
            print("Flow: No questions were loaded into the state.")
            
        return self.state

class MakeStudyPlanFlow(Flow[MakeStudyPlanState]):
    @start()
    def make_study_plan_task(self, current_level: list, answered_questions: list, syllabus: list = None):
        if syllabus is None:
            syllabus = SYLLABUS # Use the hardcoded syllabus if not provided

        print("Flow: Making study plan")
        result = (
            StudyPlan()
            .crew()
            .kickoff(inputs={"current_level": current_level,
                             "questions": answered_questions, # This is user's answers to questions
                             "syllabus": syllabus})
        )
        print("Flow: Study plan created", result.raw)
        self.state.study_plan_output = result.raw
        return self.state

# The old PoemFlow, xyz, abc, PoemState can be removed if GenerateQuestionFlow and MakeStudyPlanFlow cover their functionalities.
# The CLI kickoff() and plot() functions are also removed.