# Following instructions on: https://maps.app.goo.gl/QqCHmxLVGkkehUVJ6

import requests
import numpy as np
from llama_index.llms.lmstudio import LMStudio
from llama_index.core import SimpleDirectoryReader, Settings, VectorStoreIndex, PromptTemplate
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.chat_engine import SimpleChatEngine


class LocalAPIEmbedding(BaseEmbedding):
    api_url : str = None

    def __init__(self, api_url: str):
        super().__init__()
        self.api_url = api_url
    
    def embed(self, text: list):
        # Use nomic-embed-text-v1.5
        response = requests.post(self.api_url, json={
            "input": text
        })
        response_data = response.json()
        embedding = np.array(response_data["data"][0]["embedding"])
        return embedding

    def _get_query_embedding(self, text: str) -> np.ndarray:
        """Embed a single text string."""
        return self.embed(text)

    def _get_text_embedding(self, text: str) -> np.ndarray:
        """Embed a single text string."""
        return self.embed(text)

    def _aget_query_embedding(self, texts: list[str]) -> list[np.ndarray]:
        """Embed a single text strings."""
        return [self.embed(text) for text in texts]
    

class RagLLM: 
    base_url = "http://localhost:1234/v1" # Run LM Studio server on this port before running this code
    query_engine_with_rag = None
    query_engine_without_rag = None

    def __init__(self):
        # load data
        print("Initializing RagLLM...")
        loader = SimpleDirectoryReader(
                    input_dir = "./rag",
                    required_exts=[".pdf"],
                    recursive=True
                )
        docs = loader.load_data()

        # Can also try LM Studio embed API if supported by Llama-Index
        # embed_model = HuggingFaceEmbedding( model_name="BAAI/bge-large-en-v1.5", trust_remote_code=True)
        # Settings.embed_model = embed_model

        # ====== Create vector store and upload indexed data ======
        Settings.embed_model = LocalAPIEmbedding(self.base_url + "/embeddings") # we specify the embedding model to be used
        index = VectorStoreIndex.from_documents(docs)

        self.index = index

        # setting up the llm
        llm = LMStudio(
            model_name="meta-llama-3.1-8b-instruct",
            base_url=self.base_url,
            temperature=0.1,
            context_window=8192,
            request_timeout=120,
        )

        # ====== Setup a query engine on the index previously created ======
        Settings.llm = llm # specifying the llm to be used
        # self.query_engine_with_rag = index.as_chat_engine(chat_mode="condense_plus_context", streaming=False, similarity_top_k=4)
        # self.query_engine_without_rag = index.as_chat_engine(chat_mode="condense_plus_context", streaming=False, similarity_top_k=4, use_context=False)

        qa_prompt_tmpl_str_with_rag = (
                    "Context information is below.\n"
                    "---------------------\n"
                    "{context_str}\n"
                    "---------------------\n"
                    "Given the context information above I want you to answer the following question in a crisp manner. \n"
                    "{query_str}\n"
                    "Answer: "
                    )
        
        # print(qa_prompt_tmpl_str_with_rag)

        qa_prompt_tmpl = PromptTemplate(qa_prompt_tmpl_str_with_rag)
        self.qa_prompt_tmpl = qa_prompt_tmpl

        # Do not use query engine as it can't save history easily
        self.query_engine_with_rag = index.as_chat_engine(chat_mode="context", context_prompt=qa_prompt_tmpl)
        self.query_engine_without_rag = SimpleChatEngine.from_defaults()

        print("Initialized.")


    def reset_chat_engine(self):
        self.query_engine_with_rag.reset()
        self.query_engine_without_rag.reset()

    def renew_chat_engine(self):
        self.query_engine_with_rag = self.index.as_chat_engine(chat_mode='context', context_prompt=self.qa_prompt_tmpl)
        self.query_engine_without_rag = engine = self.index.as_chat_engine(chat_mode='best')

    def query(self, system_prompt, query_prompt, use_rag=True):
        if use_rag:
            engine = self.query_engine_with_rag
        else: 
            engine = self.query_engine_without_rag
        response = engine.chat(system_prompt + "\n" + query_prompt)
        return response.response