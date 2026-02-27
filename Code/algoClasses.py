class Project:
    def __init__(self,ID,name,skills,maxSize,minSize,optional):
        self.ID=ID
        self.name=name
        self.skills=skills
        self.maxSize=maxSize
        self.minSize=minSize
        self.optional=optional
        
        self.group=[]

    #Returns count of genders and skills as dicts, and list of students
    def get_data(self):
        genders={}
        skills={}
        students=[]
        for student in self.group:
            if student.gender in genders:
                genders[student.gender]+=1
            else:
                genders[student.gender]=1

            for skill in student.skills:
                if skill in skills:
                    skills[skill]+=1
                else:
                    skills[skill]=1

            students.append(student.__str__())
        return genders,skills,students
    
    #Returns fitness value as a float between 0-1
    def getFitness(self):
        fitness=0.0
        stuCount = 0 #Records number of students with at least one relevant skill
        skillsMet=set() #Records the skills the students have that the project demands
        genderCritMet=False #Records whether or not there are multiple genders in the group
        for student in self.group:
            commonSkills=student.skills&self.skills
            #Each student should have one project that is demanded by the project
            if len(commonSkills)>=1:
                stuCount+=1
            
            #The demands of the project should be met by the students
            skillsMet=skillsMet|commonSkills

            #There should be at least two different genders
            if not genderCritMet and student.gender != self.group[0].gender:
                genderCritMet=True
                fitness+=0.15

        try:
            fitness+=(stuCount/len(self.group))*0.6
        except:
            pass
        finally:
            try:
                fitness+=(len(skillsMet)/len(self.skills))*0.25
            except: 
                #If the project has no skill requirements, every group has met every skill requirement so earns the max weight
                fitness+=0.25
        return fitness
            
    #Adds a student to the project's group
    def addStudent(self,students):
        if type(students)==list:
            self.group+=students

        elif type(students)==Student:
            self.group.append(students)

        else:
            raise TypeError(f"Expected data with type list or Student, got data of type {type(students)}")

    def __str__(self):
        string = self.name +", "
        for student in self.group:
            string += student.__str__() +", "
        return string
    
    #Allows for the same project to appear in different individuals
    def deepcopy(self):
        return Project(self.ID,self.name,self.skills,self.maxSize,self.minSize,self.optional)


class Student:
    def __init__(self,ID,name,skills,gender):
        self.ID=ID
        self.name=name
        self.skills=skills
        self.gender=gender
    def __str__(self):
        return self.name
        

class Individual:
    def __init__(self):
        self.projects=dict()
        self.fitness=0.0
    
    #Average the fitness values of each project together to return a float between 0-1
    def calcFitness(self):
        if self.fitness==-1:
            return -1
        total=0.000
        for project in self.projects.values():
            total+=project.getFitness()
        try:
            self.fitness = round(total/len(self.projects),3)
        except:
            self.fitness = 0.000
        return self.fitness
    
    #Adds a project to the individual's list of projects
    def addProject(self,projects):
        if type(projects)==list:
            for project in projects:
                self.projects[project.ID]=project

        elif type(projects)==Project:
            self.projects[projects.ID]=projects

        else:
            raise TypeError(f"Expected data with type list or Project, got data of type {type(projects)}")
        
    def crossover(self,other):
        return self
    
    def mutate(self):
        return self

    def __str__(self):
        string=""
        for i in self.projects:
            string+= self.projects[i].__str__()+"\n"
        return string
    
    #Returns the names, size, gender count, and skill count for each project as a dict with the projects' IDs as keys
    def get_data(self):
        data=dict()
        for project in self.projects:
            project=self.projects[project]

            genders,skills,students=project.get_data()
            projectData={"name":project.name,"students":students,"size":len(project.group),"genders":genders,"skills":skills}

            data[project.ID]=projectData

        return data
            
