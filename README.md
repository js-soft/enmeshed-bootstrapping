# Demo / Anwendungsfall Kundenchatbot

```bash
uv sync              # Bootstrap Repo
docker compose up -d # Infrastruktur starten
./demo --help        # RTFM
```

# Tipps und Tricks

- Android: HTTP-only Setting muss gesetzt sein: https://developer.android.com/guide/topics/manifest/application-element#usesCleartextTraffic


# Braindump Use Cases Connector-Automatisierung

## Interaktive LLM-Integration

Bisher bietet die App keine Möglichkeit eines LLM als Chatbot. Wäre generell und für die Anwendungsfälle unten z.T. interessant. Reines Integrationsproblem.

- Streaming-Kanal für bidirektionale Kommunikation Client-LLM (hat Signal ähliches Problem? https://time.com/7346534/signal-confer-ai-moxie-marlinspike/ und https://confer.to/)

### AS1 - Message- / Mailbasiert

Automatische Beantwortung von Mails durch LLMs.

Keine Änderung der App, Connector oder Backbone notwendig. Durchstich mit Ollama auf localhost.

## Bootstrapping von Demos auf Basis einer Vorlage

Siehe Anwendungsfälle hier, die als Vorlage für einen Coding-Agenten genutzt werden könnten, der Anpassungen durchführen kann.

- Mit konkretem Anwendungsfall testen.

## Anfrage Freigabe medizinischer Daten für Forschungsprojekt

Unikliniken haben Bedarf an Patientendaten zur Auswertung von Forschungsprojekten. Hierfür muss aber eine Freigabe von den Patienten eingeholt werden. Existierende, proprietäre Lösung der Uniklinik HD geben Patienten einen QR-Code mit, mit dem ein Zugang zu einer Anwendunge freigegeben wird, mit dem die Klinik den Patienten zur Freigabe seiner Daten kontaktieren könnte.

Nachteil: proprietäre Lösung muss gesamten Tech- und Securitystack implementieren. Enmeshed bietet hier einen ready-to-use Kommunikationskanal.

Tool Calls
- Beantworten von Fragen zur Freigabe und Datenverarbeitung durch LLM (programmatische Guardrails für Korrektheit wegen Rechtssicherheit)

## Universitätsverwaltung: Agent LFS Studentenportal automatisieren

Student kann per Nachricht
- Dokumente abfragen, z.B. Immatrikulationsbescheide, ToR.
- sich zur Prüfung anmelden mit verpflichtender Bestätigung über Request

Naiver agentischer Anwendungsfall

## Integration: Dispatching von Nutzeranfragen oder -messages an zuständige Instanz oder Mitarbeiter

Ähnlich automatisierter Zustellung von Tickets.

## Kommunikationskanal für Nachfragen über Requests

Eingehende Requests, die für den Nutzer unklar sind, könnten durch ein LLM näher erläutert werden. Braucht LLM-Channel.
