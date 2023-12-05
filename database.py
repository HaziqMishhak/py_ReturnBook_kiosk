import mysql.connector
import datetime
import logging
#final 1
logging.basicConfig(level=logging.ERROR)

class DatabaseConnection:
    def __init__(self):
        # database configuration
        self.db_config = {
            "host": "sv83.ifastnet.com",
            "user": "libraryu_admin",
            "password": "Kafka!271101",
            "database": "libraryu_final"
        }

    def get_connection(self):
        self.conn = mysql.connector.connect(**self.db_config)
        return self.conn
    
    def close_connection(self):
        try:
            if self.conn and self.conn.is_connected():
                self.conn.close()
                self.conn = None  # Set the connection back to None after closing
        except Exception as e:
            logging.error(f"Error closing the database connection: {e}")
    
    def fetch_borrowed_books_by_student_id(self,student_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT s.StudentID, b.BookName, bb.BorrowDateTime, bb.DueTime
            FROM Students AS s
            JOIN BorrowBook AS bb ON s.StudentID = bb.StudentID
            JOIN Books AS b ON bb.BookID = b.BookID
            WHERE s.StudentID = %s
            AND bb.Status != 'Returned';  # Only fetch books that haven't been returned"""
        
        cursor.execute(query, (student_id,))
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return results # Return the fetched results

class BookExistsInBorrowBook:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def exists(self, book_id):
        try:
            # Here we make sure to get a fresh connection
            conn = self.db_connection.get_connection()
            cursor = conn.cursor()
            query = "SELECT COUNT(*) FROM BorrowBook WHERE BookID = %s AND Status != 'Returned';"
            cursor.execute(query, (book_id,))
            result = cursor.fetchone()[0] 
            cursor.close()
            conn.close()
            return result > 0  # Return True if exists, otherwise False
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            return False

class UpdateReturnBookTable:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def update(self, book_id):
        conn = None
        cursor = None
        try:
            conn = self.db_connection.get_connection()
            cursor = conn.cursor()
            # Get the due time and BorrowID for the book
            query_due_time_and_borrow_id = """
            SELECT BorrowID, DueTime 
            FROM BorrowBook 
            WHERE BookID = %s AND Status != 'Returned'
            """
            cursor.execute(query_due_time_and_borrow_id, (book_id,))
            result = cursor.fetchone()

            if result is None:
                # Book not found or already returned
                cursor.close()
                return "Book not found or already returned", 0

            borrow_id, due_time = result
            current_time = datetime.datetime.now()

            fine_amount = 0
            status = "On-Time"
            fine_status = None  # Initializing fine_status

            if current_time > due_time:
                # Calculate the fine
                days_late = (current_time - due_time).days
                fine_amount = days_late * 2  # Fine amount calculation logic
                status = "Late"
                fine_status = "Pending"  # Set fine status only if late

            # Insert into ReturnBook table with status
            query_insert_return = """
            INSERT INTO ReturnBook (BorrowID, ReturnDate, Status)
            VALUES (%s, %s, %s);
            """
            cursor.execute(query_insert_return, (borrow_id, current_time, status))
            return_id = cursor.lastrowid  # Assuming you have an auto-increment ID for ReturnBook

            if fine_status:  # This will only be true if the book is late and there is a fine
                # Insert into Fine table if there is a fine
                query_insert_fine = """
                INSERT INTO Fine (ReturnID, AmountDue, PaymentStatus)
                VALUES (%s, %s, %s);
                """
                cursor.execute(query_insert_fine, (return_id, fine_amount, fine_status))

            # Update the status in BorrowBook table
            query_update_borrow = """
            UPDATE BorrowBook 
            SET Status = 'Returned' 
            WHERE BookID = %s
            """
            cursor.execute(query_update_borrow, (book_id,))

            conn.commit()
            return status, fine_amount
        
        except Exception as e:
            print(f"An error occurred: {e}")
            if conn:
                conn.rollback()
        
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
            
            


