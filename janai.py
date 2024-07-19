from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

model = "gpt-4o-mini"
project = None

class JanAI:
    """
    JanAI is a class that provides an interface to various OpenAI API functionalities, including managing files,
    vector stores, and assistants. It allows for operations such as listing, creating, retrieving, and deleting
    files and vector stores, as well as managing assistants by listing, creating, updating, and deleting them.
    
    Attributes:
        model (str): The model name to be used for the assistant operations.
    """
    client = OpenAI()
    
    def __init__(self, model: str = model):
        """
        Initializes the JanAI class with a specific model.
        
        Args:
            model (str): The model name to be used for the assistant operations. Defaults to "gpt-4o".
        """
        self.model = model
        
    def set_project(self, project):
        """
        Sets the project to be used for OpenAI API operations.
        
        Args:
            project: The project ID or name to be used for the OpenAI API operations.
        """
        self.project = project
        self.client = OpenAI(project=project)
        

    def list_files(self):
        """
        Lists all files available in the OpenAI account.
        
        Returns:
            list: A list of files available in the OpenAI account.
        """
        files_response = self.client.files.list()  
        file_list = []
        for file in files_response.data:
            file_list.append(file)
        return file_list

    def create_file(self, file, purpose="assistants"):
        """
        Creates a new file in the OpenAI account.
        
        Args:
            file: The file content or a file-like object to be uploaded.
            purpose (str): The purpose of the file. Defaults to "assistants".
            
        Returns:
            The response from the file creation API call.
        """
        returnedFile = self.client.files.create(file=file, purpose=purpose)
        return returnedFile

    def retrieve_file(self, file_id):
        """
        Retrieves a specific file by its ID.
        
        Args:
            file_id: The unique identifier of the file to retrieve.
            
        Returns:
            The file object as returned by the OpenAI API.
        """
        file = self.client.files.retrieve(file_id)
        return file

    def delete_file(self, file_id):
        """
        Deletes a specific file by its ID.
        
        Args:
            file_id: The unique identifier of the file to delete.
        """
        self.client.files.delete(file_id)
        
    def list_vector_stores(self):
        """
        Lists all vector stores available in the OpenAI account.
        
        Returns:
            list: A list of vector stores available in the OpenAI account.
        """
        vector_stores = self.client.beta.vector_stores.list()
        vs_list = []
        for vector_store in vector_stores.data:
            vs_list.append(vector_store)
        return vs_list

    def create_vector_store(self, name, metadata=None):
        """
        Creates a new vector store in the OpenAI account.
        
        Args:
            name (str): The name of the vector store to create.
            metadata (dict, optional): Additional metadata for the vector store. Defaults to None.
            
        Returns:
            The response from the vector store creation API call.
        """
        vector_store = self.client.beta.vector_stores.create(name=name, metadata=metadata)
        return vector_store

    def delete_vector_store(self, vector_store_id):
        """
        Deletes a specific vector store by its ID.
        
        Args:
            vector_store_id: The unique identifier of the vector store to delete.
        """
        self.client.beta.vector_stores.delete(vector_store_id)
    
    def list_assistants(self, limit=None, order=None, after=None, before=None):
        """
        Lists all assistants available in the OpenAI account.
        
        Args:
            limit (int, optional): The maximum number of assistants to return. Defaults to None.
            order (str, optional): The order in which to return the assistants. Defaults to None.
            after (str, optional): A pagination token to retrieve the next set of assistants. Defaults to None.
            before (str, optional): A pagination token to retrieve the previous set of assistants. Defaults to None.
            
        Returns:
            list: A list of assistants available in the OpenAI account.
        """
        assistants = self.client.beta.assistants.list(limit=limit, order=order, after=after, before=before)
        assistant_list = []
        for assistant in assistants.data:
            assistant_list.append(assistant)
        return assistant_list
    
    def create_assistant(self, model, name=None, description=None, instructions=None, tools=None, tool_resources=None, temperature=1.0, top_p=1.0, metadata=None, response_format=None):
        """
        Creates a new assistant in the OpenAI account.
        
        Args:
            model (str): The model to use for the assistant.
            name (str, optional): The name of the assistant. Defaults to None.
            description (str, optional): A description of the assistant. Defaults to None.
            instructions (str, optional): Instructions for using the assistant. Defaults to None.
            tools (list, optional): A list of tools the assistant can use. Defaults to None.
            tool_resources (dict, optional): Resources available to the tools. Defaults to None.
            temperature (float, optional): The temperature to use for the assistant's responses. Defaults to 1.0.
            top_p (float, optional): The top_p to use for the assistant's responses. Defaults to 1.0.
            metadata (dict, optional): Additional metadata for the assistant. Defaults to None.
            response_format (str, optional): The format of the assistant's responses. Defaults to None.
            
        Returns:
            The response from the assistant creation API call.
        """
        assistant = self.client.beta.assistants.create(
            name=name, 
            model=model, 
            description=description, 
            instructions=instructions, 
            temperature=temperature, 
            top_p=top_p, 
        )
        return assistant
    
    def update_assistant(self, model, assistant_id, name=None, description=None, instructions=None, tools=None, tool_resources=None, temperature=None, top_p=None, metadata=None, response_format=None):
        """
        Updates an existing assistant in the OpenAI account.
        
        Args:
            model (str): The model to use for the assistant.
            assistant_id: The unique identifier of the assistant to update.
            name (str, optional): The name of the assistant. Defaults to None.
            description (str, optional): A description of the assistant. Defaults to None.
            instructions (str, optional): Instructions for using the assistant. Defaults to None.
            tools (list, optional): A list of tools the assistant can use. Defaults to None.
            tool_resources (dict, optional): Resources available to the tools. Defaults to None.
            temperature (float, optional): The temperature to use for the assistant's responses. Defaults to None.
            top_p (float, optional): The top_p to use for the assistant's responses. Defaults to None.
            metadata (dict, optional): Additional metadata for the assistant. Defaults to None.
            response_format (str, optional): The format of the assistant's responses. Defaults to None.
            
        Returns:
            The response from the assistant update API call.
        """
        assistant = self.client.beta.assistants.update(
            assistant_id, 
            name=name, 
            model=model,
            description=description, 
            instructions=instructions, 
            temperature=temperature, 
            tools=tools,
            top_p=top_p, 
        )
        return assistant
    
    def delete_assistant(self, assistant_id):
        """
        Deletes a specific assistant by its ID.
        
        Args:
            assistant_id: The unique identifier of the assistant to delete.
        """
        self.client.beta.assistants.delete(assistant_id)