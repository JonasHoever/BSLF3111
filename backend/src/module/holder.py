import math

class Create():
    def __init__(self):
        pass

    # Die Methode muss jetzt das ursprüngliche Prefix (z.B. 8, 16, 24) erhalten.
    def symsub(self, ipv4_str, original_prefix, countnet):
        # 1. IP-Adresse in Oktette aufteilen
        try:
            arr_basis_netz = list(map(int, ipv4_str.split(".")))
            # Grundlegende Validierung der Oktette
            if not all(0 <= octet <= 255 for octet in arr_basis_netz) or len(arr_basis_netz) != 4:
                raise ValueError("Ungültiges IPv4-Adressformat oder Oktettwerte außerhalb des Bereichs.")
        except ValueError as e:
            # Hier eine spezifische Fehlermeldung, wenn die IP-Adresse ungültig ist
            return {"error": f"Fehler bei der IPv4-Adresse: {e}"}

        # 2. Logik zur Bestimmung der benötigten Subnetz-Bits
        log_anz_subnetz = math.log2(countnet)
        if log_anz_subnetz % 1 != 0:
            log_anz_subnetz = int(log_anz_subnetz) + 1
        else:
            log_anz_subnetz = int(log_anz_subnetz)

        # 3. Das neue Prefix berechnen
        neue_prefix = original_prefix + log_anz_subnetz

        # 4. Fehlerbehandlung: Ungültige Präfixe
        if neue_prefix > 30: # /31 und /32 haben keine nutzbaren Hosts
            return {"error": "Zu viele Subnetze angefordert. Das resultierende Subnetz hätte keine nutzbaren Host-Adressen (Präfix > /30)."}
        if neue_prefix <= original_prefix:
             return {"error": "Die Anzahl der Subnetze ist zu klein, um das Netzwerk weiter zu unterteilen."}
        if original_prefix not in [8, 16, 24]:
             return {"error": "Ungültiges Basis-Präfix. Dieser Rechner unterstützt nur /8, /16 und /24 als Ausgangspräfix."}


        # 5. Berechnung der Host-Bits pro Subnetz und der maximalen Hosts
        # Die Anzahl der Host-Bits im neuen Subnetz
        host_bits_new_subnet = 32 - neue_prefix
        # Die Anzahl der Adressen pro Subnetz (Blockgröße)
        addresses_per_subnet = 2 ** host_bits_new_subnet
        # Anzahl der nutzbaren Hosts (abzüglich Netzwerk- und Broadcast-Adresse)
        hosts_per_subnet_usable = addresses_per_subnet - 2
        if hosts_per_subnet_usable < 0: # Für /31 und /32
             hosts_per_subnet_usable = 0

        # 6. Bestimmung des Oktetts, in dem die Subnetze aufgeteilt werden
        # und Berechnung der Sprungweite pro Oktett
        # Dies ist der kritischste Teil, der angepasst werden muss
        if neue_prefix <= 8: # Fehlerfall, sollte oben abgefangen werden
             return {"error": "Interner Fehler: Neues Präfix kleiner oder gleich ursprünglichem Präfix."}
        elif neue_prefix <= 16: # Subnetting findet im 2. Oktett statt
            subnetting_octet_index = 1 # Index 1 ist das zweite Oktett
            # Wie viele Bits werden im zweiten Oktett für die Subnetze verwendet?
            bits_in_this_octet = neue_prefix - 8
            # Der Sprungwert für dieses Oktett (Blockgröße)
            block_size_in_octet = 2 ** (8 - bits_in_this_octet)
            offset_factor = 256 * 256 # Die Einheit, um die ein Sprung im zweiten Oktett die Gesamtadresse verschiebt
            octet_multiplier = 256 * 256 # Faktor für das dritte Oktett, um in die richtige Position zu kommen
        elif neue_prefix <= 24: # Subnetting findet im 3. Oktett statt
            subnetting_octet_index = 2 # Index 2 ist das dritte Oktett
            bits_in_this_octet = neue_prefix - 16
            block_size_in_octet = 2 ** (8 - bits_in_this_octet)
            offset_factor = 256 # Die Einheit, um die ein Sprung im dritten Oktett die Gesamtadresse verschiebt
            octet_multiplier = 256 # Faktor für das dritte Oktett
        elif neue_prefix <= 30: # Subnetting findet im 4. Oktett statt
            subnetting_octet_index = 3 # Index 3 ist das vierte Oktett
            bits_in_this_octet = neue_prefix - 24
            block_size_in_octet = 2 ** (8 - bits_in_this_octet)
            offset_factor = 1 # Die Einheit, um die ein Sprung im vierten Oktett die Gesamtadresse verschiebt
            octet_multiplier = 1 # Faktor für das vierte Oktett
        else: # /31, /32
            # Sollte oben durch neue_prefix > 30 abgefangen werden, dient hier als Fallback
            return {"error": "Ungültiges Präfix nach Subnetting. Keine Hosts möglich."}


        subnetzadressen = []
        for i in range(countnet):
            # Berechne die absolute Startadresse des Subnetzes in Form einer Ganzzahl
            # Dies ist eine allgemeinere Methode als die oktettweise Addition
            # Hier: Basisadresse + (Subnetznummer * Anzahl Adressen pro Subnetz)
            # Wichtig: Die Basisadresse muss als Ganzzahl repräsentiert werden (z.B. A*256^3 + B*256^2 + C*256^1 + D*256^0)
            base_ip_int = (arr_basis_netz[0] << 24) | \
                          (arr_basis_netz[1] << 16) | \
                          (arr_basis_netz[2] << 8) | \
                          arr_basis_netz[3]

            subnet_start_int = base_ip_int + (i * addresses_per_subnet)

            # Umwandlung der Ganzzahl-Adresse zurück in Oktette
            octets = []
            for shift in [24, 16, 8, 0]:
                octets.append((subnet_start_int >> shift) & 0xFF)
            
            # Überprüfen, ob die berechnete Startadresse noch innerhalb des ursprünglichen Basisnetzes liegt
            # Dies ist wichtig, um zu verhindern, dass Subnetze außerhalb des Geltungsbereichs generiert werden.
            # Beispiel: Für 192.168.0.0/24 solltest du nicht 192.168.1.0/26 als Subnetz bekommen.
            # Hier müsste man prüfen, ob (subnet_start_int >> (32 - original_prefix)) == (base_ip_int >> (32 - original_prefix))
            # Das ist komplizierter und wird oft durch die richtige Wahl von countnet vom Benutzer erwartet.
            # Wenn der Benutzer zu viele Subnetze anfordert, die über das original_prefix hinausgehen,
            # würde das resultierende 'neue_prefix' das Problem schon anzeigen oder das Problem übergeht die Bereichsprüfung.
            # Für eine vollständige Validierung müsste man sicherstellen, dass die generierte Subnetzadresse
            # immer noch dem Netz-Teil des original_prefix entspricht.

            subnetzadressen.append(f"{octets[0]}.{octets[1]}.{octets[2]}.{octets[3]}")

        return {
            "hosts_per_subnet": hosts_per_subnet_usable,
            "subnet_mask": outnewsub,
            "subnet_addresses": subnetzadressen,
            "new_prefix": neue_prefix # Füge das neue Prefix zur Ausgabe hinzu
        }