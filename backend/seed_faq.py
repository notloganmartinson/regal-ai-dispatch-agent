import asyncio
import os
import re
from dotenv import load_dotenv
import google.generativeai as genai
from sqlalchemy import select
from backend.database import AsyncSessionLocal, FAQKnowledgeBase

load_dotenv()

# Initialize Gemini Client
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

async def generate_embedding(text: str):
    # Using 'models/text-embedding-004' which provides high-quality 768-dim embeddings.
    # Note: If your pgvector vector field is strictly 1536, 
    # you may need to switch back or adjust the database schema.
    # For now, assuming compatibility or adjustment needed.
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=text,
        task_type="retrieval_document"
    )
    return result['embedding']

def parse_faqs(filepath: str):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Look for "### Q: ..."
    # This matches the structure: ### Q: ... \n **A:** ...
    qa_pairs = re.findall(r'###\s+Q:(.*?)\n\*\*A:\*\*(.*?)(?=\n\n###|\n\n---\n|\Z)', content, re.DOTALL)
    
    faqs = []
    for q, a in qa_pairs:
        faqs.append({
            "question": q.strip(),
            "answer": a.strip()
        })
    return faqs

async def seed_faq_data():
    faqs = parse_faqs("JBHunt_Hotline_FAQs.md")
    
    async with AsyncSessionLocal() as session:
        for faq in faqs:
            print(f"Embedding question: {faq['question']}")
            embedding = await generate_embedding(faq['question'])
            
            faq_entry = FAQKnowledgeBase(
                question=faq['question'],
                answer=faq['answer'],
                embedding=embedding
            )
            session.add(faq_entry)
        
        await session.commit()
        print(f"Successfully seeded {len(faqs)} FAQs into the knowledge base.")

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not set.")
    else:
        asyncio.run(seed_faq_data())
