import os
import asyncio
import json
from dotenv import load_dotenv
import openai
from pinecone import Pinecone

from langchain.schema import Document
from api.get_data_routes import file_content

load_dotenv()

async def embed_document():
    try:
        documents = []

        # Convert Documents to text
        for file in file_content:
            doc = Document(
                page_content=f"{file['name']}\n{file['content']}",
                metadata={"source": file['content']}
            )
            res = openai.embeddings.create(
                        input=doc.page_content,
                        model="text-embedding-3-small"
                    )
            embedding = res.data[0].embedding
            documents.append({
                "id": file['name'],
                "values": embedding,
                "metadata": doc.metadata
            })

        
       
        pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
        index = pc.Index("codebase-rag")

        # Upsert vectors into Pinecone
        if documents:
            index.upsert(vectors=documents, namespace="https://github.com/CoderAgent/SecureAgent")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(embed_document())
