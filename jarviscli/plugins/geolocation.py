import requests
from plugin import plugin, require

@require(network=True)
@plugin('geolocation')
def geolocation(jarvis, s):
    """ Helps to geolocate an IP address """
    base_url = "https://api.ip2location.io/"
    payload = {'ip': s, 'format': 'json'}
    jarvis.say(f'Lookup {s} now...')
    api_result = requests.get(base_url, params=payload)
    api_result_json = api_result.json()
    jarvis.say("It's located at {}, {}, {}.".format(
        api_result_json['city_name'], api_result_json['region_name'],
        api_result_json['country_name']))
    jarvis.say("It's coordinates are ({}, {}).".format(
        api_result_json['latitude'], api_result_json['longitude']))
    jarvis.say("It's owned by {} with the ASN {}.".format(
        api_result_json['as'], api_result_json['asn']))
