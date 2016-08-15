#!/usr/bin/env python

import urllib
import json
import os
import requests
#import pycurl
#import cStringIO



from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)



@app.route('/webhook', methods=['GET','POST'])
def webhook():
    #buf = cStringIO.StringIO()
    #c = pycurl.Curl()
    #c.setopt(c.HTTPHEADER, ['Authorization:Bearer 55e0b7af149a47a7b0646ad5c264cba4'])
    #c.setopt(c.URL, 'https://api.api.ai/api/query?v=20150910&query=jkjedkj&lang=en&sessionId=59a29603-4bed-4506-999c-6a73c13d4a73&timezone=America/Montreal')
    #c.setopt(c.WRITEFUNCTION, buf.write)
    #c.perform()

    #req =  json.loads(buf.getvalue())
    #buf.close()

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



def send_simple_message(req):
    result = req.get("result")
    contexts = result.get("contexts")
    parameters = contexts.get("parameters")

    name = parameters.get("name")
    email = parameters.get("from_email")
    message = parameters.get("message")
    print message
    return requests.post(
        "https://api.mailgun.net/v3/sandboxee25071432c844e08c28e9438f9f8986.mailgun.org/messages",
        auth=("api", "key-bece1656953b819fbe56fc0e5f22a0d2"),
        data={"from": email,
              "to": ["bar@example.com", "postmaster@sandboxee25071432c844e08c28e9438f9f8986.mailgun.org"],
              "subject": "Rho",
              "text": message})

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
        # "contextOut": [],
        "source": "rhobot-email"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=True, port=port, host='0.0.0.0')
