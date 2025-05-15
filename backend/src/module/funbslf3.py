import math                                                                                         # Importiert das Math Modul

class Create():                                                                                     # Definiert die Klasse Create, diese wird in der app.py als calc Instanz zum Objekt definiert  
    def __init__(self):                                                                             # Konstruktor der Klasse, enthält die init Daten die beim erstellen einer function mit (self) aufgerufen wird
        pass                                                                                        # Da kein Breakpoint mehr benötigt wird ist hier ein "pass" Statement gesetzt

    def symsub(self, ipv4, countnet):                                                               # Definiert die Methode symsub, welche die daten aus der __init__ aufruft, in diesem Fall "pass"
                                                                                                    # Dazu nimmt die Methode an erster Stelle die angegebene ipv4 an und an zweiter Stelle die Anzahl der Subnetze auf: [Objekt.symsub( stelle1{ipv4}, stelle2{countnet})]
        arr_basis_netz = list(map(int, ipv4.split(".")))                                            # Hier wird das Objekt arr_basis_netz definiert, welches die übergebene ipv4 an den Punkten trennt und jeweils als Integer zurückgibt("192.160.100.0" = "192" & "168" & "100" & "0")
        log_anz_subnetz = math.log2(countnet)                                                       # Hier wird der Logarithmus zur Basis 2 der Anzahl an Subnetzen berechnet, dies gibt wie viele zusätzliche Bits für die Subnetzmaske benötigt werden (2^x = countnet) 

        if log_anz_subnetz % 1 != 0:                                                                # Wenn 'log_anz_subnetz' keine ganze Zahl ist
            log_anz_subnetz = int(log_anz_subnetz) + 1                                              # Wird auf die nächste ganze Zahl aufgerundet und als Integer neu definiert
        else:                                                                                       # Wenn 'log_anz_subnetz' eine ganze Zahl ist
            log_anz_subnetz = int(log_anz_subnetz)                                                  # Wird diese nicht verändert und als Integer neu definiert

        host_anz_subnetz = 2 ** (8 - log_anz_subnetz)                                               # Definiert die mögliche Anzahl der möglichen Host-Adressen in einem Oktett basierend auf den neuen Subnetz Bits
        host_anzahl = host_anz_subnetz - 2                                                          # Hier wird die maximale Anzahl der tatsächlichen nutzbaren Host-Adressen berechnet und definiert (es werden Zwei Adressen für die Netzwerkadresse und die Broadcastadresse abgezogen)

        neue_prefix = 24 + log_anz_subnetz                                                          # Wird gehen hier von einem Basis /24 Netzwerk aus, dementsprechend besteht der neue CIDR-Prefix aus einer Addition von den Bits unseres /24 Basisnetzes und den Bits unserer gespeicherten Variable 'log_anz_subnetz' 
        outnewsub = f"/{neue_prefix}"                                                               # Hier wird die neue Subnetzmaske in das CIDR-Format formatiert
        outmaxhost = host_anzahl                                                                    # Hier wird die Anzahl der nutzbaren Hosts gespeichert für die Ausgabe

        subnetzadressen = []                                                                        # Hier wird eine Liste initialisiert für die Netzwerkadressen der erstellten Subnetze, um diese zu speichern
        for i in range(countnet):                                                                   # Hier ist eine Schleife für jedes Subnetz das erstellt werden soll (von 0 bis 'countnet' -1)
            drittes_octett = arr_basis_netz[2] + (i * host_anz_subnetz) // 256                      # Hier wird das dritte Oktett berechnet. Hierfür wird das ursprüchliche Oktett genopmmen und addiert mit ([aktuelle Subnetznummer] * [Blockgröße]). Die Ganzzahldivision durch 256 ist da um Überläufe in das vierte Oktett korrekt zu behandeln
            viertes_octett = (i * host_anz_subnetz) % 256                                           # Hier wird das vierte Oktett berechet. Hierfür wird die aktuelle Subnetznummer ebenfalls mit der Blockgröße addiert. Um den korrekten Wert zu erhalten wird der Modulo 256 verwendet
            addr = f"{arr_basis_netz[0]}.{arr_basis_netz[1]}.{drittes_octett}.{viertes_octett}"     # Hier wird die vollständige Subnetz-Netzwerkadresse als String konfiguriert
            subnetzadressen.append(addr)                                                            # Speichert die generierte Subnetzadresse in der angelegten Liste

        return {                                                                                    # gibt ein Dictionary mit den berechneten Informationen zurück
            "hosts_per_subnet": outmaxhost,                                                         # Anzahl der nutzbaren Hosts pro Subnetz
            "subnet_mask": outnewsub,                                                               # Neue Subnetzmaske im CIDR-Format
            "subnet_addresses": subnetzadressen                                                     # Liste der Netzwerkadressen der Subnetze
        }
