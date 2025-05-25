from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
import os
from study_plan.typesx import QuestionGeneratorOutput
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators
gemini_llm  = LLM(
    model="gemini/gemini-1.5-flash",
    temperature=0.1,
    api_key="AIzaSyARLOmHXWd5x8w4JE7FLtDlLsztFT6OmrA",
    )
@CrewBase
class QuestionGenerate():
    """QuestionGenerate crew"""

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'


    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def question_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['question_generator'],
            llm=gemini_llm,
        )

    

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def generate_questions_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_questions_task'],
            output_json=QuestionGeneratorOutput, # This is the output type of the task
            output_file='output/questions.json', # This is the output file of the task
        )
    

    

    @crew
    def crew(self) -> Crew:
        """Creates the QuestionGenerate crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )