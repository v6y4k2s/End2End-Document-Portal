# #This code creates only one CustomLogger per program run. as Python silently ignores the second because of using logging.basicConfig. in Real world projects we use logging.getLogger() with explicit handlers. 
# import logging
# from datetime import datetime
# import os
# import structlog

# class CustomLogger:
#     def __init__(self, log_dir="logs"):
#         #Ensure LogDir exists
#         self.logs_dir=os.path.join(os.getcwd(), log_dir)
#         os.makedirs(self.logs_dir, exist_ok=True)

#         #create timestamped log file name
#         self.log_file=f"{datetime.now().strftime('%m_%d_%Y_%YH_%M_%S')}.log"
#         self.log_file_path= os.path.join(self.logs_dir, self.log_file)

#         #Logging config
#         #logging.basicConfig(
#          #   filename=log_file_path,
#           #  format="[ %(asctime)s ] %(levelname)s %(name)s (line:%(lineno)d) - %(message)s ",
#            # level=logging.INFO,
#         #)
#     def get_logger(self, name= __file__):
#         logger_name=os.path.basename(name)

#         #Configure logging for console + file (both in json)
#         file_handler = logging.FileHandler(self.log_file_path)
#         file_handler.setLevel(logging.INFO)
#         file_handler.setFormatter(logging.Formatter("%(message)s")) #raw JSON lines
        
#         console_handler = logging.StreamHandler()
#         console_handler.setLevel(logging.INFO)
#         console_handler.setFormatter(logging.Formatter("%(message)s")) #raw JSON lines

#         logging.basicConfig(
#             format="%(message)s", #Structlog will handle json rendering
#             level=logging.INFO,
#             handlers=[console_handler, file_handler]
#         )

#         #Configuring Structlog for JSON structured logging
#         structlog.configure(
#             processors=[
                
#                 structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
#                 structlog.processors.add_log_level,
#                 structlog.processors.EventRenamer(to="event"),
#                 structlog.processors.JSONRenderer()
#             ],
#             logger_factory=structlog.stdlib.LoggerFactory(),
#             cache_logger_on_first_use=True,
#         )


#         return structlog.get_logger(logger_name)
        
# #example usage
    
# # if __name__== "__main__":
# #     logger=CustomLogger()
# #     logger=logger.get_logger(__file__)
# #     logger.info("Custom logger is initialized")


import os
import logging
from datetime import datetime
import structlog

class CustomLogger:
    def __init__(self, log_dir="logs"):
        # Ensure logs directory exists
        self.logs_dir = os.path.join(os.getcwd(), log_dir)
        os.makedirs(self.logs_dir, exist_ok=True)

        # Timestamped log file (for persistence)
        log_file = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
        self.log_file_path = os.path.join(self.logs_dir, log_file)

    def get_logger(self, name=__file__):
        logger_name = os.path.basename(name)

        # Configure logging for console + file (both JSON)
        file_handler = logging.FileHandler(self.log_file_path)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter("%(message)s"))  # Raw JSON lines

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter("%(message)s"))

        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",  # Structlog will handle JSON rendering
            handlers=[console_handler, file_handler]
        )

        # Configure structlog for JSON structured logging
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
                structlog.processors.add_log_level,
                structlog.processors.EventRenamer(to="event"),
                structlog.processors.JSONRenderer()
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

        return structlog.get_logger(logger_name)


# # --- Usage Example ---
# if __name__ == "__main__":
#     logger = CustomLogger().get_logger(__file__)
#     logger.info("User uploaded a file", user_id=123, filename="report.pdf")
#     logger.error("Failed to process PDF", error="File not found", user_id=123)