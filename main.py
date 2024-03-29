from db.vector_db import VectorDB
from hf_models.models import embed_text, Models
import tkinter as tk
from visual_interface.visual_interface import ChatBotGUI

if __name__ == "__main__":

    chat_code_model = "chat_llama_code"
    chat_code_model_lite = "chat_llama_code_lite"
    code_model = "llama_code"
    code_model_lite = "llama_code_lite"
    chat_llm_model = "chat_llama_ru"
    chat_llm_model_lite = "chat_llama_ru_lite"
    llm_model = "llama_ru"
    llm_model_lite = "llama_ru_lite"

    chat_memory = []
    BUFFER_MEMORY_COUNTER = 5

    def message_processing_pipeline(user_message: str, execution_mode: str, memory_mode: str) -> str:
        """Use pipeline of processing a user input through classification and generational LLMs  with an option of
        adding window buffer memory"""
        # Vectorising and searching the db
        embeddings = embed_text([user_message])
        db_documents = db.query_current_collection(query_embeddings=embeddings)
        db_information = str(db_documents["documents"][0])
        print(f"\nInformation from DB: {db_information}")

        # Checking the state of the app
        print(f"Memory mode from visual interface: {memory_mode}")
        memory_string = "\n".join(chat_memory) + f"\n'Human': {user_message}\n'AI': "
        if memory_mode == "memory_chat":
            question = memory_string
        else:
            question = user_message

        # Sending the question to LLM classifier to choose the best LLM
        classification_prompt = models.prompt_template(question=question,
                                                       template_key="classification")
        class_model_answer, model_speed = models.generate_response(model="llama_class",
                                                                   prompt=classification_prompt)
        print(f"Classification model speed: {model_speed} tokens per second")

        # Choosing the best model
        if class_model_answer.lower() == "code":
            if execution_mode == "better":
                if memory_mode == "memory_chat":
                    model = chat_code_model
                else:
                    model = code_model
            else:
                if memory_mode == "memory_chat":
                    model = chat_code_model_lite
                else:
                    model = code_model_lite
        else:
            if execution_mode == "better":
                if memory_mode == "memory_chat":
                    model = chat_llm_model
                else:
                    model = llm_model
            else:
                if memory_mode == "memory_chat":
                    model = chat_llm_model_lite
                else:
                    model = llm_model_lite

        print(f"Chosen model: {model}")

        # Creating or clearing the memory depending on the app state
        if memory_mode == "memory_chat":
            template_key = "memory_chat"
            if len(chat_memory) == BUFFER_MEMORY_COUNTER:
                del chat_memory[0]
            ll_prompt = models.prompt_template(db_information=db_information,
                                               chat_memory=memory_string,
                                               template_key=template_key)
        else:
            template_key = "chat"
            ll_prompt = models.prompt_template(question=user_message,
                                               db_information=db_information,
                                               template_key=template_key)
            chat_memory.clear()

        chat_model_answer, model_speed = models.generate_response(model=model, prompt=ll_prompt)

        print(f"{model} model speed: {model_speed} tokens per second")

        if memory_mode == "memory_chat":
            message_pair = f"\n'Human': {user_message}\n'AI': {chat_model_answer}\n"
            chat_memory.append(message_pair)

        return chat_model_answer


    db = VectorDB()
    if db.check_connection() is not None:
        db.get_collection(collection_name="habr")

    models = Models()

    root = tk.Tk()
    root.configure(bg="white")
    my_gui = ChatBotGUI(root, process_function=message_processing_pipeline)
    root.mainloop()
