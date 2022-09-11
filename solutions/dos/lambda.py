# soluzione per attacco DoS
# lambda function

import json, boto3, uuid

def lambda_handler(event, context):
    msg = json.loads(event["Records"][0]["Sns"]["Message"])

    # CHANGE THIS
    # ------------
    node_hostname = "01.lab.be3rse.com"
    listener_arn = "arn:aws:elasticloadbalancing:eu-central-1:242136087624:listener/app/loadbalancer-01/098affb0f88fa97c/b90394976ba4a458"
    targetgroup_arn = "arn:aws:elasticloadbalancing:eu-central-1:242136087624:targetgroup/tg-01/2d831d687e44e373"
    # ------------

    client = boto3.client(
        'elbv2'
    )
    
    if msg["NewStateValue"] == "ALARM":
        cookie_value = str(uuid.uuid4())
        cookie_jsfuck = cookie_value.replace("a","'+(![]+[])[+!+[]]+'")
        cookie_jsfuck = cookie_jsfuck.replace("1","'+[+!+[]]+[]+'")
        
        response = client.create_rule(
            ListenerArn=listener_arn,
            Conditions=[
                {
                    "Field": "http-header",
                    "HttpHeaderConfig": {
                        "HttpHeaderName": "Cookie",
                        "Values": [
                            f"*dosp={cookie_value}*"
                        ]
                    }
                },
                {
                    "Field": "host-header",
                    "Values": [
                        node_hostname,
                        f"temp.{node_hostname}"
                    ]
                }
            ],
            Actions=[
                {
                    "Type": "forward",
                    "TargetGroupArn": targetgroup_arn,
                    "Order": 1,
                    "ForwardConfig": {
                        "TargetGroups": [
                            {
                                "TargetGroupArn": targetgroup_arn,
                                "Weight": 1
                            }
                        ],
                        "TargetGroupStickinessConfig": {
                            "Enabled": False
                        }
                    }
                }
            ],
            Priority=(101),
        )
        
        response = client.create_rule(
            ListenerArn=listener_arn,
            Conditions=[
                {
                    "Field": "host-header",
                    "Values": [
                        node_hostname,
                        f"temp.{node_hostname}"
                    ]
                }
            ],
            Actions=[
                {
                    "Type": "fixed-response",
                    "Order": 1,
                    "FixedResponseConfig": {
                        "MessageBody": f"<script> document.cookie='dosp={cookie_jsfuck}'; location.reload(); </script>",
                        "StatusCode": "200",
                        "ContentType": "text/html"
                    }
                }
            ],
            Priority=(102),
        )
            
    else:
        print("Ok: Remove JS Challenge")
        response = client.describe_rules(ListenerArn=listener_arn)
        for rule in response["Rules"]:
            for c in rule["Conditions"]:
                if c["Field"] == "host-header":
                    if f"temp.{node_hostname}" in c["Values"]:
                        client.delete_rule(RuleArn=rule["RuleArn"])
   
