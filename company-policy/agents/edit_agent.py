from langchain.chat_models import ChatOpenAI

class EditAgent:
    """
    EditAgent refines or reformats answers, such as converting
    detailed text into bullet points or summaries.
    """

    def __init__(self, model_name="gpt-4o-mini", temperature=0):
        """
        Initialize the EditAgent.

        Args:
            model_name (str): OpenAI model name to use (default: "gpt-4o-mini").
            temperature (float): Controls response creativity (0-1).
        """
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)

    def edit(self, text):
        """
        Edit the given text into a simplified or bulleted format.

        Args:
            text (str): The detailed text to be edited.

        Returns:
            str: Edited text (e.g., bullet points or summary).
        """
        prompt = (
            "Please rewrite the following text into clear, concise bullet points:\n\n"
            f"{text}"
        )
        response = self.llm.invoke(prompt)
        return response.content