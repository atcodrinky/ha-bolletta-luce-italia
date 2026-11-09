# Bolletta Luce Italia

Integrazione personalizzata per Home Assistant dedicata alla stima, al controllo e all’archiviazione della bolletta elettrica italiana.

> Stato del progetto: fase di progettazione. Non è ancora disponibile una versione installabile.

## Obiettivi

- Calcolare la bolletta mensile partendo dai consumi nelle fasce F1, F2 e F3.
- Supportare tariffe fisse e indicizzate al PUN Index GME.
- Gestire perdite di rete, spread, CdispD, commercializzazione, trasporto, potenza, oneri, accise, IVA e canone RAI.
- Aggiornare automaticamente i corrispettivi regolati pubblicati da ARERA, mantenendo la possibilità di correzione manuale.
- Conservare un archivio mensile con tariffe, consumi, dettaglio dei costi, bolletta reale e scostamento dalla stima.
- Permettere la modifica di contratto e sorgenti tramite l’interfaccia di Home Assistant, senza ricreare l’integrazione.

## Principi di migrazione

I sensori storici delle fasce restano sorgenti esterne permanenti e non saranno modificati:

- `sensor.energia_acquistata_fasce_f1`
- `sensor.energia_acquistata_fasce_f2`
- `sensor.energia_acquistata_fasce_f3`

L’integrazione non eliminerà automaticamente helper, sensori template o altre entità esistenti. La loro eventuale rimozione resterà una decisione e un’operazione manuale dell’utente, dopo un periodo di confronto fra vecchio e nuovo calcolo.

## Configurazione prevista

La configurazione avverrà interamente dall’interfaccia di Home Assistant e comprenderà:

- sorgenti dei consumi F1, F2 e F3;
- sorgenti dei prezzi PUN;
- fattore manuale di correzione del misuratore;
- dati contrattuali e potenza impegnata;
- componenti tariffarie e fiscali;
- modalità automatica, da entità o manuale per il CdispD;
- calendario e rate del canone RAI;
- registrazione dei consuntivi reali.

Le modifiche tariffarie saranno versionate con data di decorrenza e non altereranno i mesi già chiusi.

## Versionamento

Il progetto utilizza il versionamento semantico `MAJOR.MINOR.PATCH`:

- `MAJOR`: modifiche incompatibili o migrazioni obbligatorie;
- `MINOR`: nuove funzionalità compatibili;
- `PATCH`: correzioni compatibili e manutenzione.

Durante lo sviluppo iniziale saranno utilizzate versioni `0.y.z`. Le versioni pubblicate saranno identificate da tag nel formato `vMAJOR.MINOR.PATCH`, per esempio `v0.1.0` e `v1.0.0`. Le eventuali versioni preliminari useranno suffissi come `-alpha.1`, `-beta.1` e `-rc.1`.

## Lingua

README, documentazione e testi destinati all’utente saranno mantenuti in italiano.
