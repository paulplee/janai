from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime, timezone
from entities import File, VectorStore

client = OpenAI()
model = "gpt-4o"

class JanAI:
    def __init__(self, model: str = model):
        self.model = model
        
class JanAI:
    def __init__(self, model: str = model):
        self.model = model

    def list_files(self):
        files_response = client.files.list()  # Assuming this is how you fetch files
        file_list = []
        for file in files_response.data:
            f = File(
                id=file.id,
                object_type=file.object,
                bytes=file.bytes,
                created_at=file.created_at,
                filename=file.filename,
                purpose=file.purpose
            )
            # print(f"ID: {file.id}")
            # print(f"Object Type: {file.object}")
            # print(f"Bytes: {file.bytes}")
            # print(f"Created At: {file.created_at}")
            # print(f"Filename: {file.filename}")
            # print(f"Purpose: {file.purpose}")
            # print("----------")
            file_list.append(f)
        return file_list

    def create_file(name, purpose=None):
        file = client.files.create(name=name, purpose=purpose)
        f = File(
            id=file.id,
            object_type=file.object,
            bytes=file.bytes,
            created_at=file.created_at,
            filename=file.filename,
            purpose=file.purpose
        )
        return f

    def retrieve_file(self, file_id):
        file = client.files.retrieve(file_id)
        f = File(
            id=file.id,
            object_type=file.object,
            bytes=file.bytes,
            created_at=file.created_at,
            filename=file.filename,
            purpose=file.purpose
        )
        return f

    def delete_file(self, file_id):
        client.files.delete(file_id)
        
    def list_vector_stores(self):
        vector_stores = client.beta.vector_stores.list()
        vs_list = []
        for vector_store in vector_stores.data:
            # Check if the VectorStore has a name
            if vector_store.name:
                vs = VectorStore(
                    id=vector_store.id,
                    created_at=vector_store.created_at,
                    file_counts=vector_store.file_counts,
                    last_active_at=vector_store.last_active_at,
                    metadata=vector_store.metadata,
                    name=vector_store.name,
                    status=vector_store.status,
                    usage_bytes=vector_store.usage_bytes,
                    expires_after=vector_store.expires_after,
                    expires_at=vector_store.expires_at
                )
                # print(f"ID: {vector_store.id}")
                # print(f"Created At: {vector_store.created_at}")
                # print(f"File Counts: {vector_store.file_counts}")
                # print(f"Last Active At: {vector_store.last_active_at}")
                # print(f"Name: {vector_store.name}")
                # print(f"Status: {vector_store.status}")
                # print(f"Usage Bytes: {vector_store.usage_bytes}")
                # print(f"Metadata: {vector_store.metadata}")
                # print(f"Created At: {vector_store.created_at}")
                # print(f"Expires After: {vector_store.expires_after}")
                # print(f"Expires At: {vector_store.expires_at}")
                # print("----------")
                vs_list.append(vs)
        return vs_list

    def create_vector_store(self, name, metadata=None):
        vector_store = client.beta.vector_stores.create(name=name, metadata=metadata)
        return vector_store

    def delete_vector_store(self, vector_store_id):
        client.beta.vector_stores.delete(vector_store_id)
    
    def list_assistants(self, limit=None, order=None, after=None, before=None):
        assistants = client.beta.assistants.list(limit=limit, order=order, after=after, before=before)
        assistant_list = []
        for assistant in assistants.data:
            assistant_list.append(assistant)
        return assistant_list
    
    def delete_assistant(self, assistant_id):
        client.beta.assistants.delete(assistant_id)