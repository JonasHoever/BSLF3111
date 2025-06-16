import math                                                                                         # Importiert das Math-Modul für mathematische Operationen wie den Logarithmus.
from src.module import subfunc                                                                      # Importiert benutzerdefinierte Hilfsfunktionen aus einem anderen Modul.

class Create():                                                                                     # Definiert die Klasse Create, diese wird in der app.py als calc Instanz zum Objekt definiert.
    def __init__(self):                                                                             # Konstruktor der Klasse. Wird aufgerufen, wenn ein neues Objekt der Klasse erstellt wird.
        pass                                                                                        # Platzhalter-Anweisung. Zeigt an, dass in diesem Block nichts weiter ausgeführt wird.

    def symsub(self, ipv4, countnet):                                                               # Definiert die Methode symsub, die eine IPv4-Adresse und die gewünschte Anzahl an Subnetzen als Parameter entgegennimmt.
                                                                                                    # Beispielaufruf: [Objekt].symsub(ipv4="192.168.0.0", countnet=4)
        arr_basis_netz = list(map(int, ipv4.split(".")))                                            # Teilt den IPv4-String an den Punkten und wandelt jeden Teil in einen Integer um. Das Ergebnis wird als Liste gespeichert. Z.B. "192.168.0.0" -> [192, 168, 0, 0].
        log_anz_subnetz = math.log2(countnet)                                                       # Berechnet den Logarithmus zur Basis 2 von 'countnet'. Das Ergebnis gibt an, wie viele Bits aus dem Host-Teil "geborgt" werden müssen, um die gewünschte Anzahl an Subnetzen zu erstellen.

        if log_anz_subnetz % 1 != 0:                                                                # Prüft, ob das Ergebnis des Logarithmus eine Kommazahl ist (d.h. 'countnet' ist keine Zweierpotenz).
            log_anz_subnetz = int(log_anz_subnetz) + 1                                              # Wenn ja, wird auf die nächste ganze Zahl aufgerundet, um sicherzustellen, dass genügend Bits für alle Subnetze vorhanden sind.
        else:                                                                                       # Wenn 'countnet' eine exakte Zweierpotenz ist.
            log_anz_subnetz = int(log_anz_subnetz)                                                  # Wird der exakte ganzzahlige Wert der benötigten Bits verwendet.

        host_anz_subnetz = 2 ** (8 - log_anz_subnetz)                                               # Berechnet die "Blockgröße" oder die Anzahl der Adressen pro Subnetz im vierten Oktett. Dies sind die verbleibenden Host-Bits (8 im letzten Oktett) hoch 2.
        host_anzahl = host_anz_subnetz - 2                                                          # Berechnet die Anzahl der *nutzbaren* Host-Adressen pro Subnetz, indem die Netz- und die Broadcast-Adresse abgezogen werden.

        neue_prefix = 24 + log_anz_subnetz                                                          # Geht von einem Klasse-C-Netz (/24) aus und addiert die "geborgten" Bits, um die neue Präfixlänge zu erhalten.
        outnewsub = f"/{neue_prefix}"                                                               # Formatiert die neue Präfixlänge in die CIDR-Notation (z.B. "/26").
        outmaxhost = host_anzahl                                                                    # Speichert die Anzahl der nutzbaren Hosts für die spätere Rückgabe.

        subnetzadressen = []                                                                        # Initialisiert eine leere Liste, um die berechneten Netzwerkadressen der Subnetze zu speichern.
        for i in range(countnet):                                                                   # Eine Schleife, die so oft durchläuft, wie Subnetze erstellt werden sollen. 'i' ist der Index des aktuellen Subnetzes (beginnend bei 0).
            drittes_octett = arr_basis_netz[2] + (i * host_anz_subnetz) // 256                      # Berechnet das dritte Oktett der Subnetzadresse. Dies ist nur relevant, wenn die Subnetze über die Grenze von 256 Adressen im vierten Oktett hinausgehen. Die Ganzzahldivision (//) sorgt für den Übertrag.
            viertes_octett = (i * host_anz_subnetz) % 256                                           # Berechnet das vierte Oktett der Subnetzadresse. Der Modulo-Operator (%) sorgt dafür, dass der Wert innerhalb des gültigen Bereichs (0-255) bleibt, indem er den Rest der Division durch 256 nimmt.
            addr = f"{arr_basis_netz[0]}.{arr_basis_netz[1]}.{drittes_octett}.{viertes_octett}"     # Setzt die vier Oktette zu einer vollständigen IPv4-Adresse im String-Format zusammen.
            subnetzadressen.append(addr)                                                            # Fügt die neu erstellte Subnetzadresse zur Liste 'subnetzadressen' hinzu.

        return {                                                                                    # Gibt ein Dictionary zurück, das die wichtigsten Ergebnisse der Berechnung enthält.
            "hosts_per_subnet": outmaxhost,                                                         # Schlüssel für die Anzahl der nutzbaren Hosts pro Subnetz.
            "subnet_mask": outnewsub,                                                               # Schlüssel für die neue Subnetzmaske im CIDR-Format.
            "subnet_addresses": subnetzadressen                                                     # Schlüssel für die Liste mit den Netzwerkadressen der erstellten Subnetze.
        }

    def symsubprefix(self, ipv4, prefix, countnet):
        """
        Berechnet 'countnet' aufeinanderfolgende Subnetze
        mit einer festen 'prefix'-Länge, beginnend bei 'ipv4'.
        Diese Methode ist flexibler als symsub, da sie mit jeder beliebigen Präfixlänge arbeiten kann.
        """
        # --- Eingabevalidierung ---
        ValidPrefix = subfunc.valid_prefix(prefix)                                                  # Ruft eine Hilfsfunktion auf, um zu prüfen, ob die angegebene Präfixlänge gültig ist (z.B. zwischen 1 und 32).
        if ValidPrefix[0] == False:                                                                 # Wenn die Validierung fehlschlägt...
            raise ValueError(ValidPrefix[1])                                                        # ...wird ein ValueError mit einer erklärenden Nachricht ausgelöst, um die Ausführung zu stoppen.
        ValidCountnet = subfunc.valid_countnet(countnet)                                            # Ruft eine Hilfsfunktion auf, um zu prüfen, ob die Anzahl der Subnetze ein gültiger Wert ist.
        if ValidCountnet[0] == False:                                                               # Wenn die Validierung fehlschlägt...
            raise ValueError(ValidCountnet[1])                                                      # ...wird ebenfalls ein Fehler ausgelöst.
        
        # --- Variablen-Initialisierung ---
        netzmaske_bits = prefix                                                                     # Speichert die Präfixlänge zur besseren Lesbarkeit in einer eigenen Variable.
        netzmaske_dez = []                                                                          # Initialisiert eine leere Liste zur Speicherung der Subnetzmaske im Dezimalformat (z.B. [255, 255, 255, 192]).
        temp_prefix_length = netzmaske_bits                                                         # Temporäre Variable für die Berechnung der Netzmaske.

        # --- Berechnung der Subnetzmaske in Dezimalschreibweise ---
        for i in range(4):                                                                          # Schleife für jedes der vier Oktette der Netzmaske.
            if temp_prefix_length >= 8:                                                             # Wenn die verbleibenden Präfix-Bits 8 oder mehr sind...
                netzmaske_dez.append(255)                                                           # ...ist dieses Oktett vollständig gefüllt (Wert 255).
                temp_prefix_length -= 8                                                             # Reduziere die verbleibenden Bits um 8.
            else:                                                                                   # Wenn weniger als 8 Bits übrig sind...
                netzmaske_dez.append(256 - (2 ** (8 - temp_prefix_length)))                         # ...wird der Wert des Oktetts berechnet. Z.B. bei 2 Bits (temp_prefix_length=2) ist es 256 - 2^(8-2) = 256 - 64 = 192.
                temp_prefix_length = 0                                                              # Alle restlichen Bits wurden in diesem Oktett verbraucht.
        netzmaske_str = ".".join(map(str, netzmaske_dez))                                           # Wandelt die Liste der Dezimalwerte in einen String um (z.B. "255.255.255.192").

        # --- Berechnung weiterer relevanter Werte ---
        host_bits = 32 - netzmaske_bits                                                             # Die Anzahl der Host-Bits ist die Gesamtzahl der Bits (32) minus der Netz-Bits.
        usable_hosts = (2 ** host_bits) - 2 if host_bits > 1 else 0                                 # Anzahl nutzbarer Hosts: 2 hoch Anzahl der Host-Bits, minus 2. Bei /31 (host_bits=1) oder /32 (host_bits=0) gibt es keine nutzbaren Hosts.
        subnet_block_size = 2 ** host_bits                                                          # Die Gesamtgröße des Adressblocks pro Subnetz.
        results = []                                                                                # Leere Liste zur Speicherung der Ergebnisse für jedes Subnetz.
        
        # --- Start-IP in einen 32-Bit-Integer umwandeln für einfachere Arithmetik ---
        start_ip_int = 0
        arr_ipv4_start = list(map(int, ipv4.split(".")))
        for i, octet in enumerate(arr_ipv4_start):
            start_ip_int += octet << (8 * (3 - i))                                                  # Jedes Oktett wird an seine Position im 32-Bit-Integer "geschoben" (Bit-Shift-Operation).
        
        # --- Hauptschleife zur Generierung der Subnetze ---
        for i in range(countnet):
            current_base_ip_int = start_ip_int + (i * subnet_block_size)                            # Berechnet die Start-IP des aktuellen Subnetzes als Integer.
            
            if current_base_ip_int > 0xFFFFFFFF:                                                    # Prüft auf einen Überlauf (größer als die maximale IPv4-Adresse 255.255.255.255).
                break                                                                               # Beendet die Schleife, da keine weiteren gültigen IPv4-Adressen generiert werden können.
            
        # --- Integer-IP zurück in Dotted-Decimal-Format umwandeln ---
            current_base_ip_octets = []
            for j in range(4):
                octet_value = (current_base_ip_int >> (8 * (3 - j))) & 0xFF                         # Extrahiert jedes 8-Bit-Oktett aus dem 32-Bit-Integer.
                current_base_ip_octets.append(octet_value)
            current_base_ipv4_str = ".".join(map(str, current_base_ip_octets))

        # --- Netzwerkadresse berechnen ---
            network_address_arr = []
            for k in range(4):
                network_address_arr.append(current_base_ip_octets[k] & netzmaske_dez[k])            # Bitweises UND zwischen der IP und der Netzmaske ergibt die Netzwerkadresse.
            network_address = ".".join(map(str, network_address_arr))
            
        # --- Broadcast-Adresse berechnen ---
            broadcast_address_arr = []
            for k in range(4):
                broadcast_address_arr.append(current_base_ip_octets[k] | (255 ^ netzmaske_dez[k]))  # Bitweises ODER zwischen der IP und der invertierten Netzmaske (Wildcard) ergibt die Broadcast-Adresse.
            broadcast_address = ".".join(map(str, broadcast_address_arr))

        # --- Ersten und letzten nutzbaren Host berechnen ---
            first_host = "N/A"
            last_host = "N/A"
            if usable_hosts > 0:                                                                    # Nur berechnen, wenn es überhaupt nutzbare Hosts gibt.
                first_host_arr = list(map(int, network_address.split(".")))
                first_host_arr[3] += 1                                                              # Erster Host = Netzwerkadresse + 1.
                
        # Korrektur von Überläufen, falls die Netzwerkadresse auf .255 endet (selten, aber möglich).
                if first_host_arr[3] > 255:
                    first_host_arr[3] = 0
                    first_host_arr[2] += 1                                                          # Übertrag auf das 3. Oktett
        # Weitere Überträge müssten hier behandelt werden, ist für typische Szenarien aber nicht nötig.

                last_host_arr = list(map(int, broadcast_address.split(".")))
                last_host_arr[3] -= 1                                                               # Letzter Host = Broadcast-Adresse - 1.

        # Korrektur von Unterläufen, falls die Broadcast-Adresse auf .0 endet (selten).
                if last_host_arr[3] < 0:
                    last_host_arr[3] = 255
                    last_host_arr[2] -= 1 # "Borgen" vom 3. Oktett.

                first_host = ".".join(map(str, first_host_arr))
                last_host = ".".join(map(str, last_host_arr))
            
        # --- Ergebnis für dieses Subnetz speichern ---
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
    