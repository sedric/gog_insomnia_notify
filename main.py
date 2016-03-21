#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import json
import re
from time import sleep
from subprocess import call

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

def print_infos(cmd, game, oprice, nprice, discount, gameurl):
    message =  game + "\n"
    message = message +  "  Old price : " + oprice + "\n"
    message = message +  "  New price : " + nprice + "\n"
    message = message +  "  Discount  : " + discount + "%\n"
    message = message +  "  https://gog.com" + gameurl + "\n"
    print message

def processing(my_country_code, my_currency, wishlist, cmd, data):
    # Extract data from JSON
    dealtype    = data['dealType']
    deal        = data[dealtype]
    gameurl     = deal['url']
    game        = gameurl.split("/")[2]
    countrygrp  = deal['prices']['countriesGroups']
    currency_ids = get_currency_id(my_country_code, countrygrp)

    # Because a country can be in multiple groups, here we find the one that
    # match my_currency
    for currency_id in currency_ids:
        try:
            prices = deal['prices']['groupsPrices'][my_currency][currency_id]
            break
        except KeyError:
            continue
    oldprice    = prices.split(";")[0]
    newprice    = prices.split(";")[1]
    discount    = str(data['discount'])

    if search(game, wishlist) == 0:
        print_infos(cmd, game, oldprice, newprice, str(data['discount']), gameurl)
    else:
        print game + " : " + newprice + my_currency + " (-" + discount + "%)"

def main():
    # Config
    url             = 'https://www.gog.com/insomnia/current_deal'
    # lgogdownloader --wishlist | grep https | cut -d'/' -f 5 > wishlist
    wishlist        = './wishlist'
    last_game       = None
    my_country_code = 'FR'
    my_currency     = 'EUR'
    cmd             = 'echo'

    while True:
        try:
            jsonurl = urllib2.urlopen(url)
            data    = json.loads(jsonurl.read())
        except urllib2.HTTPError:
            # The URL does not exists, the promo as ended
            exit(1)
        except urllib2.URLError:
            # Connexion problem, wait a little time
            sleep(1)

        try:
            game = data['product']['url'].split("/")[2]
            if not last_game == game:
                processing(my_country_code, my_currency, wishlist, cmd, data)
                last_game = game
        except KeyError:
            game = data['bundle']['description']
            #debug to gain bundle example
            #call(["./print.sh", game, str(data)])
            discount = str(data['discount'])
            if not last_game == game:
                print "Bundle : " + game + " (-" + discount + "%)"
                last_game = game
            sleep(10)
        except NameError:
            # Previous connexion error
            continue
        sleep(1)


if __name__ == '__main__':
    main()
