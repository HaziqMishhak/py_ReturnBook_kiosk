import RPi.GPIO as GPIO
import time
from mfrc522 import SimpleMFRC522
from tkinter import *
import tkinter.ttk as ttk
import tkinter as tk
from database import DatabaseConnection

# Initialize GPIO and devices
class Interface2(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Initialize GPIO and RFID reader
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        self.buzzer_pin = 27
        self.ir_sensor_pin = 22
        GPIO.setup(self.buzzer_pin, GPIO.OUT)
        GPIO.setup(self.ir_sensor_pin, GPIO.IN)
        self.reader = SimpleMFRC522()

        # Initialize database connection
        self.db_helper = DatabaseConnection()

        # UI Components
        self.back_button = tk.Button(self, text="BACK", command=lambda: controller.show_frame("StartPage"),
                                  bg='#FFA45D', width=10, height=3)

        self.scan_button = tk.Button(self, text="Click to scan your matrik card",
                                     command=self.handle_scan_click, width=30, height=3, bg='#00C1FF')
        
        self.text_label = Label(self, text="Data Only show for Unreturned Book",font=('calibri', 15))
        

        # Table for displaying data
        columns = ("StudentID", "BookName", "BorrowDateTime", "DueTime")
        self.table = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.table.heading(col, text=col)

        # Layout
        self.back_button.pack(pady=20)
        self.scan_button.pack(pady=40)
        self.text_label.pack(pady=10)
        self.table.pack(pady=20)
        
    def tkraise(self, aboveThis=None):
        """Override tkraise to reset the interface state each time the frame is shown."""
        super().tkraise(aboveThis)  # Call the parent class's raise method
        
        # Clear previous data from the table
        for row in self.table.get_children():
            self.table.delete(row)

    # Event Handlers
    def handle_scan_click(self):
        # Scan RFID
        _, student_id_text = self.reader.read()
        self.beep_buzzer(0.5)  # Beep once after scanning

        # Clear previous data from the table
        for row in self.table.get_children():
            self.table.delete(row)

        # Fetch borrowed books data for the student
        book_data = self.db_helper.fetch_borrowed_books_by_student_id(student_id_text)
        for data in book_data:
            self.table.insert("", "end", values=data)

    # Buzzer beep function
    def beep_buzzer(self, beep_duration=0.2, times=1, gap_duration=0.2):
        for _ in range(times):
            GPIO.output(self.buzzer_pin, True)
            time.sleep(beep_duration)
            GPIO.output(self.buzzer_pin, False)
            if _ < times - 1:  # No need to wait after the last beep
                time.sleep(gap_duration)
                
