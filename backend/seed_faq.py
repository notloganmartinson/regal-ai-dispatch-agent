import asyncio
import os
import re
from dotenv import load_dotenv
from sqlalchemy import select
from backend.database import AsyncSessionLocal, FAQKnowledgeBase
from sentence_transformers import SentenceTransformer

load_dotenv()

model = SentenceTransformer('all-MiniLM-L6-v2')

async def generate_embedding(text: str):
    # runs the embedding on local RTX 2060 gaming gpu
    return model.encode(text).tolist()
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
