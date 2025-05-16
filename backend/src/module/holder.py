{% extends "layouts/navbar.html" %}

{% block content %}
<style>
  /* Übernehmen Sie hier nur die spezifischen Stile für DIESE Seite,
   falls es welche gibt, die NICHT im allgemeinen Cyber-Onyx-CSS sind.
   Animationen wie page-enter, fadeInUp, glitchFade sollten hier stehen.
   Generelle Formular- oder Input-Stile sollten aus dem Haupt-CSS kommen.
   Ich habe einige Stile, die im Haupt-CSS definiert sind, hier entfernt,
   um Doppelung zu vermeiden und das Haupt-CSS wirksam werden zu lassen. */

  .page-enter {
    animation: pageFadeIn 0.6s ease-out forwards;
    opacity: 0;
    transform: translateY(20px) scale(0.98);
  }

  @keyframes pageFadeIn {
    to {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
  }

  .form-group {
    margin-bottom: 1.75rem; /* Übernommen aus dem Haupt-CSS für Konsistenz */
    opacity: 0;
    animation: fadeInUp 0.5s ease-out forwards;
  }

  .form-group:nth-child(1) { animation-delay: 0.2s; }
  .form-group:nth-child(2) { animation-delay: 0.4s; }
  .form-group:nth-child(3) { animation-delay: 0.6s; }
  .form-group:nth-child(4) { animation-delay: 0.8s; } /* Angepasst für die neue Struktur */


  /* Der Button kommt nach den Form Groups, also später animieren */
  button {
    animation: fadeInUp 0.5s ease forwards;
    animation-delay: 1.0s; /* Spätere Animation */
    opacity: 0;
  }


  .results {
    margin-top: 2rem; /* Übernommen aus dem Haupt-CSS */
    /* Restliche Stile kommen aus dem Haupt-CSS (.results, .card) */
    opacity: 0;
    transform: translateY(20px);
    transition: all 0.5s ease; /* Animation für das Erscheinen beibehalten */
  }

  .results.show {
    opacity: 1;
    transform: translateY(0);
    /* Animation von .results.show im Haupt-CSS verwenden */
  }

  .subnet-group {
    /* Stile kommen aus dem Haupt-CSS (.subnet-group, .content-section) */
    margin-top: 1.5rem; /* Anpassung für Abstand zwischen Gruppen */
    animation: glitchFade 0.6s ease-out forwards; /* Glitch-Animation beibehalten */
  }
  /* Erste Subnetz-Gruppe ohne oberen Rand */
  .subnet-group:first-child {
      margin-top: 0;
  }


  @keyframes glitchFade {
    0% {
      opacity: 0;
      transform: scale(0.98) translateY(10px); /* Leichter angepasst */
      filter: hue-rotate(0deg);
    }
    100% {
      opacity: 1;
      transform: scale(1) translateY(0);
      filter: hue-rotate(0deg); /* Glitch im Hue-Rotate nur am Start */
    }
  }

  .result-item {
    /* Stile kommen aus dem Haupt-CSS */
  }

  .result-item label {
    /* Stile kommen aus dem Haupt-CSS */
  }

  @keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  /* Zusätzlicher Stil für den Container um Label und Select */
  .prefix-select-container {
      display: block; /* Oder flex, je nach Layoutwunsch */
      width: 100%;
  }

</style>

<div class="container page-enter">
  <h1>Subnetzrechner mit Prefix</h1>

  <div class="form-group">
    <label for="ip">Basis-IP-Adresse:</label>
    <input type="text" id="ip" placeholder="z.B. 192.168.0.0">
  </div>

  <div class="form-group">
    <label for="prefix">Präfixlänge (CIDR):</label>
    <div class="prefix-select-container">
        <select id="prefix">
            <option value="8">8 (/8)</option>
            <option value="16">16 (/16)</option>
            <option value="24" selected>24 (/24)</option>
        </select>
    </div>
  </div>

  <div class="form-group">
    <label for="countnet">Anzahl gewünschter Subnetze:</label>
    <input type="number" id="countnet" min="1" value="3">
  </div>

  <button onclick="confirmBerechnung()">Berechnen</button>

  <div class="results hidden" id="output">
    <h2>Berechnete Subnetze</h2>
    <div id="subnets-container"></div>
  </div>
</div>

<script>
  function confirmBerechnung() {
    const confirmed = confirm("Möchtest du die Berechnung wirklich neu starten? Bereits angezeigte Ergebnisse werden überschrieben.");
    if (confirmed) {
      berechne();
    }
  }

  async function berechne() {
    const ip = document.getElementById("ip").value;
    // Wert aus dem Select-Feld lesen
    const prefix = parseInt(document.getElementById("prefix").value);
    const countnet = parseInt(document.getElementById("countnet").value);
    const output = document.getElementById("output");
    const subnetsContainer = document.getElementById("subnets-container");

    // Bestehende Ergebnisse und die "results" Box zurücksetzen
    subnetsContainer.innerHTML = "";
    output.classList.remove("show");
    output.classList.add("hidden"); // Stelle sicher, dass es beim Zurücksetzen auch hidden wird

    // Einfache Validierung (könnte je nach Bedarf erweitert werden)
    if (!ip || !/^\d{1,3}(\.\d{1,3}){3}$/.test(ip) || ip.split('.').some(part => parseInt(part) > 255)) {
      alert("Bitte eine gültige IPv4-Adresse eingeben (z.B. 192.168.0.0).");
      return;
    }
    // Da das Select nur 8, 16, 24 anbietet, ist die Prefix-Validierung weniger kritisch,
    // aber wir können prüfen, ob ein Wert ausgewählt wurde (parseInt gibt NaN für leere Selects zurück)
    if (isNaN(prefix)) {
        alert("Bitte wählen Sie eine gültige Präfixlänge aus.");
        return;
    }

    if (isNaN(countnet) || countnet < 1) {
      alert("Bitte eine Anzahl von Subnetzen von mindestens 1 eingeben.");
      return;
    }

    try {
      const res = await fetch("/api/symsubprefix", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ipv4: ip, prefix: prefix, countnet: countnet })
      });

      if (res.ok) {
        const data = await res.json();

        if (data.error) {
          alert("Fehler bei der Berechnung: " + data.error);
          return;
        }

        if (!data.subnets || data.subnets.length === 0) {
          alert("Es wurden keine Subnetze berechnet. Bitte Eingaben prüfen.");
          return;
        }

        data.subnets.forEach(subnet => {
          const subnetGroup = document.createElement("div");
          subnetGroup.classList.add("subnet-group");

          const subnetTitle = document.createElement("h3");
          // Zeigt das ursprüngliche Präfix und das neue Subnetz-Präfix an, falls unterschiedlich
          subnetTitle.textContent = `Subnetz ${subnet.subnet_number} (${subnet.prefix_length})`;
          subnetGroup.appendChild(subnetTitle);

          const createResultItem = (label, value) => {
            const div = document.createElement("div");
            div.classList.add("result-item");
            const labelElem = document.createElement("label");
            labelElem.textContent = label + ":";
            const spanElem = document.createElement("span");
            spanElem.textContent = value;
            div.appendChild(labelElem);
            div.appendChild(spanElem);
            return div;
          };

          subnetGroup.appendChild(createResultItem("Netzwerkadresse", subnet.network_address));
          subnetGroup.appendChild(createResultItem("Broadcastadresse", subnet.broadcast_address));
          subnetGroup.appendChild(createResultItem("Erster Host", subnet.first_host));
          subnetGroup.appendChild(createResultItem("Letzter Host", subnet.last_host));
          subnetGroup.appendChild(createResultItem("Nutzbare Hosts", subnet.usable_hosts));
          subnetGroup.appendChild(createResultItem("Subnetzmaske", subnet.subnet_mask));

          subnetsContainer.appendChild(subnetGroup);
        });

        output.classList.remove("hidden");
        output.classList.add("show");
      } else {
        const errorText = await res.text();
        alert(`Fehler bei der Serveranfrage: ${res.status} ${res.statusText}\nDetails: ${errorText}`);
      }
    } catch (error) {
      console.error("Fehler beim Fetch-Vorgang:", error);
      alert("Es ist ein unerwarteter Fehler aufgetreten. Bitte versuchen Sie es später erneut.");
    }
  }
</script>
{% endblock %}