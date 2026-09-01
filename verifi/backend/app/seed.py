import asyncio
from app.repositories.seed import seed_database_and_documents

if __name__ == "__main__":
    asyncio.run(seed_database_and_documents())
    print("VERIFI Seed Data and Synthetic Documents initialized successfully.")
