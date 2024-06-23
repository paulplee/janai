from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime, timezone
from entities import File, VectorStore

client = OpenAI()
model = "gpt-4o"

class JanAI:
    def __init__(self, model: str = model):
        self.model = model
        
    def list_files(files):
        file_list = []
        for file in files.data:
            f = File(
                id=file.id,
                object_type=file.object,
                bytes=file.bytes,
                created_at=file.created_at,
                filename=file.filename,
                purpose=file.purpose
            )
            print(f"ID: {file.id}")
            print(f"Object Type: {file.object}")
            print(f"Bytes: {file.bytes}")
            print(f"Created At: {file.created_at}")
            print(f"Filename: {file.filename}")
            print(f"Purpose: {file.purpose}")
            print("----------")
            file_list.append(f)
        return file_list

    def retrieve_file(file_id):
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
    
# janai = JanAI()

# vector_stores = janai.list_vector_stores(client.beta.vector_stores.list())
# print(f"Total Vector Stores: {len(vector_stores)}")

# files = janai.list_files(client.files.list())
# print(f"Total Files: {len(files)}")

# file = janai.retrieve_file(files[0].id)
# print(file)
# timestamp = file.created_at
# human_readable_timestamp = datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

# file_content = client.files.content(file_id="file-5rLE7rImDHk9ibUT0zBYzBgJ")
# file_content.text