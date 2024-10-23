# iSAQB GREEN - Green Metrics Tool

Dieser Gitpod dient zur Ausführung von Energiemessungen mithilfe des Green Metric Tools (GMT).

Bei einem Gitpod handelt es sich um eine virtuelle Serverinstanz, so dass die Ergebnisse zwischen Messdurchläufen sich unterscheiden können. Für repräsentative Energiemessungen ist eine Umgebung wie diese hier somit ungeeignet.

Im Rahmen des iSAQB GREEN-Kurses verwenden wir trotzdem Gitpod, um Ihnen eine einfach nutzbare Umgebung ohne Installationsaufwand bereitstellen zu können.

## Einrichtung

Führen Sie bitte zunächst folgenden Befehl aus:

Die Ausführung des Skripts benötigt etwas Zeit. Es werden das Green Metrics Tool inkl. aller Abhängigkeiten installiert sowie weitere Konfigurationsanpassungen vorgenommen, die aufgrund von Gitpod nötig sind.

Führen Sie anschließend noch folgenden Befehl aus (aktiviert eine virtuelle Umgebung für Python):

```sh
source venv/bin/activate
```

## Erste simple Energiemessung

Für eine erste kurze Energiemessung kann folgender Befehl genutzt werden:

```sh
python3 runner.py --name "Simple Stress Test" --uri "$(pwd)/example-applications/" --filename "stress/usage_scenario.yml" --skip-system-checks --dev-no-optimizations
```

`runner.py` ist ein Bestandteil vom Green Metrics Tool, welches für die Koordination des gesamten Ablaufs einer Messung zuständig ist. Hier wird das Nutzungsszenario `stress/usage_scenario.yml` aus dem lokalen Repository `example-applications` genutzt. Das Nutzungsszenario führt das Linux `stress`-Kommando für 5 Sekunden aus, was die CPU stark auslastet.

Das Frontend vom Green Metrics Tool mit den Messergebnissen lässt sich wie folgt aufrufen:

- Tab "Ports" öffnen
- Adresse mit dem Port "9143" öffnen (öffnet sich in einem neuen Tab)

## Spring REST Football - Vergleich Modulith vs. Microservices

Nun möchten wir eine realistischere Anwendung untersuchen.
Hierfür nutzen wir eine von uns vorbereitete Spring Boot Demoapplikation in zwei Varianten, die wir in Bezug auf ihren Energieverbrauch in einem Lastszenario miteinander vergleichen möchten:

- [spring-rest-football-modulith](https://gitlab.com/envite-consulting/sustainable-software-architecture/isaqb-green/spring-rest-football-modulith)
- [spring-rest-football-services](https://gitlab.com/envite-consulting/sustainable-software-architecture/isaqb-green/spring-rest-football-services)

Energiemessung Modulith:

```sh
python3 runner.py --name "Modulith" --uri "https://gitlab.com/envite-consulting/sustainable-software-architecture/isaqb-green/spring-rest-football-modulith" --filename "usage_scenario-load+single.yml" --skip-system-checks --dev-no-optimizations --skip-unsafe
```

Energiemessung Microservices:

```sh
python3 runner.py --name "Microservices" --uri "https://gitlab.com/envite-consulting/sustainable-software-architecture/isaqb-green/spring-rest-football-services" --filename "usage_scenario-load+single.yml" --skip-system-checks --dev-no-optimizations --skip-unsafe
```

Die Ergebnisse lassen sich wieder im GMT-Frontend betrachten (Tab wechseln bzw. im Tab "Ports" Adresse mit dem Port 9143 öffnen).
