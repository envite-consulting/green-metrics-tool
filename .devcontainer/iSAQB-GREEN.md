# iSAQB GREEN - Green Metrics Tool

Dieser GitHub Codespace dient zur Ausführung von Energiemessungen mithilfe vom Green Metrics Tool (GMT).

Bei einem GitHub Codespace handelt es sich um eine virtuelle Serverinstanz, so dass die Ergebnisse zwischen Messdurchläufen sich unterscheiden können. Für repräsentative Energiemessungen ist eine Umgebung wie diese hier somit ungeeignet.

Im Rahmen des iSAQB GREEN-Kurses verwenden wir trotzdem GitHub Codespaces, um Ihnen eine einfach nutzbare Umgebung ohne Installationsaufwand bereitstellen zu können.

## Einrichtung

Führen Sie bitte zunächst folgenden Befehl im Terminal aus:

```sh
bash .devcontainer/codespace-setup.sh
```

Die Ausführung des Skripts benötigt etwa 5 Minuten. Es werden das Green Metrics Tool inkl. aller Abhängigkeiten installiert sowie weitere Konfigurationsanpassungen vorgenommen, die zur Ausführung innerhalb von GitHub Codespaces nötig sind.

Führen Sie anschließend noch folgenden Befehl im Terminal aus (aktiviert eine virtuelle Umgebung für Python, was für die Ausführung von GMT benötigt wird):

```sh
source venv/bin/activate
```

## Erste simple Energiemessung

Für eine erste kurze Energiemessung kann folgender Befehl genutzt werden:

```sh
python3 runner.py --name "Simple Stress Test" --uri "/workspaces/green-metrics-tool/example-applications/" --filename "stress/usage_scenario.yml" --skip-system-checks --measurement-baseline-duration=5 --measurement-idle-duration=5
```

`runner.py` ist ein Bestandteil vom Green Metrics Tool, welches für die Koordination des gesamten Ablaufs einer Messung zuständig ist. Hier wird das Nutzungsszenario `stress/usage_scenario.yml` aus dem lokalen Repository `/workspaces/green-metrics-tool/example-applications` genutzt. Das Nutzungsszenario führt das Linux `stress`-Kommando für 5 Sekunden aus, was einen CPU-Kern stark auslastet.

Wir verwenden hier die Flags `--measurement-baseline-duration=5` und `--measurement-idle-duration=5`, um die Wartezeit vor der Baseline- und Idle-Messung zu verkürzen. Der Default-Wert beträgt jeweils 60 s. Bei realen Energiemessungen ist es wichtig, solche Pausen einzubauen, um der Maschine Zeit zu geben, sich abzukühlen.

Sobald die Messung beendet ist, wird im Terminal ein Link angezeigt. Dieser kann mit Strg+Klick geöffnet werden. Die Seite mit den Messergebnissen öffnet sich in einem neuen Tab.

Die Meldung "You are about to access a development port served by someone's codespace" per Klick auf "Continue" akzeptieren.

Alternativ lässt sich das Frontend vom Green Metrics Tool wie folgt aufrufen:

- Tab "Ports" öffnen
- Adresse mit dem Port "9143" öffnen (öffnet sich in einem neuen Tab)

## Spring REST Football

Nun möchten wir eine realistischere Anwendung untersuchen.
Hierfür nutzen wir eine von uns vorbereitete Spring Boot Demoapplikation namens "Spring REST Football":
[spring-rest-football-services](https://gitlab.com/envite-consulting/sustainable-software-architecture/isaqb-green/spring-rest-football-services)

Die Anwendung besteht aus zwei Microservices, die Informationen zu Fußball-Spielern und –Clubs bereitstellt.
Es werden folgende API-Endpunkte bereitgestellt:

- Club-Service:
  - `/clubs/<id>`
  - `/clubs?namePart=<name>`
- Player-Service:
  - `/players/<id>`
  - `/players?section=<section>`

Spielerinformationen beinhalten Informationen zum Club. Um diese Informationen zu bekommen, fragt der Player-Service den Club-Service an.

### Vergleich Endpunkte

Hier möchten wir den Energieverbrauch der vier bereitgestellten Endpunkte vergleichen:

```sh
python3 runner.py --name "Spring REST Football - Microservices (APIs)" --uri "https://gitlab.com/envite-consulting/sustainable-software-architecture/isaqb-green/spring-rest-football-services" --filename "usage_scenario-all-endpoints.yml" --skip-system-checks --skip-unsafe --measurement-baseline-duration=5 --measurement-idle-duration=5
```

*Hinweis: Die Energiemessung wird hier mit "kalten" JVMs durchgeführt, d.h. die Applikationen in der Laufzeitumgebung wurden noch nicht just-in-time optimiert.*

### System unter Last

Nur einzelne Anfragen zu messen kann zu Schwankungen führen. Für Regressionstests ist es i.d.R. ratsam, das System unter Last zu setzen.

Als Lastgenerator nutzen wir [Artillery](https://www.artillery.io/). Das Lastszenario ist in den Repositories jeweils in den Dateien `client/artillery_gmt_warm_up.yml` und `client/artillery_gmt_load.yml` definiert.

Energiemessung System unter Last:

```sh
python3 runner.py --name "Spring REST Football - Microservices (Load Test)" --uri "https://gitlab.com/envite-consulting/sustainable-software-architecture/isaqb-green/spring-rest-football-services" --filename "usage_scenario-load.yml" --skip-system-checks --skip-unsafe --measurement-baseline-duration=5 --measurement-idle-duration=5
```

---

### Vergleich Modulith vs. Microservices

*Hier geht es weiter in Kapitel 6 "Softwarearchitektur"...*

Die Demoapplikation existiert in zwei Varianten, die wir in Bezug auf ihren Energieverbrauch in einem Lastszenario miteinander vergleichen möchten:

- [spring-rest-football-modulith](https://gitlab.com/envite-consulting/sustainable-software-architecture/isaqb-green/spring-rest-football-modulith)
- [spring-rest-football-services](https://gitlab.com/envite-consulting/sustainable-software-architecture/isaqb-green/spring-rest-football-services)

Als Lastgenerator nutzen wir [Artillery](https://www.artillery.io/). Das Lastszenario ist in den Repositories jeweils in den Dateien `client/artillery_gmt_warm_up.yml` und `client/artillery_gmt_load.yml` definiert.

Bevor die Energiemessung gestartet werden kann, stellen Sie sicher, dass die virtuelle Umgebung für Python im Terminal aktiviert ist:

```sh
source venv/bin/activate
```

Energiemessung Modulith:

```sh
python3 runner.py --name "Spring REST Football - Modulith (Load Test)" --uri "https://gitlab.com/envite-consulting/sustainable-software-architecture/isaqb-green/spring-rest-football-modulith" --filename "usage_scenario-load.yml" --skip-system-checks --skip-unsafe --measurement-baseline-duration=5 --measurement-idle-duration=5
```

Energiemessung Microservices (entspricht dem Befehl von oben für 'Energiemessung System unter Last'):

```sh
python3 runner.py --name "Spring REST Football - Microservices (Load Test)" --uri "https://gitlab.com/envite-consulting/sustainable-software-architecture/isaqb-green/spring-rest-football-services" --filename "usage_scenario-load.yml" --skip-system-checks --skip-unsafe --measurement-baseline-duration=5 --measurement-idle-duration=5
```

Die Ergebnisse lassen sich wieder im GMT-Frontend betrachten.
