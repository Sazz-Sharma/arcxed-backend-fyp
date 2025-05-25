from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
import os
from study_plan.typesx import AnswerEvaluationOutput, StudyPlanOutput
from crewai_tools import SerperDevTool
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators
gemini_llm  = LLM(
    model="gemini/gemini-1.5-flash",
    temperature=0.1,
    api_key="AIzaSyARLOmHXWd5x8w4JE7FLtDlLsztFT6OmrA",
    )
search_tool = SerperDevTool()
@CrewBase
class StudyPlan():
    """StudyPlan crew"""

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def answer_evaluator(self) -> Agent:
        return Agent(
            config=self.agents_config['answer_evaluator'],
            verbose=True,
            llm=gemini_llm
        )

    @agent
    def study_planner(self) -> Agent:
        return Agent(
            config=self.agents_config['study_planner'],
            verbose=True,
            llm=gemini_llm,
            tools=[search_tool], # Add the search tool to the agent
        
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def evaluate_answers_task(self) -> Task:
        return Task(
            config=self.tasks_config['evaluate_answers_task'],
            output_json=AnswerEvaluationOutput, # This is the output type of the task
            
        )

    @task
    def generate_study_plan_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_study_plan_task'],
            output_json=StudyPlanOutput, # This is the output type of the task
            context=[self.evaluate_answers_task()],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the StudyPlan crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )