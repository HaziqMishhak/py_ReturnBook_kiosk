import tkinter as tk
from PIL import Image, ImageTk

# Assuming Interface2 and Interface3 are now classes that inherit from tk.Frame
from interface2 import Interface2
from interface3 import Interface3

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Library return book")
        self.configure(bg="light grey")
        
        self.attributes('-fullscreen', True)
        
        # Frames
        self.frames = {}

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Initializing all frames
        for F in (StartPage, Interface2, Interface3):
            frame = F(container, self)
            self.frames[F.__name__] = frame  # Use the class name as the key
            print(f"Frame {F.__name__} added to dictionary with object {frame}")
            frame.grid(row=0, column=0, sticky="nsew")


        self.show_frame("StartPage")

    def show_frame(self, context):
        frame = self.frames.get(context)
        if frame:
            frame.tkraise()
        else:
            raise ValueError(f"No such frame: {context}")


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg="light grey")

        # Set up the grid for the entire frame
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Logo
        logo_path = "logo.png"
        logo_image = Image.open(logo_path)
        aspect_ratio = logo_image.height / logo_image.width
        new_height = int(250 * aspect_ratio)
        logo_image_resized = logo_image.resize((250, new_height))
        logo_photo = ImageTk.PhotoImage(logo_image_resized)
        logo_label = tk.Label(self, image=logo_photo, bg="light grey")
        logo_label.image = logo_photo  # keep a reference!
        logo_label.grid(row=0, column=0, columnspan=2, pady=20)  # Spans over two columns

        title_label = tk.Label(self, text="Library Return Book", font=("Arial", 35), bg="light grey")
        title_label.grid(row=1, column=0, columnspan=2, pady=20)  # Spans over two columns

        # Create buttons
        borrow_button = tk.Button(self, text="Check your Borrow book", width=40, height=8,
                          command=lambda: controller.show_frame("Interface2"),font=('calibri', 13))
        return_button = tk.Button(self, text="Return Book", width=40, height=8,
                          command=lambda: controller.show_frame("Interface3"),font=('calibri', 13))

        # Position the buttons in the grid
        borrow_button.grid(row=2, column=0, padx=40)
        return_button.grid(row=2, column=1, padx=40)


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
