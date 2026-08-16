import sys

from utils.model_loader import ModelLoader
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from model.models import *
from prompt.prompt_library import PROMPT_REGISTRY



class DocumentAnalyzer:
    """
    Analyzes documents using a pre-trained model.
    Automatically logs all actions and supports session-based organization.
    """

    def __init__(self):
        self.log = CustomLogger().get_logger(__name__)

        try:
            self.loader = ModelLoader()
            self.llm = self.loader.load_llm()

            # Use structured output (LangChain 1.x)
            self.structured_llm = self.llm.with_structured_output(Metadata)

            self.prompt = PROMPT_REGISTRY["document_analysis"]


            self.log.info("DocumentAnalyzer initialized successfully")

        except Exception as e:
            self.log.exception("Error initializing DocumentAnalyzer")
            raise DocumentPortalException(
                "Error initializing DocumentAnalyzer", sys
            ) from e

    def analyze_document(self, document_text: str) -> Metadata:
        """
        Analyze document text and extract structured metadata.
        """

        try:
            chain = self.prompt | self.structured_llm

            self.log.info("Metadata analysis chain initialized")

            response = chain.invoke(
                {
                    "document_text": document_text
                }
            )

            self.log.info("Metadata extraction successful")

            return response

        except Exception as e:
            self.log.exception("Metadata extraction failed")
            raise DocumentPortalException(
                "Metadata extraction failed", sys
            ) from e