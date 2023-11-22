import tkinter as tk
from tkinter import scrolledtext


class ChatBotGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Chat Bot GUI")

        # Make the interface adaptive to changes in size
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)

        # Create a scrolled text widget to display messages
        self.chat_log = scrolledtext.ScrolledText(self.master, state='disabled')
        self.chat_log.configure(font=("Arial", 16), bg='white', fg='black')
        self.chat_log.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

        # Create an entry widget for user input
        self.user_input = tk.Entry(self.master)
        self.user_input.grid(row=1, column=0, padx=5, pady=5, sticky='ew')

        # Bind the Enter key to the send_message function
        self.user_input.bind("<Return>", self.send_message)

        # Create a button to send messages
        self.send_button = tk.Button(self.master, text="Send", command=self.send_message, font=("Arial", 16))
        self.send_button.grid(row=1, column=1, padx=5, pady=5)

    def send_message(self, event=None):
        message = self.user_input.get()
        self.chat_log.configure(state='normal')
        self.chat_log.insert(tk.END, "You: " + message + "\n")
        self.chat_log.configure(state='disabled')
        self.user_input.delete(0, tk.END)

        # Add animation for each message
        self.master.after(1000, self.animate_message, self.chat_log.index(tk.END))

        # For now, let's just echo the message back
        self.chat_log.configure(state='normal')
        self.chat_log.insert(tk.END, "Bot: " + message + "\n")
        self.chat_log.configure(state='disabled')

    def animate_message(self, index):
        self.chat_log.mark_set("start", index)
        self.chat_log.mark_gravity("start", "left")
        self.chat_log.see("start")

root = tk.Tk()
root.configure(bg='white')
my_gui = ChatBotGUI(root)
root.mainloop()