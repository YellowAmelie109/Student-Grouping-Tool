from algoClasses import Project,Student,Individual
import sqlite3 as sql

def get_students(database,IDs):
    students=[]

    with sql.connect(database) as conn:
            cur = conn.cursor()

            
            for ID in IDs:
                #Get each students' skills
                cur.execute("SELECT Skill FROM StudentSkills WHERE StudentID = ?",(ID))
                skills=cur.fetchall()

                #Get each students' name and gender
                cur.execute("SELECT Name, Gender from Students WHERE StudentID = ?",(ID))
                entry=cur.fetchall()

                #Create a Student object for each student with their name, skills, and gender
                students.append(Student(entry[0],skills,entry[1]))

    return students


def get_projects(database,IDs):
    projects=[]

    with sql.connect(database) as conn:
            cur = conn.cursor()

            for ID in IDs:
                #Get each projects' skill requirements
                cur.execute("SELECT Skill FROM ProjectSkills WHERE ProjectID = ?",(ID))
                skills=cur.fetchall()

                #Get each projects' data other than skills
                cur.execute("SELECT Name, MaxSize, MinSize, Optional from Projects WHERE ProjectID = ?",(ID))
                entry=cur.fetchall()

                #Create a Project object for each project with its name, skills, maxSize, minSize, and whether or not it is optional
                projects.append(Project(entry[0],skills,entry[1],entry[2],entry[3]))

    return projects



def run(database, studentIDs, projectIDs, target_fitness, max_iterations, population_size):
    students=get_students(database,studentIDs)
    projects=get_projects(database,projectIDs)

    #Ensure there aren't too many or too few students to meet requirements