# Registro delle modifiche

Tutte le modifiche rilevanti di Bolletta Luce Italia sono documentate in questo file.

Il progetto usa il versionamento semantico e i tag nel formato `vMAJOR.MINOR.PATCH`.

## [0.2.2] - 2026-11-10

### Corretto

- Risolto l'errore durante l'apertura della seconda pagina del config flow.
- Sostituito il passo numerico non supportato con la precisione libera prevista da Home Assistant, mantenendo l'inserimento di valori tariffari con più di tre decimali.

## [0.2.1] - 2026-11-10

### Aggiunto

- Icona brand locale a 256×256 pixel e versione ad alta risoluzione a 512×512 pixel per Home Assistant.

### Corretto

- Aumentata a sei decimali la precisione dei campi tariffari espressi in €/kWh: prezzi fissi, spread, distribuzione, oneri di sistema, CdispD e accisa.

## [0.2.0] - 2026-11-10

### Aggiunto

- Configurazione iniziale suddivisa in cinque pagine.
- Contatore della pagina nei titoli del wizard.
- Comando per tornare alla pagina precedente conservando i valori inseriti.
- Options Flow multipagina con applicazione immediata senza riavviare Home Assistant.
- Controllo automatico che impedisce di pubblicare una versione assente dal registro delle modifiche.

### Modificato

- Raggruppati i campi in sorgenti energia, tariffa, rete e quote fisse, imposte e ricarica auto.
- Migliorate le descrizioni italiane dei passaggi.
- La ricarica dell'auto rimane completamente opzionale.

## [0.1.1] - 2026-11-10

### Corretto

- Risolto l'errore `400: Bad Request` del config flow su Home Assistant 2026.11.
- Adeguato il passo minimo dei campi numerici ai requisiti di Home Assistant.

## [0.1.0] - 2026-11-10

### Aggiunto

- Prima versione installabile di Bolletta Luce Italia.
- Calcolo per tariffa indicizzata al PUN o prezzo fisso, con fasce F1, F2 e F3.
- Componenti di rete, oneri, CdispD, quote fisse, accisa, IVA e canone RAI.
- Archivio mensile interno e inserimento manuale delle bollette reali.
- Ripartizione opzionale dei consumi della wallbox tra rete e fotovoltaico.
- Options Flow con ricarica della sola integrazione.
