from langchain.chat_models import ChatOpenAI

class ArrangeAgent:
    """
    ArrangeAgent combines and organizes multiple text inputs into
    a cohesive and well-structured final response.
    """

    def __init__(self, model_name="gpt-4o-mini", temperature=0):
        """
        Initialize the ArrangeAgent.

        Args:
            model_name (str): OpenAI model to use (default: "gpt-4o-mini").
            temperature (float): Controls creativity of responses.
        """
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)

    def arrange(self, texts):
        """
        Arrange and combine multiple text parts into a coherent output.

        Args:
            texts (list of str): List of text pieces from different agents.

        Returns:
            str: Combined, polished response.
        """
        prompt = (
            "You are a friendly chatbot assistant helping company employees. "
            "Combine and summarize the following information into a conversational and clear response. "
            "Avoid formal tone or email format. Speak casually and directly, like you're chatting with a colleague.\n\n"
        )
        for i, text in enumerate(texts, 1):
            prompt += f"Part {i}:\n{text}\n\n"
        response = self.llm.invoke(prompt)
        return response.content