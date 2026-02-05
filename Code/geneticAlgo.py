from algoClasses import Project,Student,Individual
import sqlite3 as sql
import random

def get_students(database,IDs):
     students=[]

     with sql.connect(database) as conn:
          cur = conn.cursor()
 
          for ID in IDs:
               #Get each students' skills
               cur.execute("SELECT Skill FROM StudentSkills WHERE StudentID = ?",(ID,))
               skills=cur.fetchall()[0]

               #Get each students' name and gender
               cur.execute("SELECT Name, Gender from Students WHERE StudentID = ?",(ID,))
               entry=cur.fetchall()[0]

               #Create a Student object for each student with their name, skills, and gender
               students.append(Student(entry[0],skills,entry[1]))

     return students


def get_projects(database,IDs):
     projects={"optional":[],"notOptional":[]}

     with sql.connect(database) as conn:
          cur = conn.cursor()

          for ID in IDs:
               #Get each projects' skill requirements
               cur.execute("SELECT Skill FROM ProjectSkills WHERE ProjectID = ?",(ID,))
               skills=cur.fetchall()[0]

               #Get each projects' data other than skills
               cur.execute("SELECT Name, MaxSize, MinSize, Optional from Projects WHERE ProjectID = ?",(ID,))
               entry=cur.fetchall()[0]

               #Create a Project object for each project with its name, skills, maxSize, minSize, and whether or not it is optional
               if bool(entry[3]):
                    projects["optional"].append(Project(entry[0],skills,entry[1],entry[2],entry[3]))
               else:
                    projects["notOptional"].append(Project(entry[0],skills,entry[1],entry[2],entry[3]))
                 

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


def GenInitialGroups(projects,students):
     individual=Individual()
     leftover=[] #Stores projects that have groups, but do not have the maximum number of students assigned yet

     #Fill every required project to minSize
     required=projects["notOptional"]
     for project in required:
          random.shuffle(students)
          project.addStudent(students[:project.minSize])
          individual.addProject(project)

          #Remove grouped students
          students=students[project.minSize:]

          #Keep projects with room to spare so that they may take on more students later
          if project.minSize!=project.maxSize:
               leftover.append(project)

     #Ensure every student is grouped
     optionals=projects["Optional"] #Stores projects that do not yet have a group assigned

     while len(students)>0:
          #Only allow students to be grouped to a project with a minSize that allows the remaining students to be housed
          optionals=get_optionals(optionals,len(students))

          #Add random students to a random project
          project=random.choice(leftover+optionals)
          random.shuffle(students)
          
          #If the project has no group currently, add minSize number of students
          if project in optionals:
               optionals.remove(project)
               project.addStudent(students[:project.minSize])
               individual.addProject(project)

               students=students[project.minSize:]

               #If project is not full
               if project.minSize!=project.maxSize:
                    leftover.append(project)

          #If project already has a group, add one student to it
          else:
               project.addStudent(students[0])
               students.pop(0)

               #Remove from list if full
               if len(project.group)==project.maxSize:
                    leftover.remove(project)

     return individual



     
def verifyGroupings(individual):
     return True

def fixGroupings(individual):
     return individual
          
     
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
     for project in projects["optional"]:
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
          population.append(individual)
     
     population.sort(key=lambda x:x.fitness,reverse=True)

     #Genetic algorithm
     for i in range(MAX_ITERATIONS):
          #Ends early when an individual has reached the target fitness
          if population[0].fitness>=TARGET_FITNESS:
               return {"status":0,"results":population[0].projects}
          
          #Eliminate individuals in the bottom half in terms of fitness
          population = population[:POPULATION_SIZE//2]
          new_pop = []

          #Create next population
          for j in range(int(0.9*POPULATION_SIZE)):
               #Crossover random individuals
               parents=random.sample(population, 2)
               individual=parents[0].crossover(parents[1])

               #Ensure all students appear once
               valid = verifyGroupings(individual)
               if not valid:
                   individual=fixGroupings(individual)

               #Random mutations to prevent convergence towards a local best solution
               individual=individual.mutate()

               new_pop.append(individual)
          
          #Create the next population with the crossover population and the best 10% of the last population
          population=population[:POPULATION_SIZE*0.1]
          population+=new_pop
          
          
          
         
if __name__=="__main__":
     run("Code/database.db",[1,3,4,5,6],[4,5,6],0.9,50,10)