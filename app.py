#!/usr/bin/env python

import urllib
import json
import os
import requests
import sendgrid
import os
from sendgrid.helpers.mail import *

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)



@app.route('/webhook', methods=['GET','POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)

    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r



def processRequest(req):
    if req.get("result").get("action") != "rhobot-email":
        return {}
    email_query = send_simple_message(req)
    if email_query is None:
        return {}
    data = json.loads(email_query)
    res = makeWebhookResult(data)
    return res



sg = sendgrid.SendGridAPIClient(apikey='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')
from_email = Email("test@example.com")
subject = "Hello World from the SendGrid Python Library!"
to_email = Email("test@example.com")
content = Content("text/plain", "Hello, Email!")
mail = Mail(from_email, subject, to_email, content)
response = sg.client.mail.send.post(request_body=mail.get())

print(response.status_code)
print(response.body)
print(response.headers)

def send_simple_message(req):
    result = req.get("result")
    contexts = result.get("contexts")
    parameters = contexts.get("parameters")
    name = parameters.get("name")
    email = parameters.get("from_email")
    message = parameters.get("message")
    print message

def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))

    speech = "Today in " + location.get('city') + ": " + condition.get('text') + \
             ", the temperature is " + condition.get('temp') + " " + units.get('temperature')

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

    app.run(debug=True, port=port, host='0.0.0.0')
