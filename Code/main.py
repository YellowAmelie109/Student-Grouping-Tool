import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3 as sql
import csv
import re
import geneticAlgo as ga
#from algoClasses import Student, Project, Individual

#=====GLOBAL CONSTANTS=====

BG_COLOUR="#FFFFFF"
HEADER_COLOUR="#FFDB32"
PASTEL_COLOURS=("#FFBABB","#FFDFBA","#FFFFBA","#BAFFC9","#BAE1FF","#FFBAFF")
LARGE_FONT=("Arial",30)
DATABASE = "Code/database.db"
#SQLFILEHEADER="SQLite format 3"

#=====ROOT WINDOW=====
#Constants for styling included within

class Window(tk.Tk):
    def __init__(self):
        #Set up window
        tk.Tk.__init__(self)

        self.state('zoomed')
        self.geometry(f"{self.winfo_screenwidth()-10}x{self.winfo_screenheight()}")
        self.title('Student Grouping Tool')
        self.config(background=BG_COLOUR)

        #=====STYLES=====

        HEADER_BUTTON_STYLE=ttk.Style()
        HEADER_BUTTON_STYLE.configure("Header.TButton",background=HEADER_COLOUR)
        
        #================
        #Dictionary that stores all loaded pages
        self.frames={}
        #Load the homepage first
        self.show_frame(HomePage)

    #Method for changing currently open page
    def show_frame(self, f,*args,**kwargs):
        #If the page is already loaded, show it
        if f in self.frames.keys():
            frame = self.frames[f]
        #Otherwise, load it then show it
        else:
            frame = f(self)
            self.frames[f] = frame
            frame.place(relx=0,rely=0,relwidth=1,relheight=1)
        frame.tkraise(*args,**kwargs)

#=====PAGES=====

class HomePage(tk.Frame):
    def __init__(self,parent):
        #Set up home page layout
        tk.Frame.__init__(self, parent)

        self.settingsButton = ttk.Button(self,text="Settings",command=lambda:parent.show_frame(SettingsPage))
        self.settingsButton.pack()

        self.label = ttk.Label(self, text="Welcome to the Student Grouping Tool!", font=LARGE_FONT)
        self.label.pack()

        self.projectButton = ttk.Button(self,text="Choose Projects",command=lambda:parent.show_frame(ProjectPage))
        self.projectButton.pack() 

        self.studentButton = ttk.Button(self,text="Choose Students",command=lambda:parent.show_frame(StudentPage))
        self.studentButton.pack() 

        self.runButton = ttk.Button(self,text="Create Groups",command=self.get_data_for_algo,state="disabled")
        self.runButton.pack() 

        self.warning = ttk.Label(self,text="Must choose projects and students first")


    #Method override that runs once everytime the page is opened
    def tkraise(self,*args,**kwargs):
        tk.Frame.tkraise(self)

        #If at least one student and one project has been selected, allow the run button to be clickable and remove the warning message
        if ProjectPage in self.master.frames and StudentPage in self.master.frames and self.master.frames[ProjectPage].check_for_selection() and self.master.frames[StudentPage].check_for_selection():
            self.runButton["state"]="enabled"
            self.warning.pack_forget()

        #Otherwise, disable the run button and display the warning message
        else:
            self.runButton["state"]="disabled"
            self.warning.pack() 

    def get_data_for_algo(self,*args,**kwargs):
        database=DATABASE
        projects=self.master.frames[ProjectPage].get_selected()
        students=self.master.frames[StudentPage].get_selected()
        settings=self.master.frames[SettingsPage].get_settings()
        fitness=settings["fitness"]
        iterations=settings["iterations"]
        popSize=settings["popSize"]
        
        self.master.show_frame(LoadingPage,database,students,projects,fitness,iterations,popSize)





class ProjectPage(tk.Frame):
    def __init__(self,parent):
        #Set up the project page layout
        tk.Frame.__init__(self,parent)

        self.header=Header(self,"Projects",HEADER_COLOUR) 
        self.header.pack(fill="x")

        self.backButton=ttk.Button(self.header,text="Back",style="Header.TButton",command=lambda:parent.show_frame(HomePage))
        self.backButton.pack(side="right")

        self.importButton=ttk.Button(self,text="Import from file",command=self.import_projects)
        self.importButton.pack()

        self.addButton=ttk.Button(self,text="New project",command=lambda:self.create_entry_window("New"))
        self.addButton.pack()

        #self.separator=ttk.Separator(self,orient="horizontal")
        #self.separator.pack(fill="x",expand=True)

        self.boxesFrame=ScrollableFrame(self)
        self.boxesFrame.canvas.pack(fill="both",expand=True)
        self.update()

        #Get and show project data from the database
        self.projectBoxes={}
        self.fetch_from_db(DATABASE)


    def fetch_from_db(self,path):
        #Fetch all project data from a database
        query="SELECT * from Projects LEFT JOIN ProjectSkills using (ProjectID)"
        with sql.connect(path) as conn:
            cur = conn.cursor()
            cur.execute(query)
            projects=cur.fetchall()

            for project in projects:
                ID=project[0]
                #When a project has multiple skills, the ID is repeated in the recieved tuple for each skill
                if ID in self.projectBoxes:
                    #The next skill is appended to the existing list of skills for this ID
                    data=self.projectBoxes[ID].get_data()
                    
                    skills=data["skills"]
                    skills.append(project[5])
                    self.projectBoxes[ID].edit_data(skills=skills)

                #If the project has not been added to the dictionary yet, add it
                else:
                    #Unpack the data, keeping data that should not be of type string spearate
                    *data,optional,skills=project
                    #Convert to correct data type
                    optional=bool(optional)
                    skills=[skills]
                    #Store data and display data on UI
                    self.projectBoxes[ID]=projectBox(self.boxesFrame,self,*data,optional,skills)
                    self.projectBoxes[ID].pack()


    #Method override as a work-around for a scrolling bug
    def update(self):
        self.master.state('normal')
        tk.Frame.update(self)
        self.master.state('zoomed')

    #Iterates through each project, returning true as soon as it finds a selected project. Returns false when no project is selected.
    def check_for_selection(self):
        for box in self.projectBoxes:
            if self.projectBoxes[box].check_selection():
                return True
        return False   

    def get_selected(self):
        sel=set()
        for box in self.projectBoxes:
            if self.projectBoxes[box].check_selection():
                sel.add(box)
        return sel

        
    def create_entry_window(self,mode,**kwargs):
        name=tk.StringVar()
        maxSize=tk.StringVar()
        minSize=tk.StringVar()
        optional=tk.BooleanVar()
        skills=tk.StringVar()
        data={"name":name,"maxSize":maxSize,"minSize":minSize,"optional":optional,"skills":skills}

        if mode == "Edit":
            popupWin=entryPopupWin(self,"Edit Project")
            name.set(kwargs["name"])
            maxSize.set(kwargs["maxSize"])
            minSize.set(kwargs["minSize"])
            optional.set(kwargs["optional"])
            skills.set(", ".join(kwargs["skills"]))
            data["ID"]=kwargs["ID"]
        else: 
            popupWin=entryPopupWin(self,"New project")

        popupWin.grab_set()
        popupWin.add_string_entry("Name:",name)

        popupWin.add_int_entry("Maximum size allowed for this project's group:",maxSize)

        popupWin.add_int_entry("Minimum size allowed for this project's group:",minSize)

        popupWin.add_checkbox("Optional:",optional)

        popupWin.add_string_entry("Skills, each one separated by a comma:",skills)

        popupWin.add_save_cancel(popupWin,mode,**data)

    def validate_entry(self,name,maxSize,minSize,optional,skills):
        if name != "" and maxSize != "" and minSize != "" and optional != "" and skills != "":
            try:
                maxSize = int(maxSize)
                minSize = int(minSize)
            except:
                return {"valid":False,"reason":"Minimum group size and maximum group size must be integers"}
            else:
                if minSize>0:
                    if maxSize>=minSize:
                        return {"valid":True}
                    else:
                        return {"valid":False,"reason":"Maximum group size must be greater than or equal to minimum group size."}
                else:
                    return {"valid":False,"reason":"Minimum group size must be greater than 0."}
        else:
            return {"valid":False,"reason":"All entries must be filled."}

    def save_entry(self,window,mode,**kwargs):
        name=kwargs["name"].get()
        maxSize=kwargs["maxSize"].get()
        minSize=kwargs["minSize"].get()
        optional=kwargs["optional"].get()
        skills=kwargs["skills"].get()

        valid=self.validate_entry(name,maxSize,minSize,optional,skills)
        if valid["valid"]:
            #Separate skills into a list, remove whitespace, and add to a set to remove duplicates
            skillList=skills.split(",")
            skills=set()
            for i in range(len(skillList)):
                skills.add(skillList[i].strip())

            if mode == "Edit":
                self.edit_project(kwargs["ID"],name,maxSize,minSize,optional,skills)
            else:
                self.new_project(name,maxSize,minSize,optional,skills)

            #Destroy the popup window
            window.destroy()

        else:
            messagebox.showerror(title="Error",message=valid["reason"])

    
    def import_projects(self):


        def importtxt(path):
            file=open(path,mode="r")
            file.close()


        def importcsv(path):
            file=open(path,newline='')
            reader=csv.reader(file)
            isRow1=True
            for row in reader:
                if isRow1 and not row==["name, maxSize, minSize, optional, skills"]:
                    messagebox.showerror(title="Import Error",message="CSV File not in correct format.")
                    break
                isRow1=False

                valid=self.validate_entry(*row)
                if valid["valid"]:
                    #Separate skills into a list, remove whitespace, and add to a set to remove duplicates
                    skillList=row[4].split(",")
                    skills=set()
                    for i in range(len(skillList)):
                        skills.add(skillList[i].strip())
                        
                    self.new_project(row[0],row[1],row[2],row[3],skills)
                else:
                    messagebox.showerror(title="Import Error",message=f"Import failed. {valid["reason"]}")


        def importdb(path):
            return
        

        #Show an "Open" dialog box and return file directory
        path = filedialog.askopenfilename()
        #Validation to ensure the user selected a valid file type
        if path != None:
            match path[-4:]:
                #case ".txt":
                    #importtxt(path)
                case ".csv":
                    importcsv(path)
                case _:
                    #if checkForDB(path):
                        #importdb(path)
                    #else:
                    messagebox.showerror(title="Import Error", message="File type unrecognised!")

        else:
            messagebox.showerror(title="Import Error", message="No file selected!")



    #Add the inputted data to the Project and Project Skills tables in the database
    def new_project(self,name,maxSize,minSize,optional,skills):
        mainquery="INSERT INTO Projects (Name, MaxSize, MinSize, Optional) VALUES (?,?,?,?)"
        skillsquery="INSERT INTO ProjectSkills (ProjectID, Skill) VALUES (?,?)"
        with sql.connect(DATABASE) as conn:
            cur = conn.cursor()

            cur.execute(mainquery,(name,maxSize,minSize,optional))

            #Fetch the autogenerated ID for this student
            ID=cur.lastrowid 

            for skill in skills:
                cur.execute(skillsquery,(ID, skill))

            conn.commit()

        #Display new project on the GUI
        self.projectBoxes[ID]=projectBox(self.boxesFrame,self,ID,name,maxSize,minSize,optional,skills)
        self.projectBoxes[ID].pack()

        #Work-around for a scrollbar bug
        self.update()
        
    def edit_project(self,ID,name,maxSize,minSize,optional,skills):
        edited=False
        box=self.projectBoxes[ID]
        oldData=box.get_data()

        #Only updates if the new data is different from the old data
        with sql.connect(DATABASE) as conn:
            cur = conn.cursor()

            if name != oldData["name"]:
                edited=True

                query = "UPDATE Projects SET Name = ? WHERE ProjectID = ?"
                cur.execute(query,(name,ID))

                box.edit_data(name=name)

            if maxSize != oldData["maxSize"]:
                edited=True

                query="UPDATE Projects SET MaxSize = ? WHERE ProjectID = ?"
                cur.execute(query,(maxSize,ID))

                box.edit_data(maxSize=maxSize)

            if minSize != oldData["minSize"]:
                edited=True

                query="UPDATE Projects SET MinSize = ? WHERE ProjectID = ?"
                cur.execute(query,(minSize,ID))

                box.edit_data(minSize=minSize)

            if optional != oldData["optional"]:
                edited=True

                query="UPDATE Projects SET Optional = ? WHERE ProjectID = ?"
                cur.execute(query,(optional,ID))

                box.edit_data(optional=optional)

            if skills != oldData["skills"]:
                edited=True
                
                cur.execute("DELETE FROM ProjectSkills WHERE ProjectID = ?",(ID,))
                query = "INSERT INTO ProjectSkills (ProjectID, Skill) VALUES (?,?)"
                for skill in skills:
                    cur.execute(query,(ID,skill))

                box.edit_data(skills=skills)
                    
            if edited:
                self.update()
                conn.commit()

    def editBox(self,boxID):
        box=self.projectBoxes[boxID]
        data=box.get_data()
        self.create_entry_window("Edit",ID=data["ID"],name=data["name"], maxSize=data["maxSize"],minSize=data["minSize"], optional=data["optional"], skills=data["skills"])
    
    def deleteBox(self,boxID):
        #Delete from database
        query1 = "DELETE FROM Projects WHERE ProjectID=?"
        query2 = "DELETE FROM ProjectSkills WHERE ProjectID=?"
        with sql.connect(DATABASE) as conn:
            cur = conn.cursor()
            cur.execute(query1,(boxID,))
            cur.execute(query2,(boxID,))
            conn.commit()
        #Delete from UI
        self.projectBoxes[boxID].pack_forget()
        #Delete from internal store
        del self.projectBoxes[boxID]

        self.update()



class StudentPage(tk.Frame):
    def __init__(self,parent):
        #Set up student page layout
        tk.Frame.__init__(self, parent)

        self.header=Header(self,"Students",HEADER_COLOUR) 
        self.header.pack(fill="x")

        self.backButton=ttk.Button(self.header,text="Back",style="Header.TButton",command=lambda:parent.show_frame(HomePage))
        self.backButton.pack(side="right")

        self.importButton=ttk.Button(self,text="Import from file",command=self.import_students)
        self.importButton.pack()

        self.addButton=ttk.Button(self,text="New student",command=lambda:self.create_entry_window("New"))
        self.addButton.pack()

        self.boxesFrame=ScrollableFrame(self)
        self.boxesFrame.canvas.pack(fill="both",expand=True)
        self.update()

        self.studentBoxes={}

        #Fetch all student data from the database
        studentquery="SELECT * from Students LEFT JOIN StudentSkills using (StudentID)"
        with sql.connect(DATABASE) as conn:
            cur = conn.cursor()
            cur.execute(studentquery)
            students=cur.fetchall()
        
            for student in students:
                ID=student[0]
                #When a student has multiple skills, the ID is repeated in the recieved tuple for each skill
                if ID in self.studentBoxes:
                    #The next skill is appended to the existing list of skills for this ID
                    data=self.studentBoxes[ID].get_data()
                    skills=data["skills"]
                    skills.append(student[3])
                    self.studentBoxes[ID].edit_data(skills=skills)
                #If the student has not been added to the dictionary yet, add it
                else:
                    #Unpack the data, keeping data that should not be of type string spearate
                    *data,skills=student
                    #Convert to correct data type
                    skills=[skills]
                    #Store data and display on UI
                    self.studentBoxes[ID]=studentBox(self.boxesFrame,self,*data,skills)
                    self.studentBoxes[ID].pack()

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
    
    def get_selected(self):
        sel=set()
        for box in self.studentBoxes:
            if self.studentBoxes[box].check_selection():
                sel.add(box)
        return sel 
    
    def validate_entry(self,name,gender,skills):
        if name != "" and gender != "" and skills != "":
            return {"valid":True}
        else:
            return {"valid":False,"reason":"All entries must be filled."}
        

    def import_students(self):

        def importcsv(path):
            file=open(path,newline='')
            reader=csv.reader(file)
            isRow1=True
            for row in reader:
                if isRow1 and not row==["name, gender, skills"]:
                    messagebox.showerror(title="Import Error",message="CSV File not in correct format.")
                    break
                isRow1=False

                valid=self.validate_entry(*row)
                if valid["valid"]:
                    #Separate skills into a list, remove whitespace, and add to a set to remove duplicates
                    skillList=row[2].split(",")
                    skills=set()
                    for i in range(len(skillList)):
                        skills.add(skillList[i].strip())
                        
                    self.new_project(row[0],row[1],skills)
                else:
                    messagebox.showerror(title="Import Error",message=f"Import failed. {valid["reason"]}")


        #Show an "Open" dialog box and return an open file object in read mode
        path = filedialog.askopenfilename()
        #Validation to ensure the user selected a valid file type
        if path != None:
            match path[-4:]:
                #case ".txt":
                    #importtxt(path)
                case ".csv":
                    importcsv(path)
                case _:
                    #if checkForDB(path):
                        #importdb(path)
                    #else:
                    messagebox.showerror(title="Import Error", message="File type unrecognised!")

        else:
            messagebox.showerror(title="Import Error", message="No file selected!")
        
    def create_entry_window(self,mode,**kwargs):
        name=tk.StringVar()
        gender=tk.StringVar()
        skills=tk.StringVar()
        data={"name":name,"gender":gender,"skills":skills}

        if mode == "Edit":
            popupWin=entryPopupWin(self, "Edit student")
            name.set(kwargs["name"])
            gender.set(kwargs["gender"])
            skills.set(", ".join(kwargs["skills"]))
            data["ID"]=kwargs["ID"]
        else:
            popupWin=entryPopupWin(self,"New student")

        popupWin.grab_set()
        
        popupWin.add_string_entry("Name:", name)

        popupWin.add_string_entry("Gender:",gender)

        popupWin.add_string_entry("Skills, each one separated by a comma:",skills)

        popupWin.add_save_cancel(popupWin,mode,**data)
    
    def save_entry(self,window,mode,**kwargs):
        name=kwargs["name"].get()
        gender=kwargs["gender"].get()
        skills=kwargs["skills"].get()

        #Validation to ensure all entries meet standards
        valid=self.validate_entry(name,gender,skills)
        if valid["valid"]:
            #Separate skills into a list, remove whitespace, add to set to remove duplicates
            skillList=skills.split(",")
            skills=set()
            for i in range(len(skillList)):
                skills.add(skillList[i].strip())

            if mode == "Edit":
                self.edit_student(kwargs["ID"],name,gender,skills)
            else:
                self.new_student(name,gender,skills)
            
            #Destroy the popup window
            window.destroy()
        else:
            messagebox.showerror(title="Error",message=valid["reason"])


    #Add the inputted data to the Student and StudentSkills tables in the database
    def new_student(self,name,gender,skills):
        mainquery="INSERT INTO Students (Name, Gender) VALUES (?,?)"
        skillsquery="INSERT INTO StudentSkills (StudentID, Skill) VALUES (?,?)"
        with sql.connect(DATABASE) as conn:
            cur = conn.cursor()

            cur.execute(mainquery,(name,gender))

            #Fetch the autogenerated ID for this student
            ID=cur.lastrowid 

            for skill in skills:
                cur.execute(skillsquery,(ID, skill))

            conn.commit()

        #Display new student on the GUI
        self.studentBoxes[ID]=studentBox(self.boxesFrame,self,ID,name,gender,skills)
        self.studentBoxes[ID].pack()

        #Scroll bar bug work-around
        self.update()


    def edit_student(self,ID,name,gender,skills):
        edited=False

        box=self.studentBoxes[ID]
        oldData=box.get_data()

        #Only updates if the new data is different from the old data
        with sql.connect(DATABASE) as conn:
            cur = conn.cursor()

            if name != oldData["name"]:
                edited=True

                query = "UPDATE Students SET Name = ? WHERE StudentID = ?"
                cur.execute(query,(name,ID))

                box.edit_data(name=name)

            if gender != oldData["gender"]:
                edited=True

                query="UPDATE Students SET Gender = ? WHERE StudentID = ?"
                cur.execute(query,(gender,ID))

                box.edit_data(gender=gender)

            if skills != oldData["skills"]:
                edited=True
                
                cur.execute("DELETE FROM StudentSkills WHERE StudentID = ?",(ID,))
                query = "INSERT INTO StudentSkills (StudentID, Skill) VALUES (?,?)"
                for skill in skills:
                    cur.execute(query,(ID,skill))

                box.edit_data(skills=skills)
                    
            if edited:
                self.update()
                conn.commit()

    def editBox(self,boxID):
        box=self.studentBoxes[boxID]
        data=box.get_data()
        self.create_entry_window("Edit", ID=data["ID"],name=data["name"],gender=data["gender"],skills=data["skills"])
    
    def deleteBox(self,boxID):
        #Delete from database
        query1 = "DELETE FROM Students WHERE StudentID=?"
        query2 = "DELETE FROM StudentSkills WHERE StudentID=?"
        with sql.connect(DATABASE) as conn:
            cur = conn.cursor()
            cur.execute(query1,(boxID,))
            cur.execute(query2,(boxID,))
            conn.commit()
        #Delete from UI
        self.studentBoxes[boxID].pack_forget()
        #Delete from internal store
        del self.studentBoxes[boxID]

        self.update()



class LoadingPage(tk.Frame):
    def __init__(self,parent):
        #Set up loading page layout
        tk.Frame.__init__(self, parent)

        self.label = ttk.Label(self, text="Grouping in progress...")
        self.label.pack()

        self.cancelButton=ttk.Button(self,text="Cancel",command=lambda:parent.show_frame(HomePage))
        self.cancelButton.pack()

    #Method override that runs once everytime the page is opened
    def tkraise(self, database, studentIDs, projectIDs, tgtFit, maxIters, popSize,*args,**kwargs):
        tk.Frame.tkraise(self)
        results=ga.run(database,studentIDs,projectIDs,tgtFit,maxIters,popSize)
        if results["status"]==-1:
            messagebox.showerror("Error",results["error"])
        elif results["status"]==0:
            results=results["results"]
            self.master.show_frame(ResultsPage,results)
        else:
            messagebox.showerror("Error","An unknown eror occured")


class ResultsPage(tk.Frame):
    def __init__(self,parent):
        #Set up results page layout
        tk.Frame.__init__(self, parent)

        self.results=None
        self.resultBoxes={}

        self.header=Header(self,"Results",HEADER_COLOUR) 
        self.header.pack(fill="x")

        self.homeButton=ttk.Button(self.header,text="Back",style="Header.TButton",command=lambda:parent.show_frame(HomePage))
        self.homeButton.pack(side="right")

        self.registerButton=ttk.Button(self.header,text="Switch to register layout",style="Header.TButton",command=lambda:parent.show_frame(RegisterPage,self.results))
        self.registerButton.pack(side="right")

        #Allows scrolling through the boxes
        self.boxesFrame=ScrollableFrame(self)
        self.boxesFrame.canvas.pack(fill="both",expand=True)
        self.update()

    def tkraise(self,results,*args,**kwargs):
        tk.Frame.tkraise(self)
        
        while len(self.resultBoxes)>0:
            ID=next(iter(self.resultBoxes))
            self.resultBoxes[ID].pack_forget()
            del self.resultBoxes[ID]

        self.results=results
        #Stores the boxes shown in the scrollable frame
        self.resultBoxes={}

        #Create the boxes and display project data in them
        for projectID in results:
            result=results[projectID]
            self.resultBoxes[projectID]=resultBox(self.boxesFrame,self,projectID,result["name"],result["students"],result["size"],result["genders"],result["skills"])
            self.resultBoxes[projectID].pack()

        self.update()

    #Method override as a work-around for a scrolling bug
    def update(self):
        self.master.state('normal')
        tk.Frame.update(self)
        self.master.state('zoomed')
        

class RegisterPage(tk.Frame):
    def __init__(self,parent):
        #Set up register page layout
        tk.Frame.__init__(self, parent)
        self.columnconfigure(0,weight=1)
        self.columnconfigure(1,weight=1)
        self.columnconfigure(2,weight=2)

        self.results=None
        self.registerBoxes={}

        self.header=Header(self,"Register",HEADER_COLOUR) 
        self.header.grid(column=0,row=0,columnspan=3,sticky="EW")

        self.homeButton=ttk.Button(self.header,text="Back",style="Header.TButton",command=lambda:parent.show_frame(HomePage))
        self.homeButton.pack(side="right")

        self.resultsButton=ttk.Button(self.header,text="Switch to results layout",style="Header.TButton",command=lambda:parent.show_frame(ResultsPage,self.results))
        self.resultsButton.pack(side="right")

        #Allows scrolling through the boxes
        self.boxesFrame=ScrollableFrame(self)
        self.boxesFrame.canvas.grid(column=0,row=1,sticky="NES",rowspan=6,columnspan=3)
        self.update()

    #Method override as a work-around for a scrolling bug
    def update(self):
        self.master.state('normal')
        tk.Frame.update(self)
        self.master.state('zoomed')

    def tkraise(self,results,*args,**kwargs):
        tk.Frame.tkraise(self)
        
        while len(self.registerBoxes)>0:
            ID=next(iter(self.registerBoxes))
            self.registerBoxes[ID].grid_forget()
            del self.registerBoxes[ID]

        self.results=results
        #Stores the boxes shown in the scrollable frame
        self.registerBoxes={}

        #Create the boxes and display project data in them
        for projectID in results:
            result=results[projectID]
            self.registerBoxes[projectID]=registerBox(self.boxesFrame,self,projectID,result["name"],result["students"])
            self.registerBoxes[projectID].grid()

        self.update()


class SettingsPage(tk.Frame):
    def __init__(self,parent,fitness,iterations,popSize):
        #Set up swttings page layout
        tk.Frame.__init__(self,parent)
        self.fitness=fitness
        self.iterations=iterations
        self.popSize=popSize

        self.header=Header(self,"Settings",HEADER_COLOUR)
        self.header.pack(fill="x")

        self.backButton=ttk.Button(self.header,text="Back",style="Header.TButton",command=self.go_back)
        self.backButton.pack(side="right")

        self.fitnessVar=tk.DoubleVar(value=self.fitness)
        self.iterVar=tk.IntVar(value=self.iterations)
        self.popSizeVar=tk.IntVar(value=self.popSize)

        ttk.Button(self,text="Export database", command=self.export_db).pack()

        #Only allows user to type a decimal number between 0 and 1, no other characters
        def fitnessCallback(P):
            if re.match("^0(\\.\\d*)?$",P) or re.match("^1(\\.0*)?$",P) or P == "":
                return True
            return False
        
        #Only allows the user to enter positive integers
        def posIntCallback(P):
            return str.isdigit(P) or P==""
        
        fitnessValidate = (self.register(fitnessCallback), '%P')
        posIntValidate = (self.register(posIntCallback), '%P')
        
        ttk.Label(self, text="Target fitness for genetic algorithm (Must be between 0-1).").pack()
        ttk.Label(self,text="Higher target fitness means better groups, with 1 being perfect groupings. May not be reached if maximum iterations is reached").pack()
        ttk.Spinbox(self, textvariable=self.fitnessVar,validate="all",validatecommand=fitnessValidate,from_=0,increment=0.05,to=1).pack()

        ttk.Label(self,text="Maximum iterations the genetic algorithm could complete (may be less if target fitness is reached).").pack()
        ttk.Spinbox(self,textvariable=self.iterVar,validate="all",validatecommand=posIntValidate,from_=1,increment=5,to=100).pack()

        ttk.Label(self,text="Size of populations for genetic algorithm. Greater sizes leads to longer runtime, but better results.").pack()
        ttk.Spinbox(self,textvariable=self.popSizeVar,validate="all",validatecommand=posIntValidate,from_=1,increment=10,to=200).pack()

        ttk.Button(self, text="Save", command=self.save_settings).pack()

    #Method override that runs once everytime this page is opened
    def tkraise(self,*args,**kwargs):
        self.fitnessVar.set(self.fitness)
        self.iterVar.set(self.iterations)
        self.popSizeVar.set(self.popSize)
        tk.Frame.tkraise(self)
    
    def get_settings(self):
        return {"fitness":self.fitness,"iterations":self.iterations,"popSize":self.popSize}

    def go_back(self): #Only show message when setting has been changed
        choice=messagebox.askyesno("Warning","Going back will not save your changes. Do you still wish to proceed?",icon="warning")
        if choice:
            self.master.show_frame(HomePage)

    def validate(self):
        if int(self.popSizeVar.get())>=4:
            if int(self.iterVar.get())>0:
                return True
            else:
                messagebox.showerror(title="Error",message="Max iterations must be greater than 0")
        else:
            messagebox.showerror(title="Error",message="Population size must be greater than or equal to 4")
            return False

    #Validate and save settings input
    def save_settings(self):
        valid=self.validate()
        if valid:
            self.fitness=float(self.fitnessVar.get())
            self.iterations=int(self.iterVar.get())
            self.popSize=int(self.popSizeVar.get())
            self.master.show_frame(HomePage)
            #Update settings.json

    def export_db(self): #The ui for selecting details before selecting directory
        self.write_csv()
    
    #Save database to a csv file
    def write_csv(self):
        filetype=[("CSV file",".csv")]
        file = filedialog.asksaveasfile(filetypes=filetype, defaultextension=filetype)
        if file is not None:
            with sql.connect(DATABASE) as conn:
                cur = conn.cursor()
                #Fetch names of every table
                cur.execute("SELECT name FROM sqlite_schema WHERE type ='table' AND name NOT LIKE 'sqlite_%';")
                tables=cur.fetchall()
                #Fetch all the data from each table
                for table in tables:
                    data=cur.execute("SELECT * FROM "+str(table[0]))

                    #Write to the csv
                    writer = csv.writer(file)
                    writer.writerow("")
                    writer.writerow(table)
                    #Get attribute names
                    cols=[]
                    for col in data.description:
                        cols.append(col[0])
                    writer.writerow(cols)
                    writer.writerows(data)
        else:
            #Warn the user export was not successful
            return
        file.close()

#=====WIDGETS=====

class Header(tk.Frame):
    def __init__(self,parent,text,colour):
        tk.Frame.__init__(self,parent)
        self.config(bg=colour)
        self.label = tk.Label(self, text=text, bg=colour,font=LARGE_FONT)
        self.label.pack(side="left")

class ScrollableFrame(tk.Frame):
    def __init__(self,parent):
        #The only tkinter widget which supports both scrollbars and embedded widgets is a canvas
        self.canvas=tk.Canvas(parent,background="white")
        tk.Frame.__init__(self,self.canvas)

        self.scrollbar=tk.Scrollbar(self.canvas,orient="vertical",command=self.canvas.yview)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right",fill="y")
        self.scrollbar.update()

        #Assign the scrollbar and scrolling function to the canvas
        self.canvas.create_window((0,0),window=self,anchor='nw',width=self.winfo_screenwidth()-self.scrollbar.winfo_width())
        self.canvas.bind("<Configure>",self.scroll)


    def scroll(self,event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"),width=self.winfo_width(),height=self.winfo_height())

#Has checkbox, name, edit button, delete button.
class selectionBox(tk.Frame):
    def __init__(self,parent,page,ID,name):
        tk.Frame.__init__(self,parent,relief="solid",bd=2)

        self.ID=ID
        self.name=name
        self.page=page

        self.selected=tk.BooleanVar(value=False)
        self.checkbox=ttk.Checkbutton(self,variable=self.selected,onvalue=True,offvalue=False)
        self.checkbox.pack()

        self.nameLabel=ttk.Label(self,text=name)
        self.nameLabel.pack()

        self.editButton=ttk.Button(self,text="Edit",command=self.edit)
        self.editButton.pack()

        self.deleteButton=ttk.Button(self,text="Delete",command=self.delete)
        self.deleteButton.pack()

    #Return whether this item has been selected by the user
    def check_selection(self):
        return self.selected.get()

    #Opens the edit window, which is handled by the page the box is located within
    def edit(self):
        self.page.editBox(self.ID)
    
    #Ask for confirmation before deletion
    #Deletion is handled by the page the box is located on
    def delete(self):
        delChoice=messagebox.askyesno(title="Delete entry", message=f"Are you sure you want to delete {self.name}?")
        if delChoice:
            #Ensure deleted data can never get caught up in the algorithm
            self.selected.set(False)
            self.page.deleteBox(self.ID)
    
    #Ensure all boxes follow the same design
    def pack(self):
        tk.Frame.pack(self,fill="x",padx=10,pady=5)

    #-----Abstract methods-----
    def get_data(self):
        return
    
    def edit_data(self):
        return
        

class projectBox(selectionBox):
    def __init__(self,parent,page,ID,name,maxSize,minSize,optional,skills):
        selectionBox.__init__(self,parent,page,ID,name)
        self.maxSize=maxSize
        self.minSize=minSize
        self.optional=optional
        self.skills=skills

        self.maxSizeLabel=ttk.Label(self,text=f"Max group size: {maxSize}")
        self.maxSizeLabel.pack()

        self.minSizeLabel=ttk.Label(self,text=f"Min group size: {minSize}")
        self.minSizeLabel.pack()

        self.optionalLabel=ttk.Label(self,text=f"Optional: {optional}")
        self.optionalLabel.pack()

        self.skillsLabel=ttk.Label(self,text=f"Skills: {", ".join(skills)}")
        self.skillsLabel.pack()

    #Return all the data about the project
    def get_data(self):
        return {"ID":self.ID,"name":self.name,"maxSize":self.maxSize,"minSize":self.minSize,"optional":self.optional,"skills":self.skills}
    
    #After the user has edited some project data, this method updates its data stores and changes the data shown on the GUI
    def edit_data(self,**kwargs):
        if "name" in kwargs:
            self.name=kwargs["name"]
            self.nameLabel.config(text=self.name)
        if "maxSize" in kwargs:
            self.maxSize=kwargs["maxSize"]
            self.maxSizeLabel.config(text=f"Max group size: {self.maxSize}")
        if "minSize" in kwargs:
            self.minSize=kwargs["minSize"]
            self.minSizeLabel.config(text=f"Min group size: {self.minSize}")
        if "optional" in kwargs:
            self.optional=kwargs["optional"]
            self.optionalLabel.config(text=f"Optional: {self.optional}")
        if "skills" in kwargs:
            self.skills=kwargs["skills"]
            self.skillsLabel.config(text=f"Skills: {", ".join(self.skills)}")

class studentBox(selectionBox):
    def __init__(self, parent, page, ID, name, gender, skills):
        selectionBox.__init__(self,parent,page,ID,name)
        self.gender=gender
        self.skills=skills

        self.genderLabel = ttk.Label(self,text=f"Gender: {gender}")
        self.genderLabel.pack()

        self.skillsLabel = ttk.Label(self, text= f"Skills: {", ".join(skills)}")
        self.skillsLabel.pack()

    #Returns all data about the student
    def get_data(self):
        return {"ID":self.ID,"name":self.name,"gender":self.gender,"skills":self.skills}
    
    #After the user has edited some student data, this method updates its data stores and changes the data shown on the GUI
    def edit_data(self,**kwargs):
        if "name" in kwargs:
            self.name=kwargs["name"]
            self.nameLabel.config(text=self.name)
        if "gender" in kwargs:
            self.gender=kwargs["gender"]
            self.genderLabel.config(text=f"Gender: {self.gender}")
        if "skills" in kwargs:
            self.skills=kwargs["skills"]
            self.skillsLabel.config(text=f"Skills: {", ".join(self.skills)}")

#Customisable pop-up widget where different types of entries and buttons can be added dynamically
class entryPopupWin(tk.Toplevel):
    def __init__(self,parent,title):
        tk.Toplevel.__init__(self,parent)
        self.title(title)
    
    def add_string_entry(self,text,variable):
        ttk.Label(self, text=text).pack()
        ttk.Entry(self, textvariable=variable).pack()

    def add_int_entry(self,text,variable,minimum=0,maximum=100,increment=1):

        #Prevents user from typing non numbers into number-only entry boxes
        def intCallback(P):
            return str.isdigit(P) or P == ""
        
        intValidate = (self.register(intCallback), '%P')
        
        ttk.Label(self, text=text).pack()
        ttk.Spinbox(self, textvariable=variable,validate="all",validatecommand=intValidate,from_=minimum,increment=increment,to=maximum).pack()
    
    def add_checkbox(self,text,variable):
        ttk.Label(self, text=text).pack()
        ttk.Checkbutton(self, variable=variable, onvalue=True, offvalue=False).pack()
    
    def add_save_cancel(self,window,mode,**kwargs):
        ttk.Button(self, text="Save", command=lambda:self.master.save_entry(window,mode,**kwargs)).pack()
        ttk.Button(self, text="Cancel", command=self.destroy).pack()


class resultBox(tk.Frame):
    #Used for ensuring adjacent boxes have different colours
    count=0
    def __init__(self,parent,page,ID,name,students:list,size,genders:dict,skills:dict):
        tk.Frame.__init__(self,parent,relief="solid",bd=2)

        #Used for ensuring adjacent boxes have different colours
        resultBox.count+=1
        self.colour=PASTEL_COLOURS[(resultBox.count-1)%6]
        self.config(bg=self.colour)


        self.page=page
        self.ID=ID

        ttk.Label(self,text=name,background=self.colour).pack(anchor="w")
        ttk.Separator(self).pack(fill="x")

        ttk.Label(self,text=f"Students: {", ".join(students)}",background=self.colour).pack(anchor="w")
        ttk.Label(self,text=f"Group size: {size}",background=self.colour).pack(anchor="w")
        
        ttk.Label(self,text="Genders:",background=self.colour).pack(anchor="w")
        for gender in genders:
            ttk.Label(self,text=f"  > {gender}: {genders[gender]}",background=self.colour).pack(anchor="w")
        
        ttk.Label(self,text="Skills:",background=self.colour).pack(anchor="w")
        for skill in skills:
            ttk.Label(self,text=f"   > {skill}: {skills[skill]}",background=self.colour).pack(anchor="w")

    #Ensure this widget always follows the same design
    def pack(self):
        tk.Frame.pack(self,fill="x",padx=10,pady=5)

class registerBox(tk.Frame):
    #Used for ensuring adjacent boxes have different colours
    count=0
    def __init__(self,parent,page,ID,name,students:list):
        tk.Frame.__init__(self,parent,relief="solid",bd=2)

        #Used for ensuring adjacent boxes have different colours
        registerBox.count+=1
        self.colour=PASTEL_COLOURS[(registerBox.count-1)%6]
        self.config(bg=self.colour)

        ttk.Label(self,text=name,background=self.colour).pack(anchor="w")
        ttk.Separator(self).pack(fill="x")

        for student in students:
            ttk.Label(self,text=student,background=self.colour).pack(anchor="w")





        

    
#=====SUBROUTINES=====
def checkForDB(path):
    #Database files could have any extension, but they all start with the same first 15 characters.
    file=open(path,"rb")
    line=file.read(15)
    file.close()
    #Convert binary to string
    line="".join(chr(x) for x in line)
    if line == "SQLite format 3":
        return True
    return False


#=====MAIN=====

app=Window()
app.mainloop()