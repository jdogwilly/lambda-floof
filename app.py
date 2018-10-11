import json
import os
import random
import sys
import requests
import logging
import xmltodict

# from aws_xray_sdk.core import xray_recorder
# from aws_xray_sdk.core import patch
# patch(["requests"])

logger = logging.getLogger()
logger.setLevel(logging.INFO)

#Lambda entry point. Filters out 
def handler(event, context):
  data = json.loads(event['body']) 
  logger.info('Recieved {}'.format(data))
  if data['name'] == os.getenv('BOT_NAME'):
    return {
      'statusCode': 200,
      'body': json.dumps({'status':'ok'}),
      'headers': {'Content-Type': 'application/json'}}

  send_message(get_res(data['text'].lower()))
  return {
    'statusCode': 200,
    'body': json.dumps({'status':'ok'}),
    'headers': {'Content-Type': 'application/json'}}

# Choose response based on keywords
# @xray_recorder.capture('get_res')
def get_res(text):
  # xray_recorder.begin_subsegment('get res')
  lis = []
  if 'dog' in text or 'pup' in text or 'good boy' in text or 'woof' in text:
    lis = [get_random('dog')]
  if 'cloud' in text or 'polar bear' in text:
    return get_res('samoyed')
  if 'cat' in text or 'meow' in text:
    lis = [get_cat()]
  if 'pitbull' in text or 'pit bull' in text:
    lis = ['https://www.thefamouspeople.com/profiles/images/og-pitbull-6049.jpg']
  if 'floof' in text:
    return get_res(random.choice(['leonberger', 'samoyed', 'stbernard']))
  if 'mop' in text:
    return get_res('komondor')
  else:
    breeds = json.loads(requests.get('https://dog.ceo/api/breeds/list').text)['message']
    switch = ''
    for breed in breeds:
      if breed in text:
        switch = ''
        subbreeds = json.loads(requests.get('https://dog.ceo/api/breed/' + breed + '/list').text)['message']
        for subbreed in subbreeds:
          if subbreed in text:
            switch = subbreed
        if switch != '':
          lis = [get_random(breed, switch)]
        else:
          lis = [get_random(breed)]
  return random.choice(lis)


# Send the chosen message to the chat
def send_message(msg):
  url  = 'https://api.groupme.com/v3/bots/post'
  data = {
          'bot_id' : os.getenv('GROUPME_BOT_ID'),
          'text'   : msg,
         }
  requests.post(url, data)
  
# Get random dog or cat
# @xray_recorder.capture('get_random')
def get_random(switch, subswitch = ''):
  # subsegment = xray_recorder.begin_subsegment('get_random')
  if (switch == 'dog'):
    link = 'https://dog.ceo/api/breeds/image/random'
    key = 'message'
  elif (switch == 'cat'):
    link = 'http://random.cat/meow'
    key = 'file'
  else:
    if subswitch == '': # just breed
      link = 'https://dog.ceo/api/breed/' + switch + '/images/random'
    else: # sub-breed
      link = 'https://dog.ceo/api/breed/' + switch + '/' + subswitch + '/images/random'
    key = 'message'
  html = requests.get(link).text
  data = json.loads(html)
  reto = data[key]
  reto.replace('\\/', '/')
  if reto.endswith('jpg') or reto.endswith('png') or reto.endswith('gif'):
    return reto
  else:
    return get_random(link)
  
# Get random cat
def get_cat():
  url = 'http://thecatapi.com/api/images/get?format=xml&results_per_page=1&type=' + random.choice(['jpg', 'gif', 'png'])
  r = requests.get(url)
  doc = xmltodict.parse(r.content)
  return str(doc['response']['data']['images']['image']['url'])