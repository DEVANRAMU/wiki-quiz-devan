import os
import json
import psycopg2
from psycopg2 import sql
from typing import Dict, Any, Optional

# Load environment variables from .env (for DB credentials)
from dotenv import load_dotenv
load_dotenv()

# --- Configuration ---
# You should update your .env file with these credentials
DB_NAME = os.getenv("POSTGRES_DB", "wikiquiz_db")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

# --- Connection and Table Setup ---

def get_db_connection():
    """Establishes and returns a PostgreSQL database connection."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        # In a real app, you might raise an error here
        return None

def setup_database():
    """Creates the 'quizzes' table if it doesn't exist."""
    conn = get_db_connection()
    if not conn:
        return

    try:
        cur = conn.cursor()
        # Define the schema for the 'quizzes' table
        # We store complex JSON data (quiz, key_entities) as JSONB for flexibility
        cur.execute("""
            CREATE TABLE IF NOT EXISTS quizzes (
                id SERIAL PRIMARY KEY,
                url VARCHAR(512) UNIQUE NOT NULL,
                title VARCHAR(255) NOT NULL,
                summary TEXT NOT NULL,
                sections TEXT[], -- Array of strings for sections
                key_entities JSONB, -- JSON object for key entities
                quiz JSONB NOT NULL, -- Array of quiz questions
                related_topics TEXT[], -- Array of strings for related topics
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
    except Exception as e:
        print(f"Error setting up database table: {e}")
    finally:
        if conn:
            conn.close()

# --- Data Insertion ---

def store_quiz(data: Dict[str, Any]) -> Optional[int]:
    """
    Stores the complete quiz data object into the PostgreSQL database.
    
    Args:
        data: A dictionary containing all fields (url, title, summary, etc.) 
              which should match the structure of QuizOutput.
    
    Returns:
        The ID of the newly inserted quiz, or None on failure.
    """
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cur = conn.cursor()
        
        # Prepare data for insertion, ensuring JSON fields are strings
        url = data['url']
        title = data['title']
        summary = data['summary']
        sections = data['sections']
        key_entities_json = json.dumps(data['key_entities'])
        quiz_json = json.dumps([q.model_dump() for q in data['quiz']]) # Convert Pydantic objects to JSON string
        related_topics = data['related_topics']

        # Check if the URL already exists to prevent duplicates (Bonus requirement)
        cur.execute("SELECT id FROM quizzes WHERE url = %s", (url,))
        existing_id = cur.fetchone()
        if existing_id:
            # If exists, return the existing ID (simple caching approach)
            print(f"Quiz for URL {url} already exists (ID: {existing_id[0]}). Skipping insertion.")
            return existing_id[0]
            
        # SQL query to insert the data
        insert_query = sql.SQL("""
            INSERT INTO quizzes (url, title, summary, sections, key_entities, quiz, related_topics)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """)
        
        # Execute the query
        cur.execute(insert_query, (
            url, 
            title, 
            summary, 
            sections, 
            key_entities_json, 
            quiz_json, 
            related_topics
        ))
        
        quiz_id = cur.fetchone()[0]
        conn.commit()
        return quiz_id
        
    except Exception as e:
        print(f"Error storing quiz data: {e}")
        conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

# Ensure the database setup runs when the application starts
setup_database()