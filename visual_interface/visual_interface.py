import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk


class ChatBotGUI:
    def __init__(self, master, process_function):
        self.master = master
        self.master.title("Chat Bot")
        self.is_processing = False
        self.execution_mode = "fast"  # Default execution mode
        self.memory_mode = "chat"  # Default memory mode
        self.process_function = process_function
        self.processing_text_index = None

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

        # Create a themed button to choose execution mode
        self.execution_mode_button = ttk.Button(self.master,
                                                text="Execution Mode: Fast",
                                                command=self.toggle_execution_mode,
                                                style='TButton')
        self.execution_mode_button.grid(row=2, column=0, pady=10, sticky='w', padx=5)
        # self.execution_mode_button.grid(row=2, column=0, columnspan=2, pady=2)

        # Create a themed button to choose execution mode
        self.memory_mode_button = ttk.Button(self.master,
                                             text="Memory Mode: Chat",
                                             command=self.toggle_memory_mode,
                                             style='TButton')
        self.memory_mode_button.grid(row=2, column=0, pady=10, sticky='e', padx=5)
        # self.memory_mode_button.grid(row=2, column=0, columnspan=2, pady=2)

        # Create a style for the themed button
        style = ttk.Style()
        style.configure('TButton',
                        font=("Arial", 16),
                        foreground='white',
                        background='#4CAF50',
                        padding=0,
                        borderwidth=0,
                        highlightthickness=0,
                        shiftrelief=-20)
        style.map('TButton', foreground=[('active', '!disabled', 'white')], background=[('active', '#45a049')])

    def send_message(self, event=None) -> None:
        if not self.is_processing:
            # Set the flag to indicate that the bot is processing
            self.is_processing = True

            # Disable entry and button during processing
            self.user_input.config(state='disabled')
            self.send_button.config(state='disabled')
            self.execution_mode_button.state(['disabled'])
            self.memory_mode_button.state(['disabled'])

            message = self.user_input.get()

            self.chat_log.configure(state='normal')
            self.chat_log.insert(tk.END, "You: " + message + "\n\n")
            self.chat_log.configure(state='disabled')

            # Display processing text
            self.chat_log.configure(state='normal')
            self.chat_log.insert(tk.END, "Bot is thinking...\n\n")
            self.processing_text_index = self.chat_log.index(tk.END)
            self.chat_log.configure(state='disabled')

            # Add animation for each message
            self.master.after(0, self.animate_message, self.chat_log.index(tk.END))

            # Process the message and get the reply from the function FOO
            self.master.after(0, self.process_message, message)

    def process_message(self, message: str) -> None:
        reply = self.process_function(message, self.execution_mode, self.memory_mode)
        self.master.after(0, self.echo_message, reply)

    def echo_message(self, message: str) -> None:
        self.chat_log.configure(state='normal')
        self.chat_log.insert(tk.END, "Bot: " + message + "\n\n")
        self.chat_log.configure(state='disabled')

        # Enable entry and button after processing
        self.user_input.config(state='normal')
        self.send_button.config(state='normal')
        self.execution_mode_button.state(['!disabled'])
        self.memory_mode_button.state(['!disabled'])
        self.user_input.delete(0, 'end')

        # Reset the flag after processing is complete
        self.is_processing = False

    def animate_message(self, index: str) -> None:
        self.chat_log.mark_set("start", index)
        self.chat_log.mark_gravity("start", "left")
        self.chat_log.see("start")

    def clear_chat_log(self):
        self.chat_log.configure(state='normal')
        self.chat_log.delete(1.0, tk.END)
        self.chat_log.configure(state='disabled')

    def toggle_execution_mode(self) -> None:
        # Toggle between "fast" and "better" execution modes
        if self.execution_mode == "fast":
            self.execution_mode = "better"
            self.execution_mode_button.config(text="Execution Mode: Better")
        else:
            self.execution_mode = "fast"
            self.execution_mode_button.config(text="Execution Mode: Fast")

    def toggle_memory_mode(self) -> None:
        # Toggle between "fast" and "better" execution modes
        if self.memory_mode == "chat":
            self.memory_mode = "memory_chat"
            self.memory_mode_button.config(text="Memory Mode: Memory Chat")
            self.clear_chat_log()
        else:
            self.memory_mode = "chat"
            self.memory_mode_button.config(text="Memory Mode: Chat")
            self.clear_chat_log()
