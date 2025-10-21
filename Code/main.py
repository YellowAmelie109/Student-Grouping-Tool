import tkinter as tk
from tkinter import ttk

#Globals

BG_COLOUR="#FFFFFF"
HEADER_COLOUR="#FFDB32"

#Root window

class Window(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.geometry("1100x700")
        #self.resizable(0, 0)
        self.title('Student Grouping Tool')
        self.config(background=BG_COLOUR)

        self.container = tk.Frame(self)
        self.container.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.frames={}
        for f in (HomePage,ProjectPage,StudentPage,LoadingPage, ResultsPage, RegisterPage):
            frame = f(self.container,self)
            self.frames[f] = frame
            frame.place(relx=0,rely=0,relwidth=1,relheight=1)

        self.show_frame(HomePage)

    def show_frame(self, f):
        frame = self.frames[f]
        frame.tkraise()

#Pages

class HomePage(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self, parent)

        self.label = ttk.Label(self, text="Welcome to AppName Grouping Tool!", font=("Ariel",30))
        self.label.pack() #Place

        self.projectButton = ttk.Button(self,text="Choose Projects",command=lambda:controller.show_frame(ProjectPage))
        self.projectButton.pack() #Place

        self.studentButton = ttk.Button(self,text="Choose Students",command=lambda:controller.show_frame(StudentPage))
        self.studentButton.pack() #Place

        self.runButton = ttk.Button(self,text="Create Groups",command=lambda:controller.show_frame(LoadingPage),state="disabled")
        self.runButton.pack() #Place

        self.warning = ttk.Label(self,text="Must choose projects and students first")

    def tkraise(self):
        tk.Frame.tkraise(self)
        if True:
            self.runButton["state"]="enabled"
            self.warning.pack_forget()
        else:
            self.warning.pack() #Place


class ProjectPage(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.header=Header(self,"Projects",HEADER_COLOUR) 
        self.header.place(relx=0, rely=0, relwidth=1,relheight=0.1)
        self.backButton=ttk.Button(self,text="Back",command=lambda:controller.show_frame(HomePage)) #Change to check where it should go back to
        self.backButton.pack()


class StudentPage(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self, parent)
        self.header=Header(self,"Students",HEADER_COLOUR) 
        self.header.place(relx=0, rely=0, relwidth=1,relheight=0.1)

class LoadingPage(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self, parent)
        self.label = ttk.Label(self, text="Groouping in progress...")

class ResultsPage(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self, parent)
        self.header=Header(self,"Students",HEADER_COLOUR) 
        self.header.place(relx=0, rely=0, relwidth=1,relheight=0.1)

class RegisterPage(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self, parent)
        self.header=Header(self,"Students",HEADER_COLOUR) 
        self.header.place(relx=0, rely=0, relwidth=1,relheight=0.1)

#Custom widgets

class Header(tk.Frame):
    def __init__(self,parent,text,colour,buttons=[]):
        tk.Frame.__init__(self,parent)
        self.config(bg=colour)
        self.label = tk.Label(self, text=text, bg=colour,font=("Ariel", 20))
        self.label.place(relx=0,rely=0) #change


app=Window()
app.mainloop()