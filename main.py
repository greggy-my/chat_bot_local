from db.vector_db import VectorDB
from models import embed_text, Models
import tkinter as tk
from visual_interface.visual_interface import ChatBotGUI

if __name__ == "__main__":

    chat_memory = []
    BUFFER_MEMORY_COUNTER = 5

    def message_processing_pipeline(user_message: str, execution_mode: str, memory_mode: str) -> str:
        print(f"Memory mode from visual interface: {memory_mode}")
        memory_string = ""
        embeddings = embed_text([user_message])
        db_documents = db.query_current_collection(query_embeddings=embeddings)
        db_information = str(db_documents["documents"][0])
        print(f"Информация из Хабра: {db_information}")
        class_model_answer, model_speed = models.generate_response(model="llama_class",
                                                                   prompt=models.prompt_template(
                                                                       db_information=db_information,
                                                                       question=user_message,
                                                                       template_key="classification",
                                                                       chat_memory=memory_string))
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

        print(f"Chosen model: {model}")

        if (memory_mode == 'memory_chat') and (len(chat_memory) < BUFFER_MEMORY_COUNTER):
            template_key = 'memory_chat'
            memory_string = '\n'.join(chat_memory) + f"\nHuman: {user_message}\nAI:"
        else:
            template_key = "chat"
            chat_memory.clear()

        print(f'Template key: {template_key}')
        print(f'\nMemory:\n{memory_string}')

        chat_model_answer, model_speed = models.generate_response(model=model,
                                                                  prompt=models.prompt_template(
                                                                      db_information=db_information,
                                                                      question=user_message,
                                                                      template_key=template_key,
                                                                      chat_memory=memory_string))

        print(f"{model} model speed: {model_speed} tokens per second")

        if memory_mode == 'memory_chat':
            message_pair = f"\nHuman: {user_message}\nAI: {chat_model_answer}\n"
            chat_memory.append(message_pair)

        return chat_model_answer


    db = VectorDB()
    if db.check_connection() is not None:
        db.get_collection(collection_name='habr')

    models = Models()

    root = tk.Tk()
    root.configure(bg='white')
    my_gui = ChatBotGUI(root, process_function=message_processing_pipeline)
    root.mainloop()
