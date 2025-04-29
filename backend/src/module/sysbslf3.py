from mysql.connector import connect, cursor
import math

class create():
    def __init__(self, host, user, password, database):
        self.conn = connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.conn.cursor()

    def init(self):
        statements = [
            """ CREATE TABLE IF NOT EXISTS Standort (
                Standort_ID INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(100) NOT NULL,
                Adresse VARCHAR(255)
            ); """,
            """ CREATE TABLE IF NOT EXISTS Netzelement (
                Netzelement_ID INT AUTO_INCREMENT PRIMARY KEY,
                Typ VARCHAR(50),
                Standort_ID INT,
                FOREIGN KEY (Standort_ID) REFERENCES Standort(Standort_ID)
            ); """,
            """ CREATE TABLE IF NOT EXISTS Schnittstellentyp (
                Schnittstellen_Typ_ID INT AUTO_INCREMENT PRIMARY KEY,
                Typ VARCHAR(50),
                Medium VARCHAR(50),
                Bandbreite VARCHAR(50)
            ); """,
            """ CREATE TABLE IF NOT EXISTS Schnittstelle (
                Schnittstellen_ID INT AUTO_INCREMENT PRIMARY KEY,
                Portbezeichnung VARCHAR(100),
                Schnittstellen_Typ_ID INT,
                MAC_Adresse VARCHAR(17),
                Netzelement_ID INT,
                FOREIGN KEY (Schnittstellen_Typ_ID) REFERENCES Schnittstellentyp(Schnittstellen_Typ_ID),
                FOREIGN KEY (Netzelement_ID) REFERENCES Netzelement(Netzelement_ID)
            ); """,
            """ CREATE TABLE IF NOT EXISTS Subnetz (
                Subnetz_ID INT AUTO_INCREMENT PRIMARY KEY,
                Netzadresse VARCHAR(45) NOT NULL,
                Subnetzmaske VARCHAR(45) NOT NULL,
                Beschreibung TEXT
            ); """,
            """ CREATE TABLE IF NOT EXISTS IP_Adresse (
                IP_Adresse VARCHAR(45) PRIMARY KEY,
                Subnetz_ID INT,
                FOREIGN KEY (Subnetz_ID) REFERENCES Subnetz(Subnetz_ID)
            ); """,
            """ CREATE TABLE IF NOT EXISTS IP_Vergabe (
                IP_Adresse VARCHAR(45),
                Schnittstellen_ID INT,
                Zuweisungsdatum DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (IP_Adresse, Schnittstellen_ID),
                FOREIGN KEY (IP_Adresse) REFERENCES IP_Adresse(IP_Adresse),
                FOREIGN KEY (Schnittstellen_ID) REFERENCES Schnittstelle(Schnittstellen_ID)
            ); """,
            """ CREATE TABLE IF NOT EXISTS VLAN (
                VLAN_ID INT AUTO_INCREMENT PRIMARY KEY,
                Bezeichnung VARCHAR(100),
                Mode VARCHAR(50)
            ); """,
            """ CREATE TABLE IF NOT EXISTS VLAN_Schnittstelle (
                VLAN_ID INT,
                Schnittstellen_ID INT,
                PRIMARY KEY (VLAN_ID, Schnittstellen_ID),
                FOREIGN KEY (VLAN_ID) REFERENCES VLAN(VLAN_ID),
                FOREIGN KEY (Schnittstellen_ID) REFERENCES Schnittstelle(Schnittstellen_ID)
            ); """]
        for stmt in statements:
            self.cursor.execute(stmt)
            self.conn.commit()
        return "initialisiert"
    
    def deldb(self):
        self.cursor.execute("SHOW TABLES")
        tables = self.cursor.fetchall()
        deltables = []

        self.cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        for table in tables:
            table_name = table[0]
            self.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            self.conn.commit()
            deltables.append(table_name)
        
        self.cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        deltables_str = ", ".join(deltables)
        return f"folgende Tabellen wurden gelöscht: {deltables_str}"
    
    def get_all_netzelemente(self):
        self.cursor.execute("SELECT * FROM Netzelement;")
        return self.cursor.fetchall()
    
    def get_client_gereate(self):
        self.cursor.execute("SELECT * from Netzelement WHERE Typ IN ('PC', 'Laptop');")
        return self.cursor.fetchall()
    
    def get_schnittstellen_fuer_geraet(self, geraet_id):
        self.cursor.execute("""
            SELECT Schnittstelle.*, Netzelement.Typ
            FROM Schnittstelle
            JOIN Netzelement ON Schnittstelle.Netzelement_ID = Netzelement.Netzelement_ID
            WHERE Netzelement.Netzelement_ID = %s;
        """, (geraet_id,))
        return self.cursor.fetchall()


    def get_geraete_in_subnetz(self, subnetz_id):
        self.cursor.execute("""
            SELECT DISTINCT Netzelement.*
            FROM Netzelement
            JOIN Schnittstelle ON Schnittstelle.Netzelement_ID = Netzelement.Netzelement_ID
            JOIN IP_Vergabe ON IP_Vergabe.Schnittstellen_ID = Schnittstelle.Schnittstellen_ID
            JOIN IP_Adresse ON IP_Adresse.IP_Adresse = IP_Vergabe.IP_Adresse
            WHERE IP_Adresse.Subnetz_ID = %s;
        """, (subnetz_id,))
        return self.cursor.fetchall()