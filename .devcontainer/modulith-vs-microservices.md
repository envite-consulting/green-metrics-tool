
# Vergleich Modulith vs. Microservices

Die Football-Demoapplikation existiert in zwei Varianten, die wir in Bezug auf ihren Energieverbrauch in einem Lastszenario miteinander vergleichen möchten:

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

Energiemessung Microservices (entspricht dem Befehl für 'Energiemessung System unter Last'):

```sh
python3 runner.py --name "Spring REST Football - Microservices (Load Test)" --uri "https://gitlab.com/envite-consulting/sustainable-software-architecture/isaqb-green/spring-rest-football-services" --filename "usage_scenario-load.yml" --skip-system-checks --skip-unsafe --measurement-baseline-duration=5 --measurement-idle-duration=5
```

Die Ergebnisse lassen sich wieder im GMT-Frontend betrachten.
