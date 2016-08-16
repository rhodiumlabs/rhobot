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



@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    res = processRequest(req)

    res = json.dumps(res, indent=4)

    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r



def processRequest(req):
    if req["result"]["action"] != "rhobot-email":
        return {}

    email_query = send_simple_message(req)
    if email_query is None:
        return {}
    import pdb; pdb.set_trace()
    data = email_query
    res = makeWebhookResult(data)
    return res





def send_simple_message(req):
    result = req["result"]
    parameters = result["parameters"]
    rhobot_name = parameters["user_name"]
    rhobot_email = parameters["from_email"]
    rhobot_message = parameters["message"]
    sg = sendgrid.SendGridAPIClient(apikey='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')
    from_email = Email(rhobot_email)
    subject = "A message from " + rhobot_name
    to_email = Email("hello@rhodium.io")
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

    app.run(debug=False, port=port, host='0.0.0.0')
