DROP TABLE IF EXISTS Bruker;

CREATE TABLE Bruker (
       epostadresse VARCHAR(255) NOT NULL,
       passordhash VARCHAR(255),
       fornavn VARCHAR(255),
       etternavn VARCHAR(255),
       CONSTRAINT BrukerPN
       	PRIMARY KEY(epostadresse)
       );

DROP TABLE IF EXISTS Sesjon;

CREATE TABLE Sesjon (
       sesjonsID INTEGER,
       epostadresse VARCHAR(255),
       CONSTRAINT SesjonPN
       	PRIMARY KEY(sesjonsID),
       CONSTRAINT SesjonFN
       	FOREIGN KEY(epostadresse)
	REFERENCES Bruker(epostadresse)
       );

DROP TABLE IF EXISTS Dikt;

CREATE TABLE Dikt (
       diktID INTEGER,
       dikt VARCHAR(255),  
       epostadresse VARCHAR(255),
       CONSTRAINT DiktPN
       	PRIMARY KEY (diktID),
       CONSTRAINT DiktFN
       	FOREIGN KEY(epostadresse)
	REFERENCES Bruker(epostadresse)
       );
