#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import json
import re
import logging
from time import sleep
from subprocess import call
import ConfigParser

# Get JSON data from GOG
def get_data_from_url(url):
    try:
        jsonurl = urllib2.urlopen(url)
        data    = json.loads(jsonurl.read())
        return data
    except urllib2.HTTPError as e:
        logging.critical("The URL does not exists, the promo as ended")
        exit(1)
    except urllib2.URLError as e:
        logging.debug("Connexion problem, will try again later " + str(e))
        sleep(1)

# Export config file as a dict
def get_dict_from_config(conffd):
  config = {}

  for section in conffd.sections():
    config[section] = {}
    for option in conffd.options(section):
      data = conffd.get(section, option)
      config[section][option] = data
  return config

# Check if current game in sale is in the wishlist
def search(game, wishlist):
    fdwishes = open(wishlist, 'r')
    for wish in fdwishes:
        if re.search(game, wish):
            fdwishes.close()
            return 0
    fdwishes.close()
    return 1

# Find the prices that match current country and currency
def get_prices(cc, currency, countrygrps, pricesgrps):
    group_possible = []
    for group in countrygrps:
        if re.search(cc, countrygrps[group]):
            group_possible.append(str(group[0]))
    # Because a country can be in multiple groups, here we find the one that
    # match my_currency
    for currency_id in group_possible:
        try:
            prices = pricesgrps[currency][currency_id]
            break
        except KeyError:
            continue
    return prices

# Generate a message and send it via configured command
def notify(cmd, game, oprice, nprice, discount, gameurl):
    message =  game + "\n"
    message = message +  "  Old price : " + oprice + "\n"
    message = message +  "  New price : " + nprice + "\n"
    message = message +  "  Discount  : " + discount + "%\n"
    message = message +  "  https://gog.com" + gameurl + "\n"
    call([cmd, message])

# Extract usefull informations from JSON et send them to notify()
def processing(config, data):
    dealtype    = data['dealType']
    deal        = data[dealtype]
    gameurl     = deal['url']
    game        = gameurl.split("/")[2]
    countrygrps = deal['prices']['countriesGroups']
    pricesgrps  = deal['prices']['groupsPrices']
    prices      = get_prices(config['my_country_code'],config['my_currency'], countrygrps, pricesgrps)
    oldprice    = prices.split(";")[0]
    newprice    = prices.split(";")[1]
    discount    = str(data['discount'])

    logging.info(game + " : " + newprice + config['my_currency'] + " (-" + discount + "%)")
    if search(game, config['wishlist']) == 0:
        notify(config['cmd'], game, oldprice, newprice, discount, gameurl)

# Main loop, read the configuration
def main():
    config    = {}
    last_game = None
    conffd    = ConfigParser.ConfigParser()
    conffd.read("config.ini")
    config    = get_dict_from_config(conffd)
    logging.basicConfig(format='%(levelname)s:%(message)s', level=config['insomnia']['loglevel'])

    while True:
        data = get_data_from_url(config['insomnia']['url'])
        try:
            game = data['product']['url'].split("/")[2]
            if not last_game == game:
                processing(config['insomnia'], data)
                last_game = game
        except KeyError:
            # Bundles don't have games URL, only game ID, I don't know how to
            # link them to a game so don't do anything
            game = data['bundle']['description']
            discount = str(data['discount'])
            if not last_game == game:
                logging.info("Bundle : " + game + " (-" + discount + "%)")
                last_game = game
            sleep(10)
        except NameError:
            # Previous connexion error
            continue
        sleep(1)

if __name__ == '__main__':
    main()
