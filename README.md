# Rev3rse Security Lab 2022

in questo repository troverai informazioni utili, script e soluzioni utili durante il laboratorio.

Ogni partecipante avrà a disposizione:
- Accesso alla console web di AWS con username e password
- Un'istanza ec2 che ospita il sito e-commerce che dovrà proteggere
- Un bilanciatore che espone il sito e-commerce
- Un target-group che mette in comunicazione il bilanciatore e l'istanza ec2
- Un editor VSCode online utilizzabile tramite browser

## Bilanciatore AWS

Il bilanciatore di AWS che useremo si chiama "**E**lastic **L**oad **B**alancer" e ci si riferisce a questa tipologia di bilanciatore con `elbv2`. Ogni partecipante al lab avrà il suo bilanciatore dedicato.

Ogni istanza `elbv2` ha al suo interno uno o più "listener" che, in breve, rappresentano la porta su cui è in ascolto (per tutti sarà `TCP/80`) e le regole attive che gestiscono il comportamento del bilanciatore. Ad esempio, alcune regole possono fare semplicemente forward verso un webserver (tramite il target-group), oppure possono inviare "fixed response" con uno specifico contenuto.

Il target-group è ciò che mette in comunicazione il bilanciatore con l'istanza su cui è ospitato il nostro e-commerce. Ogni target-group può avere più istanze registrate al suo interno (nel nostro caso sarà un'unica istanza).

## Aggiungere regola al bilanciatore (fixed response set cookie)

Questa regola di esempio ha una condizione, un'azione e la priorità.

La condizione verifica se il request header host corrisponde al nostro sito.

L'azione risponde con una "fixed response" con una piccola pagina HTML.

La priorità stabilisce l'ordine con cui la regola verrà eseguita.

```python
import boto3

client = boto3.client('elbv2')

response = client.create_rule(
    ListenerArn=listener_arn,
    Conditions=[
        {
            "Field": "host-header",
            "Values": [
                "00.lab.be3rse.com"
            ]
        }
    ],
    Actions=[
        {
            "Type": "fixed-response",
            "Order": 1,
            "FixedResponseConfig": {
                "MessageBody": f"<h1>Hello, World!</h1>",
                "StatusCode": "200",
                "ContentType": "text/html"
            }
        }
    ],
    Priority=(102),
)
```

## CloudWatch

AWS CloudWatch è un potente strumento che ci permette di gestire eventi, metriche, log, e di poter inviare alert a una o più componenti di AWS (inviare un messaggio e-mail, eseguire una funzione, ecc...). Useremo AWS CloudWatch per generare allarmi e creare un automatismo per mitigare un attacco volumetrico DoS layer 7 verso il nostro e-commerce.

Un esempio di allarme che riceverà la nostra funzione è:
```json
{
    "Records": [
        {
            "Sns": {
                "Message": "{\"NewStateValue\":\"ALARM\"}"
            }
        }
    ]
}
```

## Lambda

Faremo in modo che CloudWatch capisca che è in corso un attacco DoS verso il nostro e-commerce, e automaticamente esegua una funzione python che creerà due regole sul bilanciatore per mitigare l'attacco.

Un esempio di lambda function è:

```python
import json, boto3

def lambda_handler(event, context):
    client = boto3.client("elbv2")
    # ...
    print("Hello, World!")
    # ...
```

## boto3

per mettere in comunicazione la lambda function con il bilanciatore, useremo un modulo python chiamato `boto3` che è un SDK che permette di creare, configurare, e gestire servizi AWS come, appunto, `elbv2`.

https://boto3.amazonaws.com/v1/documentation/api/latest/index.html

## ARN

Usando boto3 dovremo far riferimento ad alcuni nostri "asset" come, ad esempio, il nostro listener sul bilanciatore o il nostro target-group. Per farlo, useremo i relativi Amazon Resource Name (ARN) che non sono altro che "id" univoci che identificano una risorsa/servizio sul nostro cloud.

Un esempio di ARN di un listener del bilanciatore è:
```
arn:aws:elasticloadbalancing:eu-central-1:242136087624:listener/app/loadbalancer-01/098affb0f88fa97c/b90394976ba4a458
```

Un esempio di ARN di un target-group è:
```
arn:aws:elasticloadbalancing:eu-central-1:242136087624:targetgroup/tg-01/2d831d687e44e373
```