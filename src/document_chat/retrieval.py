# import sys
# import os 
# from typing import List, Optional
# from operator import itemgetter
# from pathlib import Path
# from typing import List, Optional
# from langchain_core.messages import BaseMessage


# from langchain_core.chat_history import BaseChatMessageHistory
# from langchain_community.chat_message_histories import ChatMessageHistory
# from langchain_community.vectorstores import FAISS
# from langchain_core.runnables.history import RunnableWithMessageHistory
# from langchain_classic.chains.combine_documents import create_stuff_documents_chain
# from langchain_classic.chains.history_aware_retriever import create_history_aware_retriever
# from langchain_classic.chains.retrieval import create_retrieval_chain


# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.runnables import RunnablePassthrough 


# from utils.model_loader import ModelLoader
# from logger.custom_logger import CustomLogger
# from exception.custom_exception import DocumentPortalException
# from prompt.prompt_library import PROMPT_REGISTRY
# from model.models import PromptType






# class ConversationalRAG:
#     def __init__(self, session_id:str, retriever=None):
#         try:
            
#             self.log= CustomLogger().get_logger(__name__)
#             self.session_id=session_id
#             self.retriever=retriever
#             self.llm=self._load_llm()
#             self.contextualize_prompt= PROMPT_REGISTRY[PromptType.CONTEXTUALIZE_QUESTION.value]
#             self.qa_prompt= PROMPT_REGISTRY[PromptType.CONTEXT_QA.value]

#             if retriever is None:
#                 raise ValueError("Retriever cannot be None")

#             self._build_lcel_chain()
#             self.log.info("Conversational RAG initialized", session_id=session_id)



#         except Exception as e:
#             self.log.error("failed to intialize ConversationalRAG", error=str(e), session_id=session_id)
#             raise DocumentPortalException("failed to intialize ConversationalRAG",sys)
        

#     def load_retriever_from_faiss(self, index_path:str):
#         """Load a FAISS vectorstore from disk and convert to retriever """
#         try:
#             embeddings=ModelLoader().load_embeddings()
#             if not os.path.isdir(index_path):
#                 raise FileNotFoundError(f"Faiss index not found at {index_path}")
            
            
#             vectorstore=FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
#             self.retriever=vectorstore.as_retriever(search_type= "similarity", search_kwargs={"k":5})
#             self.log.info("Loaded retriever from faiss", index_path=index_path, session_id=self.session_id)

            
#             return self.retriever




#         except Exception as e:
#             self.log.error("failed to load retriever from faiss", error=str(e), session_id=self.session_id)
#             raise DocumentPortalException("failed to load retriever from faiss",sys)


#     def invoke (self, user_input:str,chat_history:Optional[List[BaseMessage]]=None)->str:
#         """
#         Args:
#             user_input(str): _description_
#             chat_history(Optional[List[BaseChatMessageHistory]]): _description_, defaults to None
#         Returns:
#             str: _description_
#         """
#         try:
#             chat_history = chat_history or []
#             payload={"input": user_input, "chat_history": chat_history}
#             answer=self.chain.invoke(payload)
#             if not answer:
#                 self.log.warning("Empty answer received", session_id=self.session_id)
#                 return "No answer Generated"

#             self.log.info("Chain invoked successfully", session_id=self.session_id, user_input=user_input, answer_preview=answer[:150])
#             return answer


#         except Exception as e:
#             self.log.error("failed to invoke", error=str(e), session_id=self.session_id)
#             raise DocumentPortalException("failed to invoke",sys)

#     def _load_llm(self):
#         try:
#             llm= ModelLoader().load_llm()
#             if not llm:
#                 raise ValueError("LLM could not be loaded")
#             self.log.info("Loaded LLM", session_id=self.session_id, class_name=llm.__class__.__name__)
#             return llm

#         except Exception as e:
#             self.log.error("failed to load llm", error=str(e), session_id=self.session_id)
#             raise DocumentPortalException("failed to load llm",sys)

#     @staticmethod
#     def _format_docs(docs):
        
#         return "\n\n".join(doc.page_content for doc in docs)

        
#     def _build_lcel_chain(self):
#         try:
# # rewrite question using chat history
#             question_rewriter = (
#                 {"input": itemgetter("input"), "chat_history": itemgetter("chat_history")}
#                  |self.contextualize_prompt
#                  |self.llm
#                  |StrOutputParser()
#             )
            
#             retrieve_docs = self.retriever | self._format_docs

#             self.chain = (
#                 {
#                     "context": retrieve_docs,
#                     "input": itemgetter("input"),
#                     "chat_history": itemgetter("chat_history"),
#                 }
#                 |self.qa_prompt
#                 |self.llm
#                 |StrOutputParser()
#             )

#         except Exception as e:
#             self.log.error("failed to build lcel chain", error=str(e), session_id=self.session_id)
#             raise DocumentPortalException("failed to build lcel chain",sys)



import sys
import os
from operator import itemgetter
from typing import List, Optional, Dict, Any

from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS

from utils.model_loader import ModelLoader
from exception.custom_exception import DocumentPortalException
from logger import GLOBAL_LOGGER as log
from prompt.prompt_library import PROMPT_REGISTRY
from model.models import PromptType


class ConversationalRAG:
    """
    LCEL-based Conversational RAG with lazy retriever initialization.

    Usage:
        rag = ConversationalRAG(session_id="abc")
        rag.load_retriever_from_faiss(index_path="faiss_index/abc", k=5, index_name="index")
        answer = rag.invoke("What is ...?", chat_history=[])
    """

    def __init__(self, session_id: Optional[str], retriever=None):
        try:
            self.session_id = session_id

            # Load LLM and prompts once
            self.llm = self._load_llm()
            self.contextualize_prompt: ChatPromptTemplate = PROMPT_REGISTRY[
                PromptType.CONTEXTUALIZE_QUESTION.value
            ]
            self.qa_prompt: ChatPromptTemplate = PROMPT_REGISTRY[
                PromptType.CONTEXT_QA.value
            ]

            # Lazy pieces
            self.retriever = retriever
            self.chain = None
            if self.retriever is not None:
                self._build_lcel_chain()

            log.info("ConversationalRAG initialized", session_id=self.session_id)
        except Exception as e:
            log.error("Failed to initialize ConversationalRAG", error=str(e))
            raise DocumentPortalException("Initialization error in ConversationalRAG", sys)

    # ---------- Public API ----------

    def load_retriever_from_faiss(
        self,
        index_path: str,
        k: int = 5,
        index_name: str = "index",
        search_type: str = "similarity",
        search_kwargs: Optional[Dict[str, Any]] = None,
    ):
        """
        Load FAISS vectorstore from disk and build retriever + LCEL chain.
        """
        try:
            if not os.path.isdir(index_path):
                raise FileNotFoundError(f"FAISS index directory not found: {index_path}")

            embeddings = ModelLoader().load_embeddings()
            vectorstore = FAISS.load_local(
                index_path,
                embeddings,
                index_name=index_name,
                allow_dangerous_deserialization=True,  # ok if you trust the index
            )

            if search_kwargs is None:
                search_kwargs = {"k": k}

            self.retriever = vectorstore.as_retriever(
                search_type=search_type, search_kwargs=search_kwargs
            )
            self._build_lcel_chain()

            log.info(
                "FAISS retriever loaded successfully",
                index_path=index_path,
                index_name=index_name,
                k=k,
                session_id=self.session_id,
            )
            return self.retriever

        except Exception as e:
            log.error("Failed to load retriever from FAISS", error=str(e))
            raise DocumentPortalException("Loading error in ConversationalRAG", sys)

    def invoke(self, user_input: str, chat_history: Optional[List[BaseMessage]] = None) -> str:
        """Invoke the LCEL pipeline."""
        try:
            if self.chain is None:
                raise DocumentPortalException(
                    "RAG chain not initialized. Call load_retriever_from_faiss() before invoke().", sys
                )
            chat_history = chat_history or []
            payload = {"input": user_input, "chat_history": chat_history}
            answer = self.chain.invoke(payload)
            if not answer:
                log.warning(
                    "No answer generated", user_input=user_input, session_id=self.session_id
                )
                return "no answer generated."
            log.info(
                "Chain invoked successfully",
                session_id=self.session_id,
                user_input=user_input,
                answer_preview=str(answer)[:150],
            )
            return answer
        except Exception as e:
            log.error("Failed to invoke ConversationalRAG", error=str(e))
            raise DocumentPortalException("Invocation error in ConversationalRAG", sys)

    # ---------- Internals ----------

    def _load_llm(self):
        try:
            llm = ModelLoader().load_llm()
            if not llm:
                raise ValueError("LLM could not be loaded")
            log.info("LLM loaded successfully", session_id=self.session_id)
            return llm
        except Exception as e:
            log.error("Failed to load LLM", error=str(e))
            raise DocumentPortalException("LLM loading error in ConversationalRAG", sys)

    @staticmethod
    def _format_docs(docs) -> str:
        return "\n\n".join(getattr(d, "page_content", str(d)) for d in docs)

    def _build_lcel_chain(self):
        try:
            if self.retriever is None:
                raise DocumentPortalException("No retriever set before building chain", sys)

            # 1) Rewrite user question with chat history context
            question_rewriter = (
                {"input": itemgetter("input"), "chat_history": itemgetter("chat_history")}
                | self.contextualize_prompt
                | self.llm
                | StrOutputParser()
            )

            # 2) Retrieve docs for rewritten question
            retrieve_docs = question_rewriter | self.retriever | self._format_docs

            # 3) Answer using retrieved context + original input + chat history
            self.chain = (
                {
                    "context": retrieve_docs,
                    "input": itemgetter("input"),
                    "chat_history": itemgetter("chat_history"),
                }
                | self.qa_prompt
                | self.llm
                | StrOutputParser()
            )

            log.info("LCEL graph built successfully", session_id=self.session_id)
        except Exception as e:
            log.error("Failed to build LCEL chain", error=str(e), session_id=self.session_id)
            raise DocumentPortalException("Failed to build LCEL chain", sys)


