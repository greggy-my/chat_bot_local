from db.vector_db import VectorDB
from models import embed_text, Models
import tkinter as tk
from visual_interface.visual_interface import ChatBotGUI

if __name__ == "__main__":

    memory = []
    buffer_memory_counter = 5

    def message_processing_pipeline(user_message: str, execution_mode: str) -> str:
        embeddings = embed_text([user_message])
        db_documents = db.query_current_collection(query_embeddings=embeddings)
        db_information = str(db_documents["documents"][0])
        print(f"Информация из Хабра: {db_information}")
        class_model_answer, model_speed = models.generate_response(model="llama_class",
                                                                   prompt=models.prompt_template(
                                                                       db_information=db_information,
                                                                       question=user_message,
                                                                       template_key="classification"))
        print(f"Classification model speed: {model_speed} tokens per second")

        if class_model_answer.lower() == "code":
            if execution_mode == "better":
                model = "llama_code"
            else:
                model = "llama_code_lite"
        else:
            if execution_mode == "better":
                model = "llama_ru"
            else:
                model = "llama_ru_lite"

        chat_model_answer, model_speed = models.generate_response(model=model,
                                                                  prompt=models.prompt_template(
                                                                      db_information=db_information,
                                                                      question=user_message,
                                                                      template_key="chat"))
        print(f"{model} model speed: {model_speed} tokens per second")

        return chat_model_answer

    def buffer_memory(user_input: str, bot_reply: str):
        message_pair = f"HUMAN: {user_input}\nAI: {bot_reply}"
        if len(memory) > buffer_memory_counter:
            memory.clear()
            return message_pair
        memory.append(message_pair)
        memory_string = '\n\n'.join(memory)
        return memory_string





    db = VectorDB()
    if db.check_connection() is not None:
        db.get_collection(collection_name='habr')

    models = Models()

    root = tk.Tk()
    root.configure(bg='white')
    my_gui = ChatBotGUI(root, process_function=message_processing_pipeline)
    root.mainloop()
