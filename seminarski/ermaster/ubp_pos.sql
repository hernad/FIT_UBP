
/* Drop Tables */

DROP TABLE RN_STAVKE;
DROP TABLE ARTIKLI;
DROP TABLE RN_FISKALNI;
DROP TABLE RACUNI;
DROP TABLE OPERATERI;
DROP TABLE PARAMETRI;
DROP TABLE REKLAMIRANI_RN;


/* Create Tables */

CREATE TABLE ARTIKLI
(
	ID INTEGER PRIMARY KEY,
	KOD CHAR(10) UNIQUE,
	BARKOD CHAR(13) UNIQUE,
	JMJ CHAR(3) NOT NULL,
	CIJENA DECIMAL(10,2) NOT NULL,
	NAZIV VARCHAR(150),
	CONSTRAINT cijena_naziv UNIQUE (CIJENA, NAZIV)
);


CREATE TABLE OPERATERI
(
	ID INTEGER PRIMARY KEY,
	NAZIV VARCHAR(100)
);


CREATE TABLE PARAMETRI
(
	ID INTEGER PRIMARY KEY,
	SVRHA CHAR(1) NOT NULL UNIQUE,
	OPIS VARCHAR(200)
);


CREATE TABLE RACUNI
(
	ID INTEGER PRIMARY KEY,
	TIP SMALLINT DEFAULT 1 NOT NULL,
	BROJ INTEGER NOT NULL,
	DATUM DATE NOT NULL,
	UKUPNO_S_PDV DECIMAL(10,2) NOT NULL,
	OPERATER_ID INTEGER NOT NULL,
	
	CONSTRAINT broj_datum UNIQUE (BROJ, DATUM),

	FOREIGN KEY (OPERATER_ID) REFERENCES OPERATERI (ID),
        FOREIGN KEY (ID) REFERENCES REKLAMIRANI_RN (REKLAMIRANI_RN_ID)
);


CREATE TABLE REKLAMIRANI_RN
(
	REKLAMIRANI_RN_ID INTEGER NOT NULL,
	RACUN_ORIGINAL_ID INTEGER,
	PRIMARY KEY (REKLAMIRANI_RN_ID)
);


CREATE TABLE RN_FISKALNI
(
	RACUN_ID INTEGER NOT NULL,
	DATUM DATE NOT NULL,
	VRIJEME TIME NOT NULL,
	BR_FISKALNOG_ISJECKA INTEGER,
	UKUPNO_S_PDV DECIMAL(10,2),
	PRIMARY KEY (RACUN_ID, DATUM, VRIJEME),
	FOREIGN KEY (RACUN_ID) REFERENCES RACUNI (ID)
);


CREATE TABLE RN_STAVKE
(
	ID integer primary key,
	RACUN_ID INTEGER,
	ARTIKAL_ID INTEGER NOT NULL,
	KOLICINA DECIMAL(12,3),
	CIJENA DECIMAL(10,2),

	FOREIGN KEY (ARTIKAL_ID) REFERENCES ARTIKLI (ID),
	FOREIGN KEY (RACUN_ID) REFERENCES RACUNI (ID)

);












