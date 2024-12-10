import tkinter
import tkinter.messagebox
import customtkinter
import time
import datetime
import threading
import sys

from websockets.sync.server import serve
from websockets.sync.client import connect

from send_recv import send, recv

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


""" 

Send on client to server
Receive on server from client

"""


app = None  # Declare app globally
target = None
port = None
Font_mono = ("Courier New", 13, "normal") 

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.history = []
        self.client = None
        self.server = None
        self.lines = 0

        # configure window
        self.title("ws-p2p-multi | Disconnected")
        self.geometry(f"{1100}x{580}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # create tabview
        self.tabview = customtkinter.CTkTabview(self, width=400)
        self.tabview.grid(row=0, column=0, columnspan=4, rowspan=4, padx=(20, 20), pady=(5, 10), sticky="nsew")
        
        # Add tabs
        self.tabview.add("Tab 1")
        self.tabview.add("Tab 2")
        self.tabview.add("Tab 3")

        # Configure grid for individual tabs
        for tab in ["Tab 1", "Tab 2", "Tab 3"]:
            self.tabview.tab(tab).grid_columnconfigure(1, weight=1)
            self.tabview.tab(tab).grid_columnconfigure((2, 3), weight=0)
            self.tabview.tab(tab).grid_rowconfigure((0, 1, 2), weight=1)

        # Example: Adding a label to each tab
        for i, tab in enumerate(["Tab 1", "Tab 2", "Tab 3"], start=1):

            if i == 1:
                self.textbox = customtkinter.CTkTextbox(self.tabview.tab(tab), width=250)
                self.textbox.grid(row=0, column=0, columnspan=4, rowspan=3, padx=(10, 10), pady=(10, 10), sticky="nsew")
                self.textbox.configure(state="disabled")

                self.textbox.configure(font=Font_mono)
                self.textbox.tag_config('colour_you', foreground="#85bd84")
                self.textbox.tag_config('colour_friend', foreground="#7c87d6")
                self.textbox.tag_config('colour_alert', foreground="#bf6767")

                # create main entry and button
                self.entry = customtkinter.CTkEntry(self.tabview.tab(tab), placeholder_text="Message")
                self.entry.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

                self.main_button_1 = customtkinter.CTkButton(master=self.tabview.tab(tab), text="Send", command=self.send_message, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
                self.main_button_1.grid(row=3, column=3, padx=10, pady=10, sticky="nsew")

    def recv_message(self, message, sender="Friend"):
        self.history.append({
            "sender": sender,
            "message": message,
            "time": datetime.datetime.now()
        })
        self.update_chat()

    def update_chat(self):
        self.textbox.configure(state="normal")

        new = (len(self.history) - self.lines)
        to_add = self.history[-new:]

        for i, message in enumerate(to_add, start=1):  # Start from 1 for line numbers

            if message['sender'] == "You":
                self.textbox.insert(tkinter.END, f"[{message['time'].strftime("%d/%m/%Y %H:%M:%S")}] {message['sender'].ljust(6)} : {message['message']}\n", "colour_you")
            elif message['sender'] == "Friend":
                self.textbox.insert(tkinter.END, f"[{message['time'].strftime("%d/%m/%Y %H:%M:%S")}] {message['sender'].ljust(6)} : {message['message']}\n", "colour_friend")
            elif message['sender'] == "Alert":
                self.textbox.insert(tkinter.END, f"[{message['time'].strftime("%d/%m/%Y %H:%M:%S")}] {message['sender'].ljust(6)} : {message['message']}\n", "colour_alert")
            elif message['sender'] == "Divider":
                self.textbox.insert(tkinter.END, f"{'-'*80}\n")
                self.textbox.insert(tkinter.END, f"{message['message']}\n")
                self.textbox.insert(tkinter.END, f"{'-'*80}\n")
            else:
                self.textbox.insert(tkinter.END, f"[{message['time'].strftime("%d/%m/%Y %H:%M:%S")}] {message['sender'].ljust(6)} : {message['message']}\n")

        self.lines += 1
        self.textbox.configure(state="disabled")
        self.textbox.see(tkinter.END)

    def is_connected(self):
        #if (self.client is not None and self.client.state == 1):
            #print(self.client.state)

        if (self.server):
            print(self.server.state)

        if (self.client is not None and self.client.state == 1 and self.server is not None and self.server.state == 1):
            self.title("ws-p2p-multi | Connected")
            
            self.recv_message("Two-way communication established", sender="Divider")
        else:
            self.title("ws-p2p-multi | Disconnected")

    def send_message(self):
        message = self.entry.get()
        if message == "":
            return

        self.entry.delete(0, tkinter.END)
        send(message)

        if self.client:   # Check if client is initialized
            try:
                self.client.send(message)
                self.recv_message(message, sender="You")
            except Exception as e:
                self.recv_message(f"Failed to send message: {str(e)}", sender="Alert")
        else:
            self.recv_message("Client not connected", sender="Alert")

def handler(websocket):
    app.recv_message("Client connected", sender="Alert")
    app.server = websocket
    app.is_connected()
    while websocket.state:
        try:
            # Wait for incoming messages
            message = websocket.recv()
            decoded_message = recv(message)  # Assuming recv is your custom function to decode messages
            app.recv_message(decoded_message, sender="Friend")
        except Exception as e:
            app.recv_message(f"Failed to receive or decode message: {str(e)}", sender="Alert")
            # If an error occurs, you might want to decide whether to close the connection or keep listening
            break

def run_server():
    with serve(handler, "localhost", port) as server:
        app.recv_message(f"Server started listening on port {port}", sender="Alert")
        server.serve_forever()

def run_client():
    print(f"ws://{target}")
    
    while True:
        try:
            with connect(f"ws://{target}") as client:
                app.recv_message(f"Connected to {target}", sender="Alert")
                app.client = client
                app.is_connected()
                
                # Keep the connection open
                while client.state:
                    try:
                        message = client.recv()
                        try:
                            decoded_message = recv(message)
                            app.recv_message(decoded_message, sender="Friend")
                        except Exception as e:
                            app.recv_message(f"Failed to decode message: {str(e)}", sender="Alert")
                    except Exception as e:
                        app.recv_message(f"Client disconnected: {str(e)}", sender="Alert")
                        break
        except Exception as e:
            app.recv_message(f"Failed to connect to server on port {port}: {str(e)}", sender="Alert")
            # Wait before retrying to avoid spamming the server with connection attempts
            time.sleep(5)

def main(arg_target, arg_port):
    global app
    app = App()

    global target
    target = arg_target

    global port
    port = int(arg_port)
    
    # Start the WebSocket server in a separate thread
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True  # This thread will be killed when the main program exits
    server_thread.start()

    client_thread = threading.Thread(target=run_client)
    client_thread.daemon = True
    client_thread.start()
    
    # Start the Tkinter main loop
    app.mainloop()

if __name__ == "__main__":

    arg_target = None
    arg_port = None

    # If you want to handle each argument individually:
    for i, arg in enumerate(sys.argv[1:], 1):
        if (arg == '--target'):
            arg_target = sys.argv[1:][i]
        elif (arg == '--port'):
            arg_port = sys.argv[1:][i]
        
    main(arg_target, arg_port)