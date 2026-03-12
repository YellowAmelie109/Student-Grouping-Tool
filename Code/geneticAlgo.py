import sqlite3 as sql
import random

#=====CLASSES=====
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

        #Prevents a divide by 0 error when the group is empty
        try:
            fitness+=(stuCount/len(self.group))*0.6
        except:
            pass
        finally:
            #Prevents a divide by 0 error if the project has no skill requirements
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

    #For testing
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
        #A fitness of -1 suggests this individual is broken (e.g. does not have every student) and should not be considered by the algorithm
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
        
    def crossover(self,other,students):
        students=set(students)
        individual=Individual()
        flagged=dict()
        leftover=dict() #Stores the ID of required projects that have not reached the size of the larger of their parents' groups as keys, with that size as values
        projects1=set(self.projects)
        projects2=set(other.projects)
        #Set of projectIDs of projects in both parents
        required=projects1&projects2
        #List of projects in only one parent
        optionals=list(projects1^projects2)
        optionals=list(map(lambda x:(self.projects|other.projects)[x],optionals))
        
        #Assign a group to every project that appears in both parents
        while len(required)>0:
            #Projects get groups in a random order
            projectID=random.choice(list(required))
            required.remove(projectID)
            project1=self.projects[projectID]
            project2=other.projects[projectID]
            newProject=project1.deepcopy()
            #Combine student lists and remove duplicates
            studentOptions=set(project1.group)|set(project2.group)
            #Remove students in a different group by only keeping students that remain in the students set
            studentOptions&=students

            #Fill the group to the size of the smaller parent group
            minSize=min(len(project1.group),len(project2.group))
            maxSize=max(len(project1.group),len(project2.group))
            if len(studentOptions)>=minSize:
                temp=list(studentOptions)
                random.shuffle(temp)
                group=temp[:minSize]
                #Prevent the grouped students from being grouped to another project
                students-=set(group)
                newProject.addStudent(group)
                if maxSize>len(group):
                    leftover[projectID]=maxSize

            #In case too many students from the parent groups have already been assigned to different projects
            else: 
                students-=studentOptions
                newProject.addStudent(list(studentOptions))
                flagged[projectID]=minSize-len(studentOptions)
            
            individual.addProject(newProject)

        #Ensure every required project has been filled
        while len(flagged)>0:
            projectID=random.choice(list(flagged.keys()))
            size=flagged[projectID]
            del flagged[projectID]
            temp=list(students)
            random.shuffle(temp)
            group=temp[:size]
            students-=set(group)
            individual.projects[projectID].addStudent(group)



        while len(students)>0:
            optionals=get_optionals(optionals,len(students))
            
            projectList=list(leftover)+optionals

            #Incase an individual does not group every student
            if len(projectList)<1:
                individual.fitness=-1
                break
            
            project=random.choice(projectList)
            
            #If the project does not yet have a group, add minSize number of students
            if project in optionals:
                newProject=project.deepcopy()
                optionals.remove(project)
                temp=list(students)
                random.shuffle(temp)
                group=temp[:project.minSize]
                students-=set(group)
                newProject.addStudent(group)
                individual.addProject(newProject)

                #If project is not full, allow for it to get more students
                if project.minSize!=project.maxSize:
                    leftover[project.ID]=project.maxSize-project.minSize
            
            #If project already had a group, add one more student to it
            else:
                projectID=project
                student=random.choice(list(students))
                individual.projects[projectID].addStudent(student)
                students.remove(student)
                
                #Remove from dict if now full
                leftover[projectID]-=1
                if leftover[projectID]<=0:
                    del leftover[projectID]


        return individual
    
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
            


#=====SUBROUTINES=====
#Fetch student details from database
def get_students(database,IDs):
     students=[]

     with sql.connect(database) as conn:
          cur = conn.cursor()
 
          for ID in IDs:
               #Get each students' skills
               cur.execute("SELECT Skill FROM StudentSkills WHERE StudentID = ?",(ID,))
               skills=set()
               result=cur.fetchall()
               for skill in result:
                    skills.add(skill[0])

               #Get each students' name and gender
               cur.execute("SELECT Name, Gender from Students WHERE StudentID = ?",(ID,))
               entry=cur.fetchall()[0]

               #Create a Student object for each student with their name, skills, and gender
               students.append(Student(ID,entry[0],skills,entry[1]))

     return students


#Fetch project details from database
def get_projects(database,IDs):
     projects={"Optional":[],"notOptional":[]}

     with sql.connect(database) as conn:
          cur = conn.cursor()

          for ID in IDs:
               #Get each projects' skill requirements
               cur.execute("SELECT Skill FROM ProjectSkills WHERE ProjectID = ?",(ID,))
               skills=set()
               result=cur.fetchall()
               for skill in result:
                    skills.add(skill[0])

               #Get each projects' data other than skills
               cur.execute("SELECT Name, MaxSize, MinSize, Optional from Projects WHERE ProjectID = ?",(ID,))
               entry=cur.fetchall()[0]

               #Create a Project object for each project with its name, skills, maxSize, minSize, and whether or not it is optional
               if bool(entry[3]):
                    projects["Optional"].append(Project(ID,entry[0],skills,entry[1],entry[2],entry[3]))
               else:
                    projects["notOptional"].append(Project(ID,entry[0],skills,entry[1],entry[2],entry[3]))
                 

     return projects

#find optional projects whose minSize is not too large to house the remaining ungrouped students
def get_optionals(optionals,extraSlots):
     optionals.sort(key=lambda x:x.minSize, reverse=True)
     for i in range(len(optionals)):
          if optionals[i].minSize>extraSlots:
               optionals.pop(i)
          else:
               break
     return optionals


#Creates an individual for the first population
def GenInitialGroups(projects,students):
     individual=Individual()
     leftover=[] #Stores projects that have groups, but do not have the maximum number of students assigned yet

     #Fill every required project to minSize with random students
     required=projects["notOptional"]
     for i in range(len(required)):
          required[i]=required[i].deepcopy()
     for project in required:
          random.shuffle(students)
          project.addStudent(students[:project.minSize])
          individual.addProject(project)

          #Remove grouped students
          students=students[project.minSize:]

          #Keep projects with room to spare so that they may take on more students later
          if project.minSize!=project.maxSize:
               leftover.append(project.ID)

     #Ensure every student is grouped
     optionals=[] #Stores projects that do not yet have a group assigned
     for i in range(len(projects["Optional"])):
          optionals.append(projects["Optional"][i].deepcopy())
     
     while len(students)>0:
          #Only allow students to be grouped to a project with a minSize that allows the remaining students to be housed
          optionals=get_optionals(optionals,len(students))
          
          #Incase an individual does not group every student
          if len(leftover+optionals)<1:
               individual.fitness=-1
               break
          #Add random students to a random project
          project=random.choice(leftover+optionals)
          random.shuffle(students)
          
          #If the project has no group currently, add minSize number of students
          if type(project)==Project:
               optionals.remove(project)
               project.addStudent(students[:project.minSize])
               individual.addProject(project)

               students=students[project.minSize:]

               #If project is not full, allow for it to gain more students
               if project.minSize!=project.maxSize:
                    leftover.append(project.ID)

          #If project already has a group, add one student to it
          else:
               individual.projects[project].addStudent(students[0])
               students.pop(0)

               #Remove from list if now full
               if len(individual.projects[project].group)>=individual.projects[project].maxSize:
                    leftover.remove(project)
     return individual



          

#Runs the genetic algorithm
def run(database, studentIDs, projectIDs, TARGET_FITNESS, MAX_ITERATIONS, POPULATION_SIZE):
     #List of students
     students=get_students(database,studentIDs)
     #Two lists of projects in dictionary, separated by whether or not the project is optional
     projects=get_projects(database,projectIDs)

     #Ensure there aren't too many or too few students to meet requirements#
     numStudents=len(students)
     minStudents=0
     maxStudents=0

     #Find max and min amount of students required
     for project in projects["notOptional"]:
          maxStudents += project.maxSize
          minStudents += project.minSize
     for project in projects["Optional"]:
          maxStudents += project.maxSize
     #Return error for too few
     if numStudents<minStudents:
          return {"status":-1,"error":f"Error: Only {len(students)} to fill a minimum of {minStudents} places."}
     #Return error for too many
     elif numStudents>maxStudents:
          return {"status":-1,"error":f"Error: {len(students)} is too many to fit in {maxStudents} places."}
     
     #Generate initial groupings and average fitness
     population = []
     for i in range(POPULATION_SIZE):
          individual = GenInitialGroups(projects, students)
          individual.calcFitness()
          population.append(individual)

     #=====Genetic algorithm======
     for i in range(MAX_ITERATIONS):
          population.sort(key=lambda x:x.fitness,reverse=True)
          #Ends early when an individual has reached the target fitness
          if population[0].fitness>=TARGET_FITNESS:
               return {"status":0,"results":population[0].get_data(),"all":population}
          
          #Eliminate individuals in the bottom half in terms of fitness
          population = population[:POPULATION_SIZE//2]
          new_pop = []

          #Create next population
          crossedSize=int(0.9*POPULATION_SIZE)
          for j in range(crossedSize):
               #Crossover random individuals
               parents=random.sample(population,2)
               individual=parents[0].crossover(parents[1],students)

               #Random mutations to prevent convergence towards a local best solution
               individual=individual.mutate()
               individual.calcFitness()

               new_pop.append(individual)
          
          #Create the next population with the crossover population and the best 10% of the last population
          population=population[:(POPULATION_SIZE-crossedSize)]
          population+=new_pop
     population.sort(key=lambda x:x.fitness,reverse=True)
     return {"status":0,"results":population[0].get_data(),"all":population}
          
          
          
#=====TESTING======    
if __name__=="__main__":
     result=run("Code/database.db",[1,3,4,5,6],[4,5,6],0.9,5,50)
     if result["status"]==0:
          pop=result["all"]
          for ind in pop:
               print(ind.fitness)
               print(ind)
