# iSAQB GREEN - Green Metrics Tool

Dieser GitHub Codespace dient zur Ausführung von Energiemessungen mithilfe des Green Metric Tools.

Bei einem GitHub Codespace handelt es sich um eine virtuelle Serverinstanz, so dass die Ergebnisse zwischen Messdurchläufen sich unterscheiden können. Für repräsentative Energiemessungen ist eine Umgebung wie diese hier somit ungeeignet.

Im Rahmen des iSAQB GREEN-Kurses verwenden wir trotzdem GitHub Codespaces, um Ihnen eine einfach nutzbare Umgebung ohne Installationsaufwand bereitstellen zu können.

## Einrichtung

Für die Einrichtung vom Green Metrics Tool führen Sie bitte folgenden Befehl aus:

```sh
bash .devcontainer/isaqb-green/codespace-setup.sh
```

Die Ausführung des Skripts benötigt etwa 3 Minuten.

## Erste simple Energiemessung

Für eine erste kurze Energiemessung führe den folgenden Befehl aus:

```sh
python3 runner.py --name "Simple Test" --uri "/workspaces/green-metrics-tool/example-applications/" --filename "stress/usage_scenario.yml" --skip-system-checks --dev-no-optimizations --dev-no-build
```

`runner.py` ist ein Bestandteil vom Green Metrics Tool, welches für die Koordination des gesamten Ablaufs einer Messung zuständig ist. In diesem Beispiel wird das Nutzungsszenario `stress/usage_scenario.yml` im lokalen Repository `/workspaces/green-metrics-tool/example-applications` genutzt. Das Nutzungsszenario führt das Linux `stress`-Kommando für 5 Sekunden aus, was die CPU zu 100 % auslastet.

Das Frontend vom Green Metrics Tool mit den Messergebnissen lässt sich wie folgt aufrufen:

- Tab "Ports" öffnen
- Addresse mit dem Port "9143" öffnen

## Spring REST Football - Vergleich Modulith vs. Microservices

Nun möchten wir eine realistischere Anwendung untersuchen.
Hierfür nutzen wir eine Spring Boot Demoapplikation, bereitgestellt in zwei Varianten, die wir in Bezug auf ihren Energieverbrauch in einem Lastszenario miteinander vergleichen möchten:

- [spring-rest-football-modulith](https://gitlab.com/envite-consulting/sustainable-software-architecture/isaqb-green/spring-rest-football-modulith)
- [spring-rest-football-services](https://gitlab.com/envite-consulting/sustainable-software-architecture/isaqb-green/spring-rest-football-services)

Modulith:

```sh
python3 runner.py --name "Modulith" --uri "https://gitlab.com/envite-consulting/sustainable-software-architecture/isaqb-green/spring-rest-football-modulith" --filename "usage_scenario-artillery.yml" --skip-system-checks --dev-no-build --skip-unsafe
```

Microservices:

```sh
python3 runner.py --name "Microservices" --uri "https://gitlab.com/envite-consulting/sustainable-software-architecture/isaqb-green/spring-rest-football-services" --filename "usage_scenario-artillery.yml" --skip-system-checks --dev-no-build --skip-unsafe
```
