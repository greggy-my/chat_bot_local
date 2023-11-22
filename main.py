from db.vector_db import VectorDB
from models import embed_text, Models
import tkinter as tk
from visual_interface.visual_interface import ChatBotGUI

if __name__ == "__main__":
    db = VectorDB()
    if db.check_connection() is not None:
        db.get_collection(collection_name='habr')

    models = Models()


def message_processing_pipeline(user_message: str, execution_mode: str) -> str:
    embeddings = embed_text([user_message])
    db_documents = db.query_current_collection(query_embeddings=embeddings)
    db_information = '\n\n'.join(db_documents["documents"][0])
    class_model_answer, model_speed = models.generate_response(model="llama_class",
                                                                     prompt=models.prompt_template(
                                                                         db_information=db_information,
                                                                         question=user_message,
                                                                         template_key="classification"))
    print(f"Classification model speed: {model_speed} tokens per second")

    if class_model_answer.lower() == "CODE":
        chat_model_answer, model_speed = models.generate_response(model="llama_code",
                                                                        prompt=models.prompt_template(
                                                                            db_information=db_information,
                                                                            question=user_message,
                                                                            template_key="chat"))
        print(f"Code model speed: {model_speed} tokens per second")
    else:
        if execution_mode == "better":
            chat_model_answer, model_speed = models.generate_response(model="llama_ru",
                                                                            prompt=models.prompt_template(
                                                                                db_information=db_information,
                                                                                question=user_message,
                                                                                template_key="chat"))
            print(f"Chat model speed: {model_speed} tokens per second")
        else:
            chat_model_answer, model_speed = models.generate_response(model="llama_ru_lite",
                                                                            prompt=models.prompt_template(
                                                                                db_information=db_information,
                                                                                question=user_message,
                                                                                template_key="chat"))
            print(f"Lite chat model speed: {model_speed} tokens per second")

    return chat_model_answer


root = tk.Tk()
root.configure(bg='white')
my_gui = ChatBotGUI(root, process_function=message_processing_pipeline)
root.mainloop()
