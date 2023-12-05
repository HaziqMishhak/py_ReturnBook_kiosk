import RPi.GPIO as GPIO
import time
from mfrc522 import SimpleMFRC522
from tkinter import *
import tkinter as tk
from database import DatabaseConnection, UpdateReturnBookTable, BookExistsInBorrowBook
#final 1
# Initialize Tkinter window
class Interface3(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Initialize GPIO and devices
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        self.buzzer_pin = 27
        self.ir_sensor_pin = 22
        GPIO.setup(self.buzzer_pin, GPIO.OUT)
        GPIO.setup(self.ir_sensor_pin, GPIO.IN)
        self.reader = SimpleMFRC522()

        # Initialize database utility classes
        self.db = DatabaseConnection()
        self.return_book_util = UpdateReturnBookTable(self.db)
        self.book_exists_util = BookExistsInBorrowBook(self.db)

        
        # Tkinter variables
        self.book_rfid_label = Label(self, text="NFC Tag located on the inside of the back cover", font=('Helvetica', 18, 'underline'))
        self.rfid_text = StringVar()
        self.rfid_text.set("")

        # Widgets
        self.time_label = Label(self, font=('calibri', 15, 'bold'), background='purple', foreground='white')
        self.time_label.pack(anchor='ne')
        self.back_button = Button(self, text="BACK", command=self.on_back_button_clicked,
                                  bg='#FFA45D', width=10, height=3)
        self.scan_button = Button(self, text="Activate Book Scanner", command=self.scan_rfid, width=25, height=2, bg='#00C1FF')
        self.rfid_label = Label(self, textvariable=self.rfid_text,font=('calibri', 15))
        self.status1_label = Label(self, text="Book Status will be shown here",font=('calibri', 15))
        self.status_label = Label(self, text="Return Status will be shown here",font=('calibri', 15))

        # Layout
        self.time_label.pack(anchor='ne')
        self.back_button.pack(pady=20)
        self.book_rfid_label.pack(pady=10)
        self.scan_button.pack(pady=20)
        self.rfid_label.pack(pady=10)
        self.status1_label.pack(pady=10)
        self.status_label.pack(pady=10)
        
        # Start the clock
        self.update_clock()
    
    # Functions
    def beep_buzzer(self,beep_duration=0.2, times=1, gap_duration=0.2):
        for _ in range(times):
            GPIO.output(self.buzzer_pin, True)
            time.sleep(beep_duration)
            GPIO.output(self.buzzer_pin, False)
            if _ < times - 1:  # No need to wait after the last beep
                time.sleep(gap_duration)

    def update_clock(self):
        if not self.winfo_exists():
            return
        # Get the current local time
        time_string = time.strftime('%d-%m-%Y %H:%M:%S')
        # Update the time label
        self.time_label.config(text=time_string)
        # Call this function again after 1 second
        self.after(1000,self.update_clock)
        
    def on_show_frame(self):
        self.db = DatabaseConnection()
        self.return_book_util = UpdateReturnBookTable(self.db)
        self.book_exists_util = BookExistsInBorrowBook(self.db)

    def wait_for_ir_trigger(self, timeout=7):
        start_time = time.time()
        initial_state = GPIO.input(self.ir_sensor_pin)

        while True:
            current_state = GPIO.input(self.ir_sensor_pin)
            if current_state != initial_state:
                return True
            if time.time() - start_time >= timeout:
                return False
            time.sleep(0.1)
            
    def reset_interface(self):
        self.rfid_text.set("")  # Clear the RFID text
        self.status1_label.config(text="Book Status will be shown here", fg="black")
        self.status_label.config(text="Return Status will be shown here", fg="black")
        
    def on_back_button_clicked(self):
        self.reset_interface()
        self.controller.show_frame("StartPage")
        
    def scan_rfid(self):
        self.scan_button.config(state="disabled")
        start_time = time.time()  # Record the start time
        try:
            self.status1_label.config(text="Book Status will be shown here", fg="black")
            self.status_label.config(text="Return Status will be shown here", fg="black")
            self.rfid_text.set("Please scan your book now...")
            self.update_idletasks()

            while True:
                id, text = self.reader.read_no_block()  # Assuming a non-blocking read method is available
                if id:
                    break  # Exit the loop if a tag is read
                if time.time() - start_time > 5:  # 10 second timeout
                    raise TimeoutError("Scanner reading timed out.")  # Raise an exception if the read times out
                time.sleep(0.1)

            if self.book_exists_util.exists(id):
                self.status1_label.config(text="(Book ID identified) - Please place the book into the return hole.", fg="green")
                self.beep_buzzer(times=1)
                self.update_idletasks()
            else:
                self.status1_label.config(text="(Book ID not recognized) - Please consult library staff or try again.", fg="red")
                self.beep_buzzer(times=3)
                self.update_idletasks()
                return  # Exit the method if the book is not found

            if self.wait_for_ir_trigger():
                status_returned, fine_amount = self.return_book_util.update(id)
                if status_returned == "On-Time":
                    self.status_label.config(text="(On-Time) - Return processed successfully. Thank you.", fg="green")
                    self.beep_buzzer(times=2)
                elif status_returned == "Late":
                    self.status_label.config(text=f"Return processed with a delay. Fine incurred: RM{fine_amount}. Please proceed to the payment counter.", fg="purple")
                    self.beep_buzzer(beep_duration=1, times=1)
                else:
                    self.status_label.config(text="Return processing failed. Unable to update return status.", fg="red")
                    self.beep_buzzer(times=3)
            else:
                self.status_label.config(text="Error: No book detected in the return slot. Return unsuccessful.", fg="red")
                self.beep_buzzer(times=3)

        except Exception as e:
            self.status_label.config(text=str(e), fg="red")
        except TimeoutError as e:
            logging.error(f"Error in scanning the tag: {e}")
        finally:
            self.scan_button.config(state="normal")

            
