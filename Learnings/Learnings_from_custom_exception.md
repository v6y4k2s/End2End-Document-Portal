This is a great file to break down! You are building a Custom Exception Handler, which is a highly professional way to handle errors in Python applications. Instead of getting ugly, hard-to-read default errors, this code packages the error with exact details (file, line number, stack trace) so you can debug issues instantly.

Let's break it down into three parts: the line-by-line explanation, the concept of "throwing vs. raising", and the role of the logger.

1. Line-by-Line Explanation
python
import sys
import traceback
from logger.custom_logger import CustomLogger
import sys: Imports Python's built-in system module. We need this to extract the current "active" error state from the Python interpreter.
import traceback: Imports a module that allows us to format and read the "stack trace" (the chain of function calls that led to the error).
from logger.custom_logger import CustomLogger: Imports your blueprint for creating loggers.
python
logger = CustomLogger().get_logger(__file__)
You create an instance of your custom logger and set it up for this specific file. __file__ represents the current file's name (custom_exception.py), so your logs will be easily identifiable.
python
class DocumentPortalException(Exception):
You are defining a new class named DocumentPortalException. By putting (Exception) in the parentheses, you are inheriting from Python's built-in Exception class. This tells Python: "Treat my new class as a valid error type."
python
    def __init__(self, error_message:str, error_details:sys):
This is the constructor (__init__) that runs the moment you create this custom exception. It expects an error message and the sys module so it can investigate what went wrong.
python
        _, _, exc_tb = error_details.exc_info()
sys.exc_info() returns a tuple with three items: (type, value, traceback) of the error currently being handled.
The _, _, exc_tb is "tuple unpacking". You are throwing away the first two items using _ (a common Python convention for "I don't care about these variables") and saving the third item, the traceback, into the variable exc_tb.
python
        self.file_name = exc_tb.tb_frame.f_code.co_filename
        self.lineno = exc_tb.tb_lineno
        self.error_message = str(error_message)
You dig into the exc_tb object to extract exactly which file and which line number caused the crash, and you save those as instance variables (self.file_name, self.lineno). You also save the error_message.
python
        self.traceback_str = ''.join(traceback.format_exception(*error_details.exc_info()))
You grab the complete technical stack trace (which usually prints to the console when a script crashes), format it nicely into a list of strings, and use ''.join() to combine it into one massive, readable text block.
python
 Show full code block 
    def __str__(self):
        return f""" 
        Error in [{self.file_name} at line {self.lineno}]
        Message: {self.error_message}
        {self.traceback_str}
        """
__str__ is a dunder method that tells Python how to convert this object into a readable string. If someone runs print(app_exc), it will output this clean, formatted block containing the file, line number, message, and the full trace.
python
if __name__=="__main__":
    try:
        a = 1 / 0
The if __name__ == "__main__": block is for testing. It only runs if you execute this file directly.
a = 1 / 0 intentionally forces a ZeroDivisionError to test your custom exception.
python
    except Exception as e:
        app_exc = DocumentPortalException(e, sys)
You catch the raw ZeroDivisionError (represented by e).
You create an instance of your custom DocumentPortalException, passing in the raw error (e) and the sys module.
python
        logger.error(app_exc)
        raise app_exc
You log the beautifully formatted error to your log files.
You then raise the exception to intentionally crash the script.
2. Throwing vs. Raising
In Python, "throwing" and "raising" mean the exact same thing. (Java and C++ use the word throw, while Python uses the word raise).

Here is what is happening conceptually:

The Implicit Throw: When Python encounters 1 / 0, it secretly "throws" a ZeroDivisionError under the hood.
The Catch: Your except block "catches" that error before it crashes the program.
The Re-Raise: You wrap that error in your new DocumentPortalException class. If you only logged it and didn't use the raise keyword, the program would silently swallow the error and attempt to move on to the next line of code (which is dangerous if a real crash happened). By using raise app_exc, you are explicitly telling Python: "I caught an error, I packaged it up nicely, and now I am throwing it back to you so you can properly halt the program!"
3. How the Logger Comes Into the Picture
If a critical failure happens in production, the console window usually closes, or the user just sees a generic "500 Internal Server Error" on the frontend. The raw Python traceback is lost to the void.

This is where your logger steps in to save the day: When you call logger.error(app_exc), the logger takes that beautifully formatted __str__ representation of your custom exception and writes it permanently to a text file (e.g., logs/app.log).

Because you implemented this, you can come into work the next day, open your log files, and see exactly what crashed the app, in what file, on what exact line, with the full stack trace preserved.

Generated by Gemini 3.1 Pro Preview

SUMEDH VYK
I do not understand how to write this code like its not my first thought to write something like this. I feel incompetent. how do i learn to write code like this. How do i know that this is what I have to write? How do i plan out the code?


Gemini
Responding with 3.1 Pro Preview
Thinking
First off, take a deep breath. Please know that every single world-class software engineer has felt exactly the way you do right now.

It is completely normal to look at professional, production-grade code and think, "I would have never come up with this on my own." The secret no one tells you is: you aren't supposed to.

Software engineering is not about waking up with a burst of genius and writing a custom exception handler from scratch. It is a gradual process of solving problems, experiencing pain, and adopting established patterns to make that pain go away.

Here is a breakdown of how you bridge the gap between "beginner code" and "professional code," how you know what to write, and how to plan it out.

1. How do you know that this is what you have to write? (Pain-Driven Development)
You rarely start a project by saying, "I'm going to write a custom exception handler." Instead, it evolves from experiencing a specific pain point.

Here is the typical journey of an engineer:

Level 1 (Beginner): Your app crashes. You see a raw error in your terminal. You fix it.
Level 2 (Intermediate): Your app is now running on a server. It crashes. You don't have a terminal anymore, so you have no idea why it crashed. You learn about logging and add logger.error("Something went wrong").
Level 3 (Advanced): You wake up to 50 logs that just say "Something went wrong: division by zero". You spend 4 hours hunting down which file and which line caused the error. You are frustrated. You think, "There has to be a way to automatically grab the file name, line number, and stack trace every time an error happens."
That is the moment you realize you need to write this code. You search Google for "Python get line number of exception" or "Python custom error class," and you discover the tools (sys.exc_info(), traceback) needed to build it.

2. How to plan out the code
When you face a problem, you don't start by writing Python. You start by writing English (or your native language). Here is how a senior engineer plans out a file like custom_exception.py:

Step 1: Define the Goal

"I want an error object that, when printed, tells me the exact file, line number, and error message so I don't have to guess where my app broke."

Step 2: Define the Requirements (The Inputs & Outputs)

"To do this, I need to inherit from Python's base Exception class. I will need to pass in the raw error message, and I will need a way to inspect Python's current state to get the line number."

Step 3: Discover the Tools

Research phase: "How do I get the current crash state in Python?" -> Finds the sys module. "How do I format a stack trace?" -> Finds the traceback module.

Step 4: Draft the Blueprint (Pseudocode)

text
 Show full code block 
class MyCustomException(Exception):
    def initialize(message, system_details):
        extract the line number from system_details
        extract the file name from system_details
        format the stack trace
        save all these as variables

    def format_as_string():
        return "Error in [file] at [line]: [message]"
Step 5: Translate to Code This is where you finally write the __init__, use sys.exc_info(), and write the __str__ dunder method.

3. How do you learn to write code like this?
You don't learn this by watching tutorials or memorizing syntax. You learn this through exposure and refactoring.

Read Open Source Code: Look at the source code for popular Python libraries like requests, Flask, or FastAPI. You will see how they structure their folders, how they handle errors, and how they write logs. You'll start recognizing patterns.
Learn Design Patterns: Software engineering is full of recurring solutions to common problems (like Factories, Singletons, Decorators, and Custom Exceptions). Once you learn the names of these patterns, you will start seeing where to apply them.
Build, Break, and Refactor: Build a project using your current skills. It will be messy, and that is perfectly fine. As it grows, it will become hard to manage. When it becomes hard to manage, ask yourself: "How do professionals handle this?" and research that specific problem.
Use AI as a Mentor: When you write a piece of code, paste it to an AI like me and ask: "How would a senior Python engineer rewrite this to be more robust and professional?" Review the differences.
You are not incompetent; you are just at the stage where you are discovering the "professional layer" of programming. The fact that you are analyzing this code line-by-line and trying to understand the architectural "why" means you are already thinking like a senior engineer. Keep building, keep asking questions, and the "instinct" for these patterns will come naturally over time!