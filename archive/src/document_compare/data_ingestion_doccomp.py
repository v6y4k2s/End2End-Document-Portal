import sys
from pathlib import Path
import fitz
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from datetime import datetime, timezone
import uuid

class DocumentIngestion:
    """
    Handles saving, reading, and combining of PFDs for comparison with session-based versioning. 
    """
    def __init__(self,base_dir:str="data\\document_compare", session_id=None):
        self.log= CustomLogger().get_logger(__name__)
        self.base_dir= Path(base_dir)
        self.session_id = session_id or f"session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        self.session_path=self.base_dir / self.session_id
        self.session_path.mkdir(parents=True, exist_ok=True)

        self.log.info("DocumentComparator Initialized", session_path=str(self.session_path))



    # def delete_existing_files(self):
    #     """Delets existing files at the specified paths """
    #     try:
    #         if self.base_dir.exists() and self.base_dir.is_dir():
    #             for file in self.base_dir.iterdir():
    #                 if file.is_file():
    #                     file.unlink()
    #                     self.log.info("Existing file deleted successfully", path=str(file))
    #     except Exception as e:
    #         self.log.error(f"error deleting existing files: {e}")
    #         raise DocumentPortalException("Error deleting existing files",sys)

    # def save_uploaded_files(self, reference_file, actual_file):
    #    """Saves reference and actual PDF files in the session directory. """
    #    try:
    #        self.delete_existing_files()
    #        self.log.info("Existing files deleted successfully")

    #        ref_path=self.base_dir / reference_file.name
    #        act_path=self.base_dir / actual_file.name


    #        if not reference_file.name.endswith(".pdf") or not actual_file.name.endswith(".pdf"):
    #             raise ValueError("Invalid file type. Only PDF files are allowed.")
           
    #        with open(ref_path, "wb") as f:
    #             f.write(reference_file.getbuffer())
    #        with open(act_path, "wb") as f:
    #             f.write(actual_file.getbuffer())

    #        self.log.info("Uploaded files saved successfully", ref_path=ref_path, act_path=act_path)
    #        return ref_path, act_path
           
        
    #    except Exception as e:
    #        self.log.error(f"error saving uploaded files: {e}")
    #        raise DocumentPortalException("Error saving uploaded files",sys)

    def save_uploaded_files(self, reference_file, actual_file):
        try:
            ref_path = self.session_path / reference_file.name
            act_path = self.session_path / actual_file.name

            if not reference_file.name.lower().endswith(".pdf") or not actual_file.name.lower().endswith(".pdf"):
                raise ValueError("Invalid file type. Only PDF files are allowed.")

            with open(ref_path, "wb") as f:
                f.write(reference_file.getbuffer())

            with open(act_path, "wb") as f:
                f.write(actual_file.getbuffer())

            self.log.info("Uploaded files saved successfully", ref_path=str(ref_path), act_path=str(act_path))
            return str(ref_path), str(act_path)
        
        except Exception as e:
            self.log.error(f"error saving uploaded files: {e}")
            raise DocumentPortalException("Error saving uploaded files",sys)

            
                                                                                                        

    def read_pdf(self, pdf_path: Path)->str:
        """Reads PDF FILE and extracts text from each page."""
        try:
            with fitz.open(pdf_path) as doc:
                if doc.is_encrypted:
                    raise ValueError("PDF is encrypted and cannot be read.")
                all_text=[]
                for page_num in range(doc.page_count): 
                    page=doc.load_page(page_num)
                    text=page.get_text()
                    if text.strip():
                        all_text.append(f"\n --- Page {page_num + 1} --- \n{text}")
                self.log.info("PDF read successfully", file=str(pdf_path), pages=len(all_text))
                return "\n".join(all_text)


        except Exception as e:
            self.log.error(f"error reading pdf", file=str(pdf_path), error=str(e))
            raise DocumentPortalException("An error occurred while reading PDF",sys)
        
    
    def combine_documents(self, ref_path:Path, act_path:Path)->str:
        """
        Combine content of all pdf's in session folder into a single string
        """
        try:
            doc_parts=[]

            for filename in sorted(self.base_dir.iterdir()):
                if filename.is_file() and filename.suffix == ".pdf":
                    content=self.read_pdf(filename)
                    doc_parts.append(f"Document: {filename}\n{content}")

            combined_text = "\n\n".join(doc_parts)
            self.log.info("Documents combined",count = len(doc_parts), session=self.session_id)
            return combined_text


        except Exception as e:
            self.log.error(f"error combining documents", error =str(e), session = self.session_id)
            raise DocumentPortalException("An error occurred while combining documents",sys)
        

    def clean_old_sessions(self,keep_latest: int =3):
        """
        Optional method to delete older session folders, keeping only the latest N
    
        """

        try:
            session_folders = sorted(
                [f for f in self.base_dir.iterdir() if f.is_dir()],
                reverse = True
            )
            for folder in session_folders[keep_latest:]:
                for file in folder.iterdir():
                    file.unlink()
                folder.rmdir()
                self.log.info("Old session folder deleted", path=str(folder))
        except Exception as e:
            self.log.error(f"error cleaning old sessions", error=str(e))
            raise DocumentPortalException("An error occurred while cleaning old sessions",sys)  

