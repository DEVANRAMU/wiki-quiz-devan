import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from quiz_models import GeneratedQuizContent # Import the specific model for LLM output

# Load environment variables from the .env file
load_dotenv()
# The GOOGLE_API_KEY environment variable will be automatically read by the constructor

def generate_quiz_from_text(article_summary: str) -> GeneratedQuizContent:
    """
    Uses LangChain and the Gemini API to generate a structured quiz.
    
    Args:
        article_summary: The summary text scraped from Wikipedia.
    
    Returns:
        A Pydantic object containing the questions and related topics.
    """
    
    # 1. Initialize the LLM (LangChain automatically finds the GOOGLE_API_KEY)
    # Using gemini-2.5-flash is fast and excellent for structured output tasks.
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.5)

    # 2. Define the Prompt Template (This is critical for quality!)
    # Include instructions to meet all assignment requirements.
    system_prompt = (
        "You are an expert quiz generator. Your task is to generate a challenging "
        "and factual quiz (between 5 and 10 questions) based ONLY on the provided text. "
        "You MUST return the output as a JSON object that strictly adheres to the "
        "provided Pydantic schema for structured output. "
        "Ensure questions include a difficulty ('easy', 'medium', or 'hard'), "
        "a short explanation, and four clear options."
    )

    user_prompt = (
        "Generate the quiz and related topics based on the following article content:\n\n"
        "--- ARTICLE CONTENT ---\n"
        "{article_text}\n"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", user_prompt)
    ])

    # 3. Create the Structured Chain
    # .with_structured_output ensures the LLM output is parsed into our Pydantic model
    structured_llm = llm.with_structured_output(GeneratedQuizContent)
    chain = prompt | structured_llm

    # 4. Invoke the Chain
    result = chain.invoke({"article_text": article_summary})

    # The result is a validated Pydantic object
    return result