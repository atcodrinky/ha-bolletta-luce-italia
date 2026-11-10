# Bolletta Luce Italia

Bolletta Luce Italia è un'integrazione personalizzata per Home Assistant che stima e archivia la bolletta elettrica italiana partendo dai consumi mensili F1, F2 e F3.

La versione 0.1.0 è una prima versione installabile e verificabile in parallelo ai sensori template esistenti.

[![Apri nel Marketplace di Home Assistant](https://my.home-assistant.io/badges/marketplace_repository.svg)](https://my.home-assistant.io/redirect/marketplace_repository/?owner=atcodrinky&repository=ha-bolletta-luce-italia&category=integration)


## Funzioni disponibili

- tariffa indicizzata al PUN oppure prezzo fisso;
- tre fasce F1, F2 e F3;
- fattore manuale di correzione dei consumi;
- perdite di rete e spread separati per fascia;
- CdispD, distribuzione, oneri di sistema, quote fisse e quota potenza;
- accise, IVA e dieci rate configurabili del canone RAI;
- stima totale, dettaglio delle singole voci e costo medio effettivo;
- archivio mensile nello storage interno di Home Assistant;
- inserimento manuale di consumi e totale delle bollette reali;
- ripartizione opzionale della ricarica auto fra rete e fotovoltaico;
- attribuzione opzionale e proporzionale delle quote fisse all'auto;
- modifica di tutte le opzioni senza riavviare Home Assistant.

## Sensori da conservare

L'integrazione usa come sorgenti esterne e non modifica i sensori storici:

- sensor.energia_acquistata_fasce_f1
- sensor.energia_acquistata_fasce_f2
- sensor.energia_acquistata_fasce_f3

Questi sensori, il relativo misuratore di utilità e lo storico della Dashboard Energia devono rimanere attivi. Gli helper usati per i vecchi calcoli possono restare durante il confronto e possono essere eliminati manualmente in seguito.

## Installazione manuale

1. Copiare la cartella custom_components/bolletta_luce_italia nella cartella custom_components della propria installazione Home Assistant.
2. Riavviare Home Assistant soltanto per il primo caricamento del codice.
3. Aprire Impostazioni, Dispositivi e servizi, Aggiungi integrazione.
4. Cercare Bolletta Luce Italia.

È possibile aggiungere questo repository anche come repository personalizzato di tipo Integrazione nel Marketplace di Home Assistant.

## Configurazione consigliata per Octopus

Per il contratto usato durante lo sviluppo:

- modello tariffario: indicizzato;
- sensori energia: i tre sensori storici F1, F2 e F3;
- sensori PUN: sensor.pun_fascia_f1, sensor.pun_fascia_f2 e sensor.pun_fascia_f3;
- fattore perdite di rete: 1,10;
- spread F1, F2 e F3: 0,0088 €/kWh;
- quota fissa vendita: 72 €/anno;
- accisa: 0,0227 €/kWh;
- IVA: 10%;
- canone RAI: 90 €/anno in 10 rate.

Le altre componenti devono essere copiate dalla bolletta o dai valori ARERA applicabili al periodo. Il fattore di correzione può essere modificato in qualsiasi momento dalle opzioni dell'integrazione.

## Calcolo

Per una tariffa indicizzata il prezzo di ogni fascia è:

    prezzo fascia = PUN fascia × fattore perdite + spread fascia

La stima mensile somma:

    materia energia
    + CdispD
    + distribuzione e oneri variabili
    + quote fisse e quota potenza
    + accise
    + IVA
    + canone RAI

I valori sono arrotondati per l'esposizione dei sensori; il calcolo interno usa i valori non arrotondati.

## Ricarica auto opzionale

La funzione è disattivata per impostazione predefinita. Quando viene attivata sono richiesti almeno i kWh mensili della wallbox prelevati dalla rete. I kWh da fotovoltaico sono facoltativi e informativi.

Nel sistema di riferimento si possono usare:

- sensor.wallbox_rete_mese
- sensor.wallbox_fv_mese

Le quote fisse non vengono attribuite all'auto salvo attivazione dell'opzione dedicata.

## Inserimento delle bollette reali

Il servizio bolletta_luce_italia.registra_bolletta accetta:

- entry_id: identificativo della configurazione;
- month: mese nel formato AAAA-MM;
- energy: consumi fatturati in kWh;
- total: totale reale in euro.

Questo consente di inserire anche i consuntivi da gennaio a ottobre senza dipendere dallo storico dei vecchi helper. Un valore già presente per lo stesso mese viene sostituito.

Il servizio bolletta_luce_italia.archivia_mese salva manualmente la fotografia corrente del calcolo. Il passaggio a un nuovo mese archivia inoltre automaticamente l'ultima fotografia mantenuta in memoria.

## Opzioni e applicazione immediata

Aprire l'integrazione e scegliere Configura. Il pulsante Salva applica i nuovi valori ricaricando soltanto Bolletta Luce Italia: non è necessario riavviare Home Assistant e non occorre eliminare o ricreare la configurazione.

## Limiti della versione 0.1.0

- CdispD e componenti ARERA sono inseriti manualmente.
- L'importazione automatica da fonti ufficiali ARERA sarà aggiunta dopo la validazione dei calcoli della prima versione.
- L'archivio non importa automaticamente lo storico dei vecchi helper; i consuntivi reali possono però essere inseriti con il servizio dedicato.
- L'integrazione è progettata esclusivamente per forniture elettriche italiane domestiche.

## Versionamento

Il progetto usa il versionamento semantico. Le versioni pubblicate sono identificate da tag nel formato vMAJOR.MINOR.PATCH.

## Licenza

Distribuito con licenza MIT.
