class Project:
    def __init__(self,name,skills,maxSize,minSize,optional,group=None):
        self.name=name
        self.skills=skills
        self.maxSize=maxSize
        self.minSize=minSize
        self.optional=optional
        
        self.group=group
        self.fitness=self.calcFitness()
    
    def calcFitness():
        return
    
    def addStudent(self,student):
        self.group.append(student)
        self.fitness=self.calcFitness()

class Student:
    def __init__(self,name,skills,gender):
        self.name=name
        self.skills=skills
        self.gender=gender

class Individual:
    def __init__(self,projects):
        self.projects=projects
        self.fitness=self.calcFitness()
    
    def calcFitness(self):
        return
    
    def addProject(self,project):
        self.projects.append(project)
        self.fitness=self.calcFitness()