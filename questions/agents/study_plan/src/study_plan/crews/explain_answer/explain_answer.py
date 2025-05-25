from crewai import Agent, Crew, Process, Task,LLM
from crewai.project import CrewBase, agent, crew, task
from study_plan.typesx import MCQResponse
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators
gemini_llm  = LLM(
    model="gemini/gemini-1.5-flash",
    temperature=0.1,
    api_key="AIzaSyARLOmHXWd5x8w4JE7FLtDlLsztFT6OmrA",
    )
@CrewBase
class ExplainAnswer():
    """ExplainAnswer crew"""

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def mcq_assistant(self) -> Agent:
        return Agent(
            config=self.agents_config['mcq_assistant'],
            verbose=True,
            llm=gemini_llm
        )

    # @agent
    # def answer_explainer(self) -> Agent:
    #     return Agent(
    #         config=self.agents_config['answer_explainer'],
    #         verbose=True,
    #         llm=gemini_llm
    #     )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def mcq_analysis(self) -> Task:
        return Task(
            config=self.tasks_config['mcq_analysis'],
            output_json=MCQResponse,
          # This is the output type of the task
        )

    # @task
    # def answer_selection(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['answer_selection'],
    #         output_file='report.md',
    #         output_json=AnswerSelectionOutput,
    #     )

    @crew
    def crew(self) -> Crew:
        """Creates the ExplainAnswer crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )