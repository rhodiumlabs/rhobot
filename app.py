#!/usr/bin/env python

import urllib
import json
import os
import sendgrid
from sets import Set
from sendgrid.helpers.mail import *

from flask import Flask
from flask import request
from flask import make_response

rhodium_email = 'hello@rhodium.io'

# Flask app should start in global layout
app = Flask(__name__)



@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    res = processRequest(req)

    res = json.dumps(res, indent=4)

    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r



def processRequest(req):
    if req["result"]["action"] == "rhobot-email":
        email_query = send_email(req)
        if email_query is None:
            return {}
        data = email_query
        res = makeEmailWebhookResult(data)
        return res
    elif req["result"]["action"] == "team-expertise":
        res = makeExpertiseWebhookResult(req)
        return res
    else:
        return {}

def send_email(req):
    result = req["result"]
    parameters = result["parameters"]
    #rhobot_name = parameters["user_name"]
    rhobot_subject = parameters["subject"]
    rhobot_email = parameters["from_email"]
    rhobot_message = parameters["message"]
    sg = sendgrid.SendGridAPIClient(apikey= os.environ['SENDGRID_API_KEY'])

    from_email = Email(rhobot_email)
    subject = rhobot_subject
    to_email = Email(rhodium_email)
    content = Content("text/plain", rhobot_message)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)

    print(response.status_code)
    print(response.body)
    print(response.headers)
    return result

def makeExpertiseWebhookResult(req):
    result = req["result"]
    parameters = result["parameters"]
    expertise = parameters["expertise"]
    experts = findExperts(experts)
    speech = "The following team members know about " + expertise + ": " + experts

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        "data": req,
        "contextOut": [],
        "source": "team-expertise"
    }

def findExperts(expertise):
    engineers = {}
    engineers.setdefault('engineer', []).append('Ari Ramdial')
    engineers.setdefault('engineer', []).append('Alex Daskalov')
    experts = ''.join(str(e) for e in engineers[expertise])
    return experts

def makeEmailWebhookResult(data):
    speech = "I sent an email to " + rhodium_email + "! "

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        "data": data,
        "contextOut": [],
        "source": "rhobot-email"
    }



if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=False, port=port, host='0.0.0.0')
