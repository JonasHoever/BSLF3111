import math                                                                                         # Importiert das Math Modul
import subfunc

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

    def symsubprefix(self, ipv4, prefix, countnet):
        """
        Berechnet 'countnet' aufeinanderfolgende Subnetze
        mit einer festen 'prefix'-Länge, beginnend bei 'ipv4'.
        """
        # Validierung der Eingaben
        ValidPrefix = subfunc.valid_prefix(prefix)
        if ValidPrefix[0] == False:
            raise ValueError(ValidPrefix[1])
        ValidCountnet = subfunc.valid_countnet(countnet)
        if ValidCountnet[0] == False:
            raise ValueError(ValidCountnet[1])
        
        # --- Variablen-Initialisierung nach außen verschoben ---
        netzmaske_bits = prefix
        netzmaske_dez = [] # Hier initialisiert
        temp_prefix_length = netzmaske_bits

        # Berechnung der Netzmaske
        for i in range(4):
            if temp_prefix_length >= 8:
                netzmaske_dez.append(255)
                temp_prefix_length -= 8
            else:
                netzmaske_dez.append(256 - (2 ** (8 - temp_prefix_length)))
                temp_prefix_length = 0
        netzmaske_str = ".".join(map(str, netzmaske_dez)) # Hier zugewiesen

        # Weitere Variablen initialisiert
        host_bits = 32 - netzmaske_bits
        usable_hosts = (2 ** host_bits) - 2 # -2 für Netz- und Broadcastadresse
        subnet_block_size = 2 ** host_bits
        results = []
        
        # Start-IP in Integer umwandeln
        start_ip_int = 0
        arr_ipv4_start = list(map(int, ipv4.split(".")))
        for i, octet in enumerate(arr_ipv4_start):
            start_ip_int += octet << (8 * (3 - i))
        # --- Ende der Variablen-Initialisierung ---
            
        # Schleife für jedes der 'countnet' Subnetze
        for i in range(countnet):
            current_base_ip_int = start_ip_int + (i * subnet_block_size)
            
            # Überprüfen auf Überlauf über die IPv4-Grenze hinaus
            if current_base_ip_int > 0xFFFFFFFF:
                # Hier ist es besser, die Schleife zu beenden, anstatt einen ValueError zu werfen,
                # da es sich um eine natürliche Grenze der Berechnung handelt und nicht unbedingt
                # um einen "Fehler" in den Eingabeparametern.
                break 
            
            # Aktuelle Integer-IP zurück in dotted-decimal Format umwandeln
            current_base_ip_octets = []
            for j in range(4):
                current_base_ip_octets.append((current_base_ip_int >> (8 * (3 - j))) & 0xFF)
            current_base_ipv4_str = ".".join(map(str, current_base_ip_octets))

            # Netzwerkadresse berechnen
            network_address_arr = []
            for k in range(4):
                # Hier war der Fehler: netzmaske_dez muss Elemente enthalten.
                network_address_arr.append(current_base_ip_octets[k] & netzmaske_dez[k])
            network_address = ".".join(map(str, network_address_arr))
            
            # Broadcast-Adresse berechnen
            broadcast_address_arr = []
            for k in range(4):
                # Verwende bitweises OR mit invertierter Netzmaske (255 ^ netzmaske_dez[k]) für korrekte Broadcast
                broadcast_address_arr.append(current_base_ip_octets[k] | (255 ^ netzmaske_dez[k]))
            broadcast_address = ".".join(map(str, broadcast_address_arr))

            # Erster und letzter Host
            first_host = "N/A"
            last_host = "N/A"
            if usable_hosts > 0:
                first_host_arr = list(network_address_arr)
                first_host_arr[3] += 1

                last_host_arr = list(broadcast_address_arr)
                last_host_arr[3] -= 1

                # Behandle Überträge/Unterläufe
                for octet_idx in range(3, -1, -1): # Schleife von 3 bis 0, auch das erste Oktett prüfen
                    # Erster Host
                    if first_host_arr[octet_idx] > 255:
                        first_host_arr[octet_idx] = 0
                        if octet_idx > 0: first_host_arr[octet_idx - 1] += 1
                    elif first_host_arr[octet_idx] < 0:
                        first_host_arr[octet_idx] = 255
                        if octet_idx > 0: first_host_arr[octet_idx - 1] -= 1
                    
                    # Letzter Host
                    if last_host_arr[octet_idx] < 0:
                        last_host_arr[octet_idx] = 255
                        if octet_idx > 0: last_host_arr[octet_idx - 1] -= 1
                    elif last_host_arr[octet_idx] > 255:
                        last_host_arr[octet_idx] = 0
                        if octet_idx > 0: last_host_arr[octet_idx - 1] += 1
                    
                first_host = ".".join(map(str, first_host_arr))
                last_host = ".".join(map(str, last_host_arr))
            
            results.append({
                "subnet_number": i + 1,
                "base_ipv4_input_for_this_subnet": current_base_ipv4_str,
                "prefix_length": f"/{prefix}",
                "subnet_mask": netzmaske_str,
                "network_address": network_address,
                "broadcast_address": broadcast_address,
                "usable_hosts": usable_hosts,
                "first_host": first_host,
                "last_host": last_host
            })
        return {"subnets": results}
    
    def symsubany(self, ipv4, prefix, countnet):                                                    # Definition der neuen methode symsubany
        #Validierung der Daten
        ValidPrefix = subfunc.valid_prefix(prefix)
        if ValidPrefix[0] == False:
            ValueError = ValidPrefix[1]
        ValidCountnet = subfunc.valid_countnet(countnet)
        if ValidCountnet[0] == False:
            ValueError = ValidPrefix[1]