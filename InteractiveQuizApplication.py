import tkinter as tk
from tkinter import messagebox, ttk
import random
import smtplib
import re
import requests
import json
import os
import uuid
import time
import pyperclip
import tkinter.simpledialog
from threading import Thread

class FadeInLabel(tk.Label): # Inherits from tk.Label
    def __init__(self, master, **kwargs): # **kwargs allows us to pass keyword arguments to the tk.Label constructor
        tk.Label.__init__(self, master, **kwargs)
        self.alpha = 0
        self.fade_in()

    def fade_in(self): # Fade in animation
        for alpha in range(0, 255, 5):
            rgba = self.winfo_rgb(self.cget("bg")) + (alpha,)
            color = "#%02x%02x%02x" % rgba[:3]
            self.configure(bg=color)
            self.update_idletasks()
            time.sleep(0.01)

    def pack(self, **kwargs):   # Override the pack method
        tk.Label.pack(self, **kwargs)
        self.fade_in()

class AnimatedButton(ttk.Button): # Inherits from ttk.Button
    def __init__(self, master, **kwargs): # **kwargs allows us to pass keyword arguments to the ttk.Button constructor
        ttk.Button.__init__(self, master, **kwargs)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event): # Event handler for the <Enter> event
        self.config(style="Hover.TButton")
        self.update()

    def on_leave(self, event): # Event handler for the <Leave> event
        self.config(style="TButton")
        self.update()

class AnimatedToplevel(tk.Toplevel): # Inherits from tk.Toplevel
    def __init__(self, master, **kwargs): # **kwargs allows us to pass keyword arguments to the tk.Toplevel constructor
        tk.Toplevel.__init__(self, master, **kwargs)
        self.overrideredirect(True)
        self.attributes("-alpha", 0)
        self.fade_in()

    def fade_in(self): # Fade out animation
        for alpha in range(0, 101, 5):
            self.attributes("-alpha", alpha/100)
            self.update_idletasks()
            time.sleep(0.01)
        self.attributes("-alpha", 1)  # Ensure the window is fully visible

    def fade_out(self): # Fade out animation
        for alpha in range(100, -1, -5):
            self.attributes("-alpha", alpha/100)
            self.update_idletasks()
            time.sleep(0.01)
        self.destroy()

class AnimatedLabel(tk.Label): # Inherits from tk.Label
    def __init__(self, master, **kwargs):
        tk.Label.__init__(self, master, **kwargs)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event): # Event handler for the <Enter> event
        self.config(fg="blue")
        self.update()

    def on_leave(self, event): # Event handler for the <Leave> event
        self.config(fg="black")
        self.update()

class AnimatedRadioButton(ttk.Radiobutton): # Inherits from ttk.Radiobutton
    def __init__(self, master, variable, value, **kwargs): # **kwargs allows us to pass keyword arguments to the ttk.Radiobutton constructor
        super().__init__(master, variable=variable, value=value, **kwargs)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self.config(style="Hover.TRadiobutton")
        self.update()

    def on_leave(self, event):
        self.config(style="TRadiobutton")
        self.update()


class User: # User class to store user details
    def __init__(self, id, name, email, password): # Constructor
        self.id = id
        self.name = name
        self.email = email
        self.password = password

class Question: # Question class to store question details
    def __init__(self, question, answers, correct_answer): # Constructor
        self.question = question
        self.answers = answers
        self.correct_answer = correct_answer

class QuizApp: # QuizApp class
    def __init__(self, root): # Constructor
        self.root = root # Store the root window
        self.root.title("Interactive Quiz App") # Set the title of the root window
        self.root.geometry("500x300") # Set the size of the root window
        self.current_user_id = None  # Initialize current_user_id to None

        self.title_label = FadeInLabel(self.root, text="Interactive Quiz App", font=("Helvetica", 24, "bold"), fg="blue", bg="white")
        self.title_label.pack(pady=20) # Pack the title label

        self.login_button = AnimatedButton(self.root, text="Login", command=self.show_login) # Create the login button
        self.login_button.pack(side=tk.LEFT, padx=125) # Pack the login button

        self.signup_button = AnimatedButton(self.root, text="Sign Up", command=self.show_signup) # Create the signup button
        self.signup_button.pack(side=tk.LEFT, padx=10)  # Pack the signup button

        self.quiz = Quiz() # Create a Quiz object

        self.users = self.load_users() # Load users from users.json
    
    def center_window(self, window, width, height): # Center a window
        screen_width = window.winfo_screenwidth() 
        screen_height = window.winfo_screenheight()

        x = (screen_width - width) // 2  # Calculate x and y coordinates to center a window
        y = (screen_height - height) // 2

        window.geometry(f"{width}x{height}+{x}+{y}")   # Set the geometry of the window to width x height + x_offset + y_offset

    def clear_widgets(self): # Clear all widgets from the root window
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login(self): # Show the login page
        self.clear_widgets() # Clear all widgets from the root window
        
        self.username_label = AnimatedLabel(self.root, text="Username / Userid:") # Create the username label
        self.username_label.pack(pady=10) # Pack the username label

        self.username_entry = tk.Entry(self.root, width=30) # Create the username entry
        self.username_entry.pack() # Pack the username entry

        self.password_label = AnimatedLabel(self.root, text="Password:") # Create the password label
        self.password_label.pack(pady=10) # Pack the password label

        self.password_entry = tk.Entry(self.root, show="*", width=30) # Create the password entry
        self.password_entry.pack() # Pack the password entry

        self.login_button = AnimatedButton(self.root, text="Login", command=self.user_login) # Create the login button
        self.login_button.pack(pady=10) # Pack the login button

        self.signup_prompt_label = AnimatedLabel(self.root, text="Don't have an account?", pady=20) # Create the signup prompt label
        self.signup_prompt_label.pack() # Pack the signup prompt label

        self.signup_button = AnimatedButton(self.root, text="Sign Up", command=self.show_signup)    # Create the signup button
        self.signup_button.pack(pady=10) # Pack the signup button

        self.center_window(self.root, 500, 300) # Center the root window

    def show_signup(self):
        self.clear_widgets()

        self.name_label = AnimatedLabel(self.root, text="Name:")
        self.name_label.pack()

        self.name_entry = tk.Entry(self.root, width=30)
        self.name_entry.pack(pady=10)

        self.email_label = AnimatedLabel(self.root, text="Email:")
        self.email_label.pack()

        self.email_entry = tk.Entry(self.root, width=30)
        self.email_entry.pack(pady=10)

        self.signup_button = AnimatedButton(self.root, text="Sign Up", command=self.send_otp)
        self.signup_button.pack()

        self.error_label = AnimatedLabel(self.root, text="", fg="red")
        self.error_label.pack()

        self.valid_email_label = AnimatedLabel(self.root, text="", fg="green")
        self.valid_email_label.pack()

        self.signup_prompt_label = AnimatedLabel(self.root, text="Already have an account?", pady=20)
        self.signup_prompt_label.pack()

        self.signup_button = AnimatedButton(self.root, text="Sign In", command=self.show_login)
        self.signup_button.pack()

        self.center_window(self.root, 500, 300)

    def user_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Username and password are required")
            return

        existing_user_id = self.check_user_name_id_password(username, password)
        if existing_user_id != "":
            self.current_user_id = existing_user_id  # Set the current_user_id
            self.root.withdraw()
            self.show_quiz()
        else:
            messagebox.showerror("Error", "User does not exist or incorrect password")

    def check_user_name_id_password(self, username, password):
        for user in self.users:
            if (user.name.upper() == username.upper() or user.id == username) and user.password == password:
                return user.id
        return ""

    def load_users(self):
        if os.path.exists("users.json"):
            with open("users.json", "r") as file:
                users_data = json.load(file)
                users = [User(data["id"], data["name"], data["email"], data["password"]) for data in users_data]
                return users
        else:
            return []

    def save_users(self):
        users_data = [{"id": user.id, "name": user.name, "email": user.email, "password": user.password} for user in self.users]
        with open("users.json", "w") as file:
            json.dump(users_data, file)

    def register_new_user(self, id, name, email, password):
        self.users.append(User(id, name, email, password))
        self.save_users()

    def send_otp(self):
        email = self.email_entry.get()

        if not self.is_valid_email(email):
            self.error_label.config(text="Invalid email address")
            self.valid_email_label.config(text="")
            return
        existing_user = self.get_user_by_name(self.name_entry.get())
        if existing_user:
            self.error_label.config(text="User already exists, Select a different username")
            return
        self.error_label.config(text="")
        self.valid_email_label.config(text=f"Valid email: {email}", fg="green")
        otp = str(random.randint(1000, 9999))
        self.send_email(email, "OTP Verification", f"Your OTP: {otp}")
        self.verify_otp(otp)

    def is_valid_email(self, email):
        pattern = r"^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$"
        return re.match(pattern, email)

    def verify_otp(self, otp):
        self.verify_window = tk.Toplevel()
        self.verify_window.title("Verify OTP")
        self.verify_window.geometry("300x150")

        # Aniamtion label for the OTP
        self.otp_label = FadeInLabel(self.verify_window, text="Enter OTP:", font=("Helvetica", 12, "bold"), fg="blue", bg="white")
        self.otp_label.pack(pady=10)

        self.otp_entry = tk.Entry(self.verify_window)
        self.otp_entry.pack(pady=10)

        # Animation for the verify button
        self.verify_button = AnimatedButton(self.verify_window, text="Verify", command=lambda:self.register_or_login(otp))
        self.verify_button.pack(pady=5)

    def register_or_login(self, otp):
        if self.otp_entry.get() == otp:
            messagebox.showinfo("OTP", "OTP verified")
            self.verify_window.destroy()
            
            user_id = str(uuid.uuid4())  # Generate a unique ID for the user
            # take password from user on a new window
            self.register_window = tk.Toplevel()
            self.register_window.title("Register")
            self.register_window.geometry("300x150")
            
            # center the window
            self.center_window(self.register_window, 300, 150)
            
            # Label for the Password
            self.password_label = tk.Label(self.register_window, text="Password:")
            self.password_label.pack(pady=10)
            # Animation for the password entry
            self.password_entry = tk.Entry(self.register_window, show="*")
            self.password_entry.pack(pady=10)
            # Animation for the register button
            self.register_button = AnimatedButton(self.register_window, text="Register", command=lambda:self.register_user(user_id))
            self.register_button.pack(pady=5)
                
        else:
            messagebox.showerror("Error", "Incorrect OTP")

    def register_user(self, user_id):
        # send email with user ID
        subject = "User ID for Interactive Quiz App"
        # descriptive body with name of user and user ID (This is the ID that will be used to login)
        body = f"Dear {self.name_entry.get()},\n\nYour user ID is {user_id}.\n\nRegards,\nInteractive Quiz App"
        self.send_email(self.email_entry.get(), subject, body)
        password = self.password_entry.get()
        
        # save user ID, name, email and password in users.json
        self.register_new_user(user_id, self.name_entry.get(), self.email_entry.get(), password)
        self.verify_window.destroy()

        messagebox.showinfo("Registration", f"Registration successful. Your user ID: {user_id}")
        self.copy_to_clipboard_prompt(user_id)

        # take user to login page
        self.show_login()

    def copy_to_clipboard_prompt(self, user_id):
        result = tkinter.simpledialog.askstring("Copy to Clipboard", "Do you want to copy your user ID to the clipboard?\n\nYour user ID:", initialvalue=user_id)
        if result == user_id:
            pyperclip.copy(user_id)
            messagebox.showinfo("Copied to Clipboard", "User ID copied to clipboard")
            return


    def get_user_by_id(self, user_id):
        for user in self.users:
            if user.id == user_id:
                return user
        return None

    def get_user_by_name(self, user_name):
        for user in self.users:
            if user.name.upper() == user_name.upper():
                return user
        return None

    def show_quiz(self):
        self.quiz_window = tk.Toplevel()
        self.quiz_window.title("Quiz")
        self.quiz_window.geometry("600x400")
        self.center_window(self.quiz_window, 600, 400)

        self.current_question = 0
        self.score = 0
        self.choices = []

        self.show_question()

    def show_question(self):
        self.quiz_window.destroy()
        self.quiz_window = tk.Toplevel()
        self.quiz_window.title(f"Question {self.current_question + 1}/10")
        self.quiz_window.geometry("600x400")
        self.center_window(self.quiz_window, 600, 400)
        
        question_text = self.quiz.questions[self.current_question].question
        question_label = AnimatedLabel(self.quiz_window, text=question_text, wraplength=550)
        question_label.pack()

        self.selected_choice = tk.StringVar(value="")  # Initially set to an empty value

        for i, choice in enumerate(self.quiz.questions[self.current_question].answers):
            radio_button = AnimatedRadioButton(self.quiz_window, variable=self.selected_choice, value=i, text=choice)
            radio_button.pack(anchor="w", padx=10, pady=5)
            self.selected_choice.set(None)  # Deselect the radio button

        self.timer_label = tk.Label(self.quiz_window, text="Timer: 5 seconds", fg="red")
        self.timer_label.pack(pady = 10)

        self.start_timer()  # Start the timer

        if self.current_question >= len(self.quiz.questions) - 1:
            action_button = AnimatedButton(self.quiz_window, text="Submit", command=self.show_results)
        else:
            action_button = AnimatedButton(self.quiz_window, text="Next", command=self.show_next_question)
            
        action_button.pack()

    def start_timer(self):
        self.timer_seconds = 5
        self.update_timer()

    def update_timer(self):
        if self.timer_seconds > 0:
            self.timer_label.config(text=f"Timer: {self.timer_seconds} seconds")
            self.timer_seconds -= 1
            self.quiz_window.after(1000, self.update_timer)
        else:
            self.timer_label.config(text="Timer: Time's up!")
            
        if self.current_question < len(self.quiz.questions) - 1:
            self.quiz_window.after(6000, self.show_next_question)
        else:
            self.quiz_window.after(6000, self.show_results)

    def show_next_question(self):
        self.check_answer()  # Check the answer for the current question
        self.current_question += 1 # Move to the next question
        self.show_question()

    def check_answer(self):
        selected_choice = self.selected_choice.get()

        if selected_choice is not None and selected_choice != "":
            # self.current_question is the index of the current question and is also the index of the user's choice for that question
            # IndexError: list index out of range if current_question is greater than the number of questions
            if self.current_question < len(self.quiz.questions): 
                if selected_choice.isdigit() and int(selected_choice) == self.quiz.questions[self.current_question].correct_answer:
                    self.score += 1

        self.choices.append(selected_choice)

        if self.current_question <= len(self.quiz.questions) - 1:
            self.show_question()  # Show the next question

    def show_results(self): 
        while self.current_question < len(self.quiz.questions):
            self.current_question += 1
            self.check_answer()

        self.quiz_window.destroy() # Close the quiz window

        results_window = tk.Toplevel() # Open the results window
        results_window.title("Results") 
        results_window.geometry("400x400")
        self.center_window(results_window, 400, 400)  # Center the results window
        self.animate_fade_in(results_window)  # Apply fade-in animation

        current_user = self.get_user_by_id(self.current_user_id)  # Retrieve the current user
        result_label = tk.Label(results_window, text=f"Hi {current_user.name}, your score is {self.score}/{len(self.quiz.questions)}")
        result_label.pack()

        report_label = tk.Label(results_window, text="Detailed Report:")
        report_label.pack()

        report_text = tk.Text(results_window, wrap="word", height=10, width=40)
        report_text.pack()

        for i, question in enumerate(self.quiz.questions):
            # self.choices[i] is the user's choice for question i and is None if the user did not answer the question
            # IndexError: list index out of range if the user did not answer the question
            # So we check if self.choices[i] is not None and is a digit before retrieving the user's answer
            if  i < len(self.choices) and self.choices[i] is not None: 
                user_answer_index = self.choices[i]
            else:
                user_answer_index = None
            if user_answer_index is not None and user_answer_index.isdigit():
                user_answer = question.answers[int(user_answer_index)]
            else:
                user_answer = "No answer provided"

            report_text.insert(tk.END, f"Question {i+1}: {question.question}\n")
            report_text.insert(tk.END, f"Your answer: {user_answer} \n")
            correct_answer = question.answers[question.correct_answer]
            report_text.insert(tk.END, f"Correct answer: {correct_answer}\n")
            report_text.insert(tk.END, "--------------------------\n")

        self.send_results_button = AnimatedButton(results_window, text="Send Results", command=self.send_results)
        self.send_results_button.pack(pady=10)

        self.re_attempt_button = AnimatedButton(results_window, text="Re-attempt Quiz", command=self.show_quiz)
        self.re_attempt_button.pack()

        self.exit_button = AnimatedButton(results_window, text="Exit", command=exit)
        self.exit_button.pack(pady=10)

    def animate_fade_in(self, window):
        window.attributes("-alpha", 0.0)  # Set initial alpha to 0 (fully transparent)
        window.update_idletasks()  # Update the window to apply initial alpha setting

        fade_duration = 1000  # Duration of the fade-in animation in milliseconds
        steps = 50  # Number of animation steps

        for i in range(steps + 1):
            alpha = i / steps
            window.attributes("-alpha", alpha)  # Update alpha value
            window.update_idletasks()  # Update the window
            window.after(int(fade_duration / steps))

    def send_results(self):
        subject = "Quiz Results for Interactive Quiz App"
        current_user = self.get_user_by_id(self.current_user_id)  # Retrieve the current user
        email = current_user.email
        name = current_user.name

        body = f"Dear {name},\n\nYour score is {self.score}/{len(self.quiz.questions)}.\n\nDetailed Report:\n"
        for i, question in enumerate(self.quiz.questions):
            # question.text is the question text can be obtained from the question object
            body += f"Question {i+1}: {question.question}\n"

            if self.choices[i] is not None:
                # ValueError: invalid literal for int() with base 10: 'None' if self.choices[i] is None and is passed to int() function
                # So we check if self.choices[i] is not None and is a digit before retrieving the user's answer
                if self.choices[i].isdigit():
                    chosen_answer = question.answers[int(self.choices[i])]
                    body += f"Your answer: {chosen_answer}\n"
            else:
                body += "Your answer: Not answered\n"

            correct_answer = question.answers[question.correct_answer]
            body += f"Correct answer: {correct_answer}\n\n"

        self.send_email(email, subject, body)
        messagebox.showinfo("Results Sent", "Quiz results have been sent to your email.")
        exit()

    def send_email(self, recipient, subject, body):
        sender_email = "youremail@gmail.com"
        # how to get app password for gmail account
        # https://support.google.com/accounts/answer/185833?hl=en
        sender_password = "yourapppassword"
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        message = f"Subject: {subject}\n\n{body}"
        server.sendmail(sender_email, recipient, message)
        server.quit()

class Quiz:
    def __init__(self):
        self.questions = self.get_filtered_questions(10)  # Get 10 filtered questions from the API

    def get_filtered_questions(self, amount):
        url = f"https://opentdb.com/api.php?amount={amount}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            questions = []
            for result in data["results"]:
                question_text = result["question"]
                plain_text_question = self.remove_special_characters(question_text)
                if plain_text_question and self.is_fit_dimensions(plain_text_question):
                    correct_answer = result["correct_answer"]
                    answers = self.remove_special_characters_from_options([result["correct_answer"]] + result["incorrect_answers"])
                if all(answers):  # Ensure all answers are valid plain text
                    random.shuffle(answers)
                    questions.append(Question(plain_text_question, answers, answers.index(correct_answer)))

            return questions
        else:
            return []

    def remove_special_characters(self, text):
        # Replace special HTML characters with their corresponding symbols
        text = re.sub(r"&quot;", "\"", text)
        text = re.sub(r"&#039;", "'", text)
        text = re.sub(r"&ldquo;", "“", text)
        text = re.sub(r"&rdquo;", "”", text)
        text = re.sub(r"&lsquo;", "‘", text)
        text = re.sub(r"&rsquo;", "’", text)
        text = re.sub(r"&eacute;", "é", text)
        text = re.sub(r"&amp;", "&", text)
        text = re.sub(r"&uuml;", "ü", text)
        text = re.sub(r"&shy;", "", text)
        text = re.sub(r"&hellip;", "…", text)
        text = re.sub(r"&ldquo;", "“", text)
        text = re.sub(r"&rdquo;", "”", text)       
        return text

    def remove_special_characters_from_options(self, options):
        # Iterate through the options and remove special characters
        return [self.remove_special_characters(option) for option in options]

    def is_fit_dimensions(self, text):
        # Assuming the quiz window width is 600 and height is 400
        return len(text) <= 500  # Adjust the length limit as needed

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    app.center_window(root, 500, 300)  # Center the main app window
    root.mainloop()
