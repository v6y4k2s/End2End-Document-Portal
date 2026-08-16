import sys
import os 
import streamlit as st
from dotenv import load_dotenv
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.vectorstores import FAISS
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains.history_aware_retriever import create_history_aware_retriever
from langchain_classic.chains.retrieval import create_retrieval_chain
from utils.model_loader import ModelLoader
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from prompt.prompt_library import PROMPT_REGISTRY
from model.models import PromptType



class ConversationalRAG:
    def __init__(self, session_id:str, retriever):
        try:
            
            self.log=CustomLogger().get_logger(__name__)
            self.session_id=session_id
            self.retriever=retriever
            self.llm=self._load_llm()
            self.contextualize_prompt= PROMPT_REGISTRY[PromptType.CONTEXTUALIZE_QUESTION.value]
            self.qa_prompt= PROMPT_REGISTRY[PromptType.CONTEXT_QA.value]
            self.history_aware_retriever= create_history_aware_retriever(
                self.llm, self.retriever, self.contextualize_prompt
            )
            self.log.info("Created history-aware retriever", session_id=session_id)
            self.qa_chain= create_stuff_documents_chain(self.llm, prompt=self.qa_prompt)
            self.log.info("Created QA chain", session_id=session_id)
            self.rag_chain= create_retrieval_chain(self.history_aware_retriever, self.qa_chain)
            self.log.info("Create RAG Chain", session_id=session_id)

            self.chain = RunnableWithMessageHistory(self.rag_chain, 
                                                    self._get_session_history,
                                                    input_messages_key="input",
                                                    history_messages_key="chat_history",
                                                    output_messages_key="answer")
            self.log.info("Created RunnableWithMessageHistory", session_id=session_id)

            

        except Exception as e:
            self.log.error("failed to intialize ConversationalRAG", error=str(e), session_id=session_id)
            raise DocumentPortalException("failed to intialize ConversationalRAG",sys)
        
    def _load_llm(self):
        try:
            llm= ModelLoader().load_llm()
            self.log.info("Loaded LLM", session_id=self.session_id, class_name=llm.__class__.__name__)
            return llm
        
        except Exception as e:
            self.log.error("failed to load llm", error=str(e), session_id=self.session_id)
            raise DocumentPortalException("failed to load llm",sys)
        
    def _get_session_history(self):
        try:
            pass
        except Exception as e:
            self.log.error("failed to fetch session history", error=str(e), session_id=self.session_id)
            raise DocumentPortalException("failed to fetch session history",sys)
        
    def load_retriever_from_faiss(self, index_path:str):
        try:
            embeddings= ModelLoader().load_embeddings()
            if not os.path.isdir(index_path):
                raise FileNotFoundError(f"Faiss index not found at {index_path}")
            
            vectorstore=FAISS.load_local(index_path, embeddings)
            self.log.info("Loaded retriever from faiss", index_path=index_path, session_id=self.session_id)
            return vectorstore.as_retriever(search_type= "similarity", search_kwargs={"k":5})


        except Exception as e:
            self.log.error("failed to load retriever from faiss", error=str(e), session_id=self.session_id)
            raise DocumentPortalException("failed to load retriever from faiss",sys)
        
    def invoke(self, user_input:str)->str:
        try:
            response=self.chain.invoke(
                {"input": user_input},
                config = {"configurable": {"session_id": self.session_id}}
            )
            answer = response.get("answer", "No answer.")
            if not answer:
                self.log.warning("Empty answer received", session_id=self.session_id)

            self.log.info("Chain invoked successfully", session_id=self.session_id, user_input=user_input, answer_preview=answer[:150])
        except Exception as e:
            self.log.error("failed to invoke", error=str(e), session_id=self.session_id)
            raise DocumentPortalException("failed to invoke",sys)
        
    