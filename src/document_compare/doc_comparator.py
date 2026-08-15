# import sys 
# from dotenv import load_dotenv
# import pandas as pd
# from logger.custom_logger import CustomLogger
# from exception.custom_exception import DocumentPortalException
# from model.models import *
# from prompt.prompt_library import PROMPT_REGISTRY
# from utils.model_loader import ModelLoader
# from langchain_core.output_parsers import JsonOutputParser
# from langchain_classic.output_parsers import OutputFixingParser

# class DocumentComparatorLLM:
#     def __init__(self):
#         load_dotenv()
#         self.log=CustomLogger().get_logger(__name__)
#         self.loader=ModelLoader()
#         self.llm=self.loader.load_llm()
#         self.parser=JsonOutputParser(pydantic_object=SummaryResponse)
#         self.fixing_parser=OutputFixingParser.from_llm(parser=self.parser,llm=self.llm)
#         self.prompt=PROMPT_REGISTRY.get("document_comparator")
#         self.chain=self.prompt|self.llm|self.fixing_parser
#         self.log.info("DocumentsComparatorLLM initialized with modeland parser ")



#     def compare_documents(self, combined_docs: str)-> pd.DataFrame:
#         """Compares 2 docs and returns a structured comparison"""
#         try:
#             inputs ={ 
#                 "combined_docs": combined_docs,
#                 "format_instructions": self.parser.get_format_instructions()
            
#             }
#             self.log.info("Starting Document Comparison", inputs=inputs)
#             response= self.chain.invoke(inputs)
#             self.log.info("Document Comparison completed", response=response)
#             return self._format_response(response)

#         except Exception as e:
#             self.log.error(f"error in compare_documents:{e}")
#             raise DocumentPortalException("An error occurred while comparing documents",sys)


#     def _format_response(self, response_parsed:list[dict])->pd.DataFrame: #type:ignore
#         """formats the llm response into a structured response"""
#         try:
#             df=pd.DataFrame(response_parsed)
#             self.log.info("Resonse formatted into DataFrame", dataframe=df)
#             return df
#         except Exception as e:
#             self.log.error(f"error formating response into DataFrame",error =str(e))
#             raise DocumentPortalException("Error Formatting Response ",sys)




import sys
from dotenv import load_dotenv
import pandas as pd
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from utils.model_loader import ModelLoader
from logger import GLOBAL_LOGGER as log
from exception.custom_exception import DocumentPortalException
from prompt.prompt_library import PROMPT_REGISTRY
from model.models import SummaryResponse,PromptType

class DocumentComparatorLLM:
    def __init__(self):
        load_dotenv()
        self.loader = ModelLoader()
        self.llm = self.loader.load_llm()
        self.parser = JsonOutputParser(pydantic_object=SummaryResponse)
        self.fixing_parser = OutputFixingParser.from_llm(parser=self.parser, llm=self.llm)
        self.prompt = PROMPT_REGISTRY[PromptType.DOCUMENT_COMPARATOR.value]
        self.chain = self.prompt | self.llm | self.parser
        log.info("DocumentComparatorLLM initialized", model=self.llm)

    def compare_documents(self, combined_docs: str) -> pd.DataFrame:
        try:
            inputs = {
                "combined_docs": combined_docs,
                "format_instruction": self.parser.get_format_instructions()
            }

            log.info("Invoking document comparison LLM chain")
            response = self.chain.invoke(inputs)
            log.info("Chain invoked successfully", response_preview=str(response)[:200])
            return self._format_response(response)
        except Exception as e:
            log.error("Error in compare_documents", error=str(e))
            raise DocumentPortalException("Error comparing documents", sys)

    def _format_response(self, response_parsed: list[dict]) -> pd.DataFrame: #type: ignore
        try:
            df = pd.DataFrame(response_parsed)
            return df
        except Exception as e:
            log.error("Error formatting response into DataFrame", error=str(e))
            DocumentPortalException("Error formatting response", sys)