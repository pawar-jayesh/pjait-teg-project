from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI

class WriteAgent:
    """
    WriteAgent uses a retriever and OpenAI's chat model
    to generate detailed and comprehensive answers to queries.
    """

    def __init__(self, retriever, model_name="gpt-4o-mini", temperature=0):
        """
        Initialize the WriteAgent.

        Args:
            retriever: Retriever object for searching documents.
            model_name (str): OpenAI model name to use (default: "gpt-4o-mini").
            temperature (float): Controls response creativity (0-1).
        """
        self.retriever = retriever
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            return_source_documents=True
        )

    def answer(self, query):
        """
        Generate an answer to the query using the retriever and LLM.

        Args:
            query (str): User's question.

        Returns:
            str: Generated answer from the model.
        """
        result = self.qa_chain.invoke({"query": query}) 
        return result["result"]