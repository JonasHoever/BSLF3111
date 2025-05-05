import math

class Create():
    def __init__(self):
        pass  # Kein Breakpoint mehr nötig

    def symsub(self, ipv4, countnet):
        arr_basis_netz = list(map(int, ipv4.split(".")))
        log_anz_subnetz = math.log2(countnet)

        if log_anz_subnetz % 1 != 0:
            log_anz_subnetz = int(log_anz_subnetz) + 1
        else:
            log_anz_subnetz = int(log_anz_subnetz)

        host_anz_subnetz = 2 ** (8 - log_anz_subnetz)
        host_anzahl = host_anz_subnetz - 2

        neue_prefix = 24 + log_anz_subnetz
        outnewsub = f"/{neue_prefix}"
        outmaxhost = host_anzahl

        subnetzadressen = []
        for i in range(countnet):
            drittes_octett = arr_basis_netz[2] + (i * host_anz_subnetz) // 256
            viertes_octett = (i * host_anz_subnetz) % 256
            addr = f"{arr_basis_netz[0]}.{arr_basis_netz[1]}.{drittes_octett}.{viertes_octett}"
            subnetzadressen.append(addr)

        return {
            "hosts_per_subnet": outmaxhost,
            "subnet_mask": outnewsub,
            "subnet_addresses": subnetzadressen
        }
