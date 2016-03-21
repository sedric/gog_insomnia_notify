#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import json
import re
import logging
from time import sleep
from subprocess import call
import ConfigParser

def get_dict_from_config(conffd):
  config = {}

  for section in conffd.sections():
    config[section] = {}
    for option in conffd.options(section):
      data = conffd.get(section, option)
      config[section][option] = data
  return config

def search(game, wishlist):
    fdwishes = open(wishlist, 'r')
    for wish in fdwishes:
        if re.search(game, wish):
            fdwishes.close()
            return 0
    fdwishes.close()
    return 1

def get_currency_id(cc, groups):
    group_possible = []
    for group in groups:
        if re.search(cc, groups[group]):
            group_possible.append(str(group[0]))
    return group_possible

def notify(cmd, game, oprice, nprice, discount, gameurl):
    message =  game + "\n"
    message = message +  "  Old price : " + oprice + "\n"
    message = message +  "  New price : " + nprice + "\n"
    message = message +  "  Discount  : " + discount + "%\n"
    message = message +  "  https://gog.com" + gameurl + "\n"
    call([cmd, message])

def processing(config, data):
    # Extract data from JSON
    dealtype    = data['dealType']
    deal        = data[dealtype]
    gameurl     = deal['url']
    game        = gameurl.split("/")[2]
    countrygrp  = deal['prices']['countriesGroups']
    currency_ids = get_currency_id(config['my_country_code'], countrygrp)

    # Because a country can be in multiple groups, here we find the one that
    # match my_currency
    for currency_id in currency_ids:
        try:
            prices = deal['prices']['groupsPrices'][config['my_currency']][currency_id]
            break
        except KeyError:
            continue
    oldprice    = prices.split(";")[0]
    newprice    = prices.split(";")[1]
    discount    = str(data['discount'])

    if search(game, config['wishlist']) == 0:
        notify(config['cmd'], game, oldprice, newprice, discount, gameurl)
    logging.info(game + " : " + newprice + config['my_currency'] + " (-" + discount + "%)")

def main():
    config    = {}
    last_game = None
    conffd    = ConfigParser.ConfigParser()
    conffd.read("config.ini")
    config    = get_dict_from_config(conffd)
    logging.basicConfig(format='%(levelname)s:%(message)s', level=config['insomnia']['loglevel'])

    while True:
        try:
            jsonurl = urllib2.urlopen(config['insomnia']['url'])
            data    = json.loads(jsonurl.read())
        except urllib2.HTTPError as e:
            logging.critical("The URL does not exists, the promo as ended")
            exit(1)
        except urllib2.URLError as e:
            logging.debug("Connexion problem, will try again later " + e)
            sleep(1)

        try:
            game = data['product']['url'].split("/")[2]
            if not last_game == game:
                print last_game
                processing(config['insomnia'], data)
                last_game = game
        except KeyError:
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
