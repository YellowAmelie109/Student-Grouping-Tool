class Project:
    def __init__(self,name,skills,maxSize,minSize,optional,group=[]):
        self.name=name
        self.skills=skills
        self.maxSize=maxSize
        self.minSize=minSize
        self.optional=optional
        
        self.group=group
        self.fitness=self.calcFitness()
    
    def calcFitness(self):
        return
    
    def addStudent(self,students):
        if type(students)==list:
            self.group+=students

        elif type(students)==Student:
            self.group.append(students)

        else:
            raise TypeError(f"Expected data with type list or Student, got data of type {type(students)}")

        self.fitness=self.calcFitness()


class Student:
    def __init__(self,name,skills,gender):
        self.name=name
        self.skills=skills
        self.gender=gender
        

class Individual:
    def __init__(self,projects=[]):
        self.projects=projects
        self.fitness=self.calcFitness()
    
    def calcFitness(self):
        return
    
    def addProject(self,projects):
        if type(projects)==list:
            self.projects+=projects

        elif type(projects)==Project:
            self.projects.append(projects)

        else:
            raise TypeError(f"Expected data with type list or Project, got data of type {type(projects)}")

        self.fitness=self.calcFitness()