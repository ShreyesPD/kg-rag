"""
Non-interactive setup script to create the disease vector database
"""
import os
from kg_rag.utility import config_data

print("Starting vector database setup...")
print("")

# Check if vectorDB already exists
if os.path.exists(config_data["VECTOR_DB_PATH"]):
    print(f"VectorDB already exists at: {config_data['VECTOR_DB_PATH']}")
    print("Setup completed!")
else:
    print("Creating vectorDB...")
    try:
        from kg_rag.vectorDB.create_vectordb import create_vectordb
        create_vectordb()
        print("VectorDB created successfully!")
        print("Setup completed!")
    except Exception as e:
        print(f"Error creating vectorDB: {e}")
        print("Please check the VECTOR_DB_PATH in config.yaml")
