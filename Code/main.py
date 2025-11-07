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
        #self.geometry("1100x700")
        #self.attributes("-fullscreen", True)
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}")
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
        if True:
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

        self.projectBoxes={}
        for i in range(10):
            name="Name"+str(i)
            self.projectBoxes[name]=projectBox(self.boxesFrame,self,name,0,0,True,["g"])
            self.projectBoxes[name].pack(fill="x",padx=10,pady=5)

    

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
        popupWin=tk.Toplevel(self.master)
        name=tk.StringVar()
        maxSize=tk.IntVar()
        minSize=tk.IntVar()
        optional=tk.BooleanVar()
        #skills=

    def editBox(self,boxName):
        return
    
    def deleteBox(self,boxName):
        self.projectBoxes[boxName].pack_forget()
        del self.projectBoxes[boxName]




class StudentPage(tk.Frame):
    def __init__(self,parent):
        tk.Frame.__init__(self, parent)

        self.header=Header(self,"Students",HEADER_COLOUR) 
        self.header.pack(fill="x")

        self.backButton=ttk.Button(self.header,text="Back",style="Header.TButton",command=lambda:parent.show_frame(HomePage)) #Change to check where it should go back to
        self.backButton.pack(side="right")


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

        self.checkbox=ttk.Checkbutton(self)
        self.checkbox.pack()

        self.nameLabel=ttk.Label(self,text=name)
        self.nameLabel.pack()

        self.editButton=ttk.Button(self,text="Edit",command=self.edit)
        self.editButton.pack()

        self.deleteButton=ttk.Button(self,text="Delete",command=self.delete)
        self.deleteButton.pack()

    def edit(self):
        self.page.editBox(self.name)
    
    def delete(self):
        delChoice=messagebox.askyesno(title="Delete entry", message=f"Are you sure you want to delete {self.name}?")
        if delChoice:
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

#=====MAIN=====

app=Window()
app.mainloop()