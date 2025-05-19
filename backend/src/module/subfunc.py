import math

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