import uuid
from datetime import datetime, timezone
from pathlib import Path
import sys
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from utils.model_loader import ModelLoader
from datetime import datetime, timezone


class SingleDocIngestor:
    def __init__(self, data_dir: str= "data/single_document_chat", faiss_dir:str ="faiss_index"):
        try:
            self.log=CustomLogger().get_logger(__name__)
            
             # Project root
            self.base_dir = Path(__file__).resolve().parent.parent

            # Absolute paths
            self.data_dir = self.base_dir / data_dir
            self.faiss_dir = self.base_dir / faiss_dir


            # self.data_dir=Path(data_dir)
            # self.data_dir.mkdir(parents=True, exist_ok=True)
            
            # self.faiss_dir=Path(faiss_dir)
            # self.faiss_dir.mkdir(parents=True, exist_ok=True)
            self.data_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            self.faiss_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            
            self.model_loader=ModelLoader()

            self.log.info("SingleDocIngestor initialized", temp_path=str(self.data_dir), faiss_path=str(self.faiss_dir))
            
        except Exception as e:
            self.log.error("failed to intialize SingleDocIngestor", error=str(e))
            raise DocumentPortalException("failed to intialize SingleDocIngestor",sys)
        
    
    def ingest_files(self, uploaded_files):
        try:
            
            documents=[]
            
            for uploaded_file in uploaded_files:
                unique_filename= f"session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.pdf"
                temp_path=self.data_dir / unique_filename
                
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.read())
                
                self.log.info("PDF saved for ingestion", filename= uploaded_file.name)
                loader=PyPDFLoader(str(temp_path))
                docs=loader.load()
                documents.extend(docs)
            self.log.info("PDF files loaded", count=len(documents))
            return self._create_retriever(documents)
        

        except Exception as e:
            self.log.error("failed to ingest files", error=str(e))
            raise DocumentPortalException("failed to ingest files",sys)
        
    def _create_retriever(self, documents):
        try:
            splitter=RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=300,
                length_function=len
            )
            chunks=splitter.split_documents(documents) 
            self.log.info("Documents split into chunks", count=len(chunks))

            embeddings = self.model_loader.load_embeddings()
            vectorstore = FAISS.from_documents(chunks, embeddings)
            
            vectorstore.save_local(str(self.faiss_dir))

            self.log.info("Faiss index created and saved", faiss_path=str(self.faiss_dir))
            
            retriever = vectorstore.as_retriever( search_type="similarity", search_kwargs={"k":5})
            self.log.info("Retriever created", retriever_type=str(type(retriever)))
            return retriever


        except Exception as e:
            self.log.error("failed to create retrieveer", error=str(e))
            raise DocumentPortalException("failed to create retrieveer",sys)