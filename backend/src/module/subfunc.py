import math

#Aufgabe 1
# Array Basis Netz
def array_basis_netz(ipv4):
    arr_basis_netz = list(map(int, ipv4.split(".")))
    return(arr_basis_netz)
# Berechnung Subnetze
def subnet_count(countnet):
    log_anz_subnetz = math.log2(countnet)
    if log_anz_subnetz % 1 != 0:
        log_anz_subnetz = int(log_anz_subnetz) +1
    else:
        log_anz_subnetz = int(log_anz_subnetz)
    host_anz_subnetz = 2 ** (8 - log_anz_subnetz)
    host_anzahl = host_anz_subnetz - 2
    neue_prefix = f"/{24 + log_anz_subnetz}"
    return(host_anzahl, neue_prefix)


# Überprüfung Prefix
def valid_prefix(prefix):
    valid = True
    ValueError = "ungültiger Prefix"
    if not (isinstance(prefix, int) and 0 <= prefix <= 32):
        valid = False
    return(valid, ValueError)

# Überprüfung Anzahl Subnetze 
def valid_countnet(countnet):
    valid = True
    ValueError = "ungültige Anzahl von gewünschten Subnetzen"
    if countnet <= 0:
        valid = False
    return(valid, ValueError)