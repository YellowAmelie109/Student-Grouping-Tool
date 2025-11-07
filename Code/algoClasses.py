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