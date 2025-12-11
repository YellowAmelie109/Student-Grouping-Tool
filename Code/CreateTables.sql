-- SQLite
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Students (
    StudentID INTEGER PRIMARY KEY,
    Name TEXT,
    Gender TEXT
);

CREATE TABLE IF NOT EXISTS StudentSkills (
    StudentID INTEGER NOT NULL,
    Skill TEXT NOT NULL,
	PRIMARY KEY (StudentID, Skill),
	FOREIGN KEY (StudentID) REFERENCES Students (StudentID) 
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Projects (
    ProjectID INTEGER PRIMARY KEY,
    Name TEXT,
    MaxSize INTEGER,
    MinSize INTEGER,
    Optional INTEGER
);

CREATE TABLE IF NOT EXISTS ProjectSkills (
    ProjectID INTEGER NOT NULL,
    Skill TEXT NOT NULL,
	PRIMARY KEY (ProjectID, Skill),
	FOREIGN KEY (ProjectID) REFERENCES Projects (ProjectID) 
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Results (
    ResultID INTEGER PRIMARY KEY,
    ProjectID INTEGER NOT NULL,
    LocalTimeGenerated TEXT,
    EpochTimeGenerated INTEGER,
    FOREIGN KEY (ProjectID) REFERENCES Projects (ProjectID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
    
);

CREATE TABLE IF NOT EXISTS ResultStudentLink (
    ResultID INTEGER NOT NULL,
    StudentID INTEGER NOT NULL,
	PRIMARY KEY (ResultID, StudentID),
    FOREIGN KEY (ResultID) REFERENCES Results (ResultID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
	FOREIGN KEY (StudentID) REFERENCES Students (StudentID) 
        ON DELETE CASCADE
        ON UPDATE CASCADE
);