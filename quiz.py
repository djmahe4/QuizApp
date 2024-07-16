import time
import tkinter as tk
import random
from tkinter import messagebox,simpledialog,Button,Text
import google.generativeai as genai
from dotenv import load_dotenv, find_dotenv
import os
import re
from time import sleep
from pylatexenc.latex2text import LatexNodes2Text


def latex_to_unicode(latex_str):
    return LatexNodes2Text().latex_to_text(latex_str)

def init():
    # Find or create .env file
    env_path = find_dotenv()
    if env_path == "":
        with open('.env', 'w') as f:
            pass
    env_path = find_dotenv()

    # Load existing .env file or create one if it doesn't exist
    load_dotenv(find_dotenv(), override=True)

    # Check if API key is in environment variables
    api_key = os.getenv('GENERATIVE_AI_KEY')
    if api_key is None:
        # If API key is not set, ask the user for it
        api_key = input('Please enter your API key from https://ai.google.dev: ')
        # Store the API key in the .env file
        with open(find_dotenv(), 'a') as f:
            f.write(f'GENERATIVE_AI_KEY={api_key}\n')
        print("API key stored successfully!")

    load_dotenv()
    genai.configure(api_key=os.environ["GENERATIVE_AI_KEY"])

    generation_config = {
        "temperature": 0.7,
        "top_p": 1,
        "top_k": 0,
        "response_mime_type": "text/plain"
    }

    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        }
    ]

    model = genai.GenerativeModel(
        model_name="gemini-1.0-pro",
        safety_settings=safety_settings,
        generation_config=generation_config
    )

    chat_session = model.start_chat(history=[])
    return chat_session

def generate_questions(query,chat_session):
    # This function will communicate with Gemini AI to get the output
    # Replace with actual Gemini AI API calls
    try:
        while True:
            response = chat_session.send_message(query)
            #response=latex_to_unicode(response.text)
            # Extract the question and answer from the generated text
            question_answer = response.text.replace("*","").replace("**","")
            #question_answer = response.replace("*", "").replace("**", "")
            print(question_answer)

            # Define a pattern to extract the question, options, and answer
            #pattern = r"\d+\.(.*?)\n\((a)\)(.*?)\n\((b)\)(.*?)\n\((c)\)(.*?)\n\((d)\)(.*?)\n\n\*\*AnswerKey:\*\*\n(\d+)\.\((.)\)"

            # Find all matches in the input text
            #matches = re.findall(pattern, question_answer, re.DOTALL)
            matches=question_answer.split("\n")

            # Create a list of dictionaries, each containing question, options, and answer
            questions_list = []

            diction={
                'question':"",
                'options':['','','','']
            }
            questions_list.append(diction)
            for match in matches:
                if match==" " or match=="" :#or "answer" in match.lower():
                    continue
                if 'answer' in match.lower():
                    match2 = re.search(r"\((.)\)", match)
                    if match2:
                        extracted_character = match.group(1)
                        diction.update({"answer": extracted_character})
                #if type(match[0])==int:
                try:
                    if int(match[0]) and len(match)>10:
                        diction["question"]=match[3:]
                        print(match[3:])
                except ValueError:
                    pass
                if diction["question"]=="" and match.endswith("?"):
                    diction["question"]=match
                if match[1]=='a':
                    diction['options'][0]=match
                if match[1]=='b':
                    diction['options'][1]=match
                if match[1]=='c':
                    diction['options'][2]=match
                if match[1]=='d':
                    diction['options'][3] = match
                    diction = {
                        'question': "",
                        'options': ['','','','']
                    }
                    questions_list.append(diction)
                qmatch = re.match(r"(\d+)\.\s*\((\w)\)", match)
                if qmatch:
                    question_number, answer = qmatch.groups()
                    question_number=int(question_number)
                    print(f"Question {question_number}: Answer = {answer}")
                    # options=questions_list[question_number]["options"]
                    diction=questions_list[question_number-1]
                    diction.update({"answer": answer})
                    questions_list[question_number-1]=diction
                #else:
                    #diction["question"]+=match
            break
    #except questions_list==[]:
    except UnboundLocalError:
        sleep(10)
        print("retrying..")

    # Print the list of dictionaries
    print(questions_list)
    #else:
    #return response.text.replace("*","")
    return questions_list


class TestPQRSApp:
    def __init__(self, rt):
        #super().__init__(rt)
        self.root = rt
        self.root.title("Quiz App")
        self.output_text = tk.Text(self.root, height=20, width=80)
        self.output_text.pack()
        self.setup_test_ui()
        # Create a close button
        #self.close_button = Button(self.test_window, text="Close", command=self.close_app)
        #self.close_button.pack()

    def setup_test_ui(self):
        self.test_window = tk.Toplevel(self.root)
        self.test_window.title("Test Your Knowledge")
        self.topic_entry = tk.Entry(self.root)
        self.question_label = tk.Label(self.test_window, text="")
        self.question_label.pack()
        self.option_buttons = []
        for i in range(4):
            button = tk.Button(self.test_window, text="", command=lambda idx=i: self.check_answer(idx))
            button.pack()
            self.option_buttons.append(button)
        self.score_label = tk.Label(self.test_window, text="Score: 0")
        self.score_label.pack()


    def test(self):
        topic = simpledialog.askstring("Enter Topic", "Please enter a topic for the quiz:")
        if topic:
            self.questions = generate_questions(f"Formulate mcq quiz on {topic} with answers",chat)
            #random.shuffle(self.questions)  # Shuffle the questions
            self.score = 0
            self.current_question_index = 0
            self.load_next_question()
        else:
            self.output_text.insert(tk.END, "No topic entered. Canceling test.\n")

    def load_next_question(self):
        if self.questions[self.current_question_index]["question"] == "":
            self.test_window.destroy()
            self.test()
        if self.current_question_index < len(self.questions) or self.questions[self.current_question_index][
            "answer"] != "":
            question_data = self.questions[self.current_question_index]
            question = question_data["question"]
            options = question_data["options"]
            self.question_label.config(text=question)
            #random.shuffle(options)  # Shuffle the options
            for i in range(4):
                self.option_buttons[i].config(text=options[i])
        else:
            self.finish_test()

    def check_answer(self, selected_index):
        #correct_answer = self.questions[self.current_question_index]["options"][0]  # First option is correct
        correct_answer = self.questions[self.current_question_index]["answer"]
        check={'a':0,'b':1,'c':2,'d':3}
        ca=self.questions[self.current_question_index]["options"][check[correct_answer]]
        user_answer = self.option_buttons[selected_index].cget("text")
        if user_answer == ca:
            self.score += 1
        self.current_question_index += 1
        self.score_label.config(text=f"Score: {self.score}")
        self.load_next_question()



    def finish_test(self):
        messagebox.showinfo("Test Completed", f"Your final score is: {self.score}")
        self.test_window.destroy()
        self.cont=tk.Tk()
        result = messagebox.askyesnocancel("Confirmation", "Do you want to continue?")
        if not result:
            self.cont.destroy()
            root.destroy()

if __name__ == "__main__":
    chat=init()
    root = tk.Tk()
    app = TestPQRSApp(root)
    app.test()
    root.mainloop()
    #print(generate_questions("Formulate mcq quiz on linux bash with answers"))
