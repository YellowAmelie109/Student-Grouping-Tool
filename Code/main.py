import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

#=====GLOBAL CONSTANTS=====

BG_COLOUR="#FFFFFF"
HEADER_COLOUR="#FFDB32"
LARGE_FONT=("Ariel",30)

#=====ROOT WINDOW=====
#Constants for styling included within

class Window(tk.Tk):
    def __init__(self):
        #Setup window
        tk.Tk.__init__(self)
        self.state('zoomed')
        self.geometry(f"{self.winfo_screenwidth()-10}x{self.winfo_screenheight()}")
        self.title('Student Grouping Tool')
        self.config(background=BG_COLOUR)

        #=====STYLES=====

        HEADER_BUTTON_STYLE=ttk.Style()
        HEADER_BUTTON_STYLE.configure("Header.TButton",background=HEADER_COLOUR)
        
        #================
        #Dictionary that will store all loaded pages
        self.frames={}
        #Show the home page first
        self.show_frame(HomePage)

    #Method for changing currently open page
    def show_frame(self, f):
        #If the page is already loaded, show it
        if f in self.frames.keys():
            frame = self.frames[f]
        #Otherwise, load it then show it
        else:
            frame = f(self)
            self.frames[f] = frame
            frame.place(relx=0,rely=0,relwidth=1,relheight=1)
        frame.tkraise()

#=====PAGES=====

class HomePage(tk.Frame):
    def __init__(self,parent):
        tk.Frame.__init__(self, parent)
        self.label = ttk.Label(self, text="Welcome to AppName Grouping Tool!", font=LARGE_FONT)
        self.label.pack() 

        self.projectButton = ttk.Button(self,text="Choose Projects",command=lambda:parent.show_frame(ProjectPage))
        self.projectButton.pack() 

        self.studentButton = ttk.Button(self,text="Choose Students",command=lambda:parent.show_frame(StudentPage))
        self.studentButton.pack() 

        self.runButton = ttk.Button(self,text="Create Groups",command=lambda:parent.show_frame(LoadingPage),state="disabled")
        self.runButton.pack() 

        self.warning = ttk.Label(self,text="Must choose projects and students first")


    #This method runs once everytime the page is opened
    def tkraise(self):
        tk.Frame.tkraise(self)

        #If at least one student and one project has been selected, allow the run button to be clickable and remove the warning message
        if ProjectPage in self.master.frames and StudentPage in self.master.frames and self.master.frames[ProjectPage].check_for_selection() and self.master.frames[StudentPage].check_for_selection():
            self.runButton["state"]="enabled"
            self.warning.pack_forget()

        #Otherwise, disable the run button and display the warning message
        else:
            self.runButton["state"]="disabled"
            self.warning.pack() 


class ProjectPage(tk.Frame):
    def __init__(self,parent):
        tk.Frame.__init__(self,parent)

        self.header=Header(self,"Projects",HEADER_COLOUR) 
        self.header.pack(fill="x")

        self.backButton=ttk.Button(self.header,text="Back",style="Header.TButton",command=lambda:parent.show_frame(HomePage)) #Change to check where it should go back to
        self.backButton.pack(side="right")

        self.importButton=ttk.Button(self,text="Import from file",command=self.import_projects)
        self.importButton.pack()

        self.addButton=ttk.Button(self,text="New project",command=self.new_project)
        self.addButton.pack()

        #self.separator=ttk.Separator(self,orient="horizontal")
        #self.separator.pack(fill="x",expand=True)

        self.boxesFrame=ScrollableFrame(self)
        self.boxesFrame.canvas.pack(fill="both",expand=True)
        self.update()

        self.projectBoxes={}
        for i in range(10):
            name="Name"+str(i)
            self.projectBoxes[name]=projectBox(self.boxesFrame,self,name,0,0,True,["g"])
            self.projectBoxes[name].pack(fill="x",padx=10,pady=5)

    #Method override as a work-around for a scrolling bug
    def update(self):
        self.master.state('normal')
        tk.Frame.update(self)
        self.master.state('zoomed')

    #Iterates through every project, and returns true if it finds a selected project. Returns false when no project is selected.
    def check_for_selection(self):
        for box in self.projectBoxes:
            if self.projectBoxes[box].check_selection():
                return True
        return False    

    def import_projects(self):
        #Show an "Open" dialog box and return an open file object in read mode
        file = filedialog.askopenfile(mode='r',filetypes=[("Supported file types",".txt .csv")]) #Add excel
        #Validation to ensure the user selected a file
        if file == None:
            return
        
        #<<<---------------------------------------------

        file.close()
        return
        
    def new_project(self):
        
        popupWin=entryPopupWin(self,"New project")
        name=tk.StringVar()
        maxSize=tk.StringVar()
        minSize=tk.StringVar()
        optional=tk.BooleanVar()
        skills=tk.StringVar()

        popupWin.add_string_entry("Enter name:",name)

        popupWin.add_int_entry("Enter the maximum size allowed for this project's group:",maxSize)

        popupWin.add_int_entry("Enter the minimum size allowed for this project's group:",minSize)

        popupWin.add_checkbox("Is this project optional?",optional)

        popupWin.add_string_entry("Enter skills, each one separated by a comma:",skills)

        popupWin.add_save_cancel(popupWin,name,maxSize,minSize,optional,skills)

    def save_entry(self,window,*variables):
        name=variables[0].get()
        maxSize=variables[1].get()
        minSize=variables[2].get()
        optional=variables[3].get()
        skills=variables[4].get()

        #Validation to ensure all required entries are filled
        if name != "" and maxSize != "" and minSize != "" and skills != "":
            
            maxSize = int(maxSize)
            minSize = int(minSize)
            
            #Separate skills into a list and remove whitespace
            skills=skills.split(",")
            for i in range(len(skills)):
                skills[i]=skills[i].strip()

            #Display new project on the GUI
            self.projectBoxes[name]=projectBox(self.boxesFrame,self,name,maxSize,minSize,optional,skills)
            self.projectBoxes[name].pack(fill="x",padx=10,pady=5)

            #Destroy the popup window
            window.destroy()

            #Work-around for a scrollbar bug
            self.update()

    def editBox(self,boxName):
        return
    
    def deleteBox(self,boxName):
        self.projectBoxes[boxName].pack_forget()
        del self.projectBoxes[boxName]
        self.update()




class StudentPage(tk.Frame):
    def __init__(self,parent):
        tk.Frame.__init__(self, parent)

        self.header=Header(self,"Students",HEADER_COLOUR) 
        self.header.pack(fill="x")

        self.backButton=ttk.Button(self.header,text="Back",style="Header.TButton",command=lambda:parent.show_frame(HomePage)) #Change to check where it should go back to
        self.backButton.pack(side="right")

        self.importButton=ttk.Button(self,text="Import from file",command=self.import_students)
        self.importButton.pack()

        self.addButton=ttk.Button(self,text="New student",command=self.new_student)
        self.addButton.pack()

        self.boxesFrame=ScrollableFrame(self)
        self.boxesFrame.canvas.pack(fill="both",expand=True)
        self.update()

        self.studentBoxes={}
        for i in range(10):
            name="Name"+str(i)
            self.studentBoxes[name]=studentBox(self.boxesFrame,self,name,"F",["G"])
            self.studentBoxes[name].pack(fill="x",padx=10,pady=5)

    #Method override as a work-around for a scrolling bug
    def update(self):
        self.master.state('normal')
        tk.Frame.update(self)
        self.master.state('zoomed')

    def check_for_selection(self):
        for box in self.studentBoxes:
            if self.studentBoxes[box].check_selection():
                return True
        return False  
    
    def import_students(self):
        #Show an "Open" dialog box and return an open file object in read mode
        file = filedialog.askopenfile(mode='r',filetypes=[("Supported file types",".txt .csv")]) #Add excel
        #Validation to ensure the user selected a file
        if file == None:
            return
        
        #<<<---------------------------------------------

        file.close()
        return
        
    def new_student(self):
        popupWin=entryPopupWin(self,"New student")
        name=tk.StringVar()
        gender=tk.StringVar()
        skills=tk.StringVar()

        popupWin.add_string_entry("Enter name:", name)

        popupWin.add_string_entry("Enter gender:",gender)

        popupWin.add_string_entry("Enter skills, each one separated by a comma:",skills)

        popupWin.add_save_cancel(popupWin,name,gender,skills)
    
    def save_entry(self,window,*variables):
        name=variables[0].get()
        gender=variables[1].get()
        skills=variables[2].get()

        #Validation to ensure all required entries are filled
        if name != "" and gender != "" and skills != "":

            #Separate skills into a list and remove whitespace
            skills=skills.split(",")
            for i in range(len(skills)):
                skills[i]=skills[i].strip()

            #Display new student on the GUI
            self.studentBoxes[name]=studentBox(self.boxesFrame,self,name,gender,skills)
            self.studentBoxes[name].pack(fill="x",padx=10,pady=5)

            #Destroy the popup window
            window.destroy()

            #Scroll bar bug work-around
            self.update()

    def editBox(self,boxName):
        return
    
    def deleteBox(self,boxName):
        self.studentBoxes[boxName].pack_forget()
        del self.studentBoxes[boxName]
        self.update()


class LoadingPage(tk.Frame):
    def __init__(self,parent):
        tk.Frame.__init__(self, parent)

        self.label = ttk.Label(self, text="Grouping in progress...")
        self.label.pack()

        self.cancelButton=ttk.Button(self,text="Cancel",command=lambda:parent.show_frame(HomePage))
        self.cancelButton.pack()

class ResultsPage(tk.Frame):
    def __init__(self,parent):
        tk.Frame.__init__(self, parent)

        self.header=Header(self,"Results",HEADER_COLOUR) 
        self.header.pack(fill="x")

        self.homeButton=ttk.Button(self.header,text="Back",style="Header.TButton",command=lambda:parent.show_frame(HomePage))
        self.homeButton.pack(side="right")

class RegisterPage(tk.Frame):
    def __init__(self,parent):
        tk.Frame.__init__(self, parent)

        self.header=Header(self,"Register",HEADER_COLOUR) 
        self.header.pack(fill="x")

        self.homeButton=ttk.Button(self.header,text="Back",style="Header.TButton",command=lambda:parent.show_frame(HomePage))
        self.homeButton.pack(side="right")

#=====WIDGETS=====

class Header(tk.Frame):
    def __init__(self,parent,text,colour):
        tk.Frame.__init__(self,parent)
        self.config(bg=colour)
        self.label = tk.Label(self, text=text, bg=colour,font=LARGE_FONT) #change to ttk
        self.label.pack(side="left")

class ScrollableFrame(tk.Frame):
    def __init__(self,parent):
        self.canvas=tk.Canvas(parent,background="white")
        tk.Frame.__init__(self,self.canvas)

        self.scrollbar=tk.Scrollbar(self.canvas,orient="vertical",command=self.canvas.yview)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right",fill="y")
        self.scrollbar.update()

        self.canvas.create_window((0,0),window=self,anchor='nw',width=self.winfo_screenwidth()-self.scrollbar.winfo_width())
        self.canvas.bind("<Configure>",self.scroll)
        #self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    #def _on_mousewheel(self, event):
        #self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    def scroll(self,event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"),width=self.winfo_width(),height=self.winfo_height())

#Has checkbox, name, edit button, delete button.
class selectionBox(tk.Frame):
    def __init__(self,parent,page,name):
        tk.Frame.__init__(self,parent,relief="solid",bd=2)

        self.name=name
        self.page=page

        self.selected=tk.BooleanVar(value=False)
        self.checkbox=ttk.Checkbutton(self,variable=self.selected,name=name.lower(),onvalue=True,offvalue=False)
        self.checkbox.pack()

        self.nameLabel=ttk.Label(self,text=name)
        self.nameLabel.pack()

        self.editButton=ttk.Button(self,text="Edit",command=self.edit)
        self.editButton.pack()

        self.deleteButton=ttk.Button(self,text="Delete",command=self.delete)
        self.deleteButton.pack()

    def check_selection(self):
        return self.selected.get()

    def edit(self):
        self.page.editBox(self.name)
    
    def delete(self):
        delChoice=messagebox.askyesno(title="Delete entry", message=f"Are you sure you want to delete {self.name}?")
        if delChoice:
            self.selected.set(False)
            self.page.deleteBox(self.name)
        

class projectBox(selectionBox):
    def __init__(self,parent,page,name,maxSize,minSize,optional,skills):
        selectionBox.__init__(self,parent,page,name)

        self.maxSize=ttk.Label(self,text=f"Max group size: {maxSize}")
        self.maxSize.pack()

        self.minSize=ttk.Label(self,text=f"Min group size: {minSize}")
        self.minSize.pack()

        self.optional=ttk.Label(self,text=f"Optional: {optional}")
        self.optional.pack()

        self.skills=ttk.Label(self,text=f"Skills: {", ".join(skills)}")
        self.skills.pack()

class studentBox(selectionBox):
    def __init__(self, parent, page, name, gender, skills):
        selectionBox.__init__(self,parent,page,name)

        self.gender = ttk.Label(self,text=f"Gender: {gender}")
        self.gender.pack()

        self.skills = ttk.Label(self, text= f"Skills: {", ".join(skills)}")
        self.skills.pack()


class entryPopupWin(tk.Toplevel):
    def __init__(self,parent,title):
        tk.Toplevel.__init__(self,parent)
        self.title(title)
    
    def add_string_entry(self,text,variable):
        ttk.Label(self, text=text).pack()
        ttk.Entry(self, textvariable=variable).pack()

    def add_int_entry(self,text,variable):

        #Prevents user from typing non numbers into number-only entry boxes
        def intCallback(P):
            return str.isdigit(P) or P == ""
        
        intValidate = (self.register(intCallback), '%P')
        
        ttk.Label(self, text=text).pack()
        ttk.Entry(self, textvariable=variable,validate="all",validatecommand=intValidate).pack()
    
    def add_checkbox(self,text,variable):
        ttk.Label(self, text=text).pack()
        ttk.Checkbutton(self, variable=variable, onvalue=True, offvalue=False).pack()
    
    def add_save_cancel(self,window,*variables):
        ttk.Button(self, text="Save", command=lambda:self.master.save_entry(window,*variables)).pack()
        ttk.Button(self, text="Cancel", command=self.destroy).pack()

    

#=====MAIN=====

app=Window()
app.mainloop()