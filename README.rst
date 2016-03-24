GOG Insomnia Notifier
#####################

A toy script that watch current insomnia sales on GOG.com and send a notification where a game on your Wishlist is on sale.

The notification can be any exernal progam that takes one argument (informations about the sale).

Default is `echo` but it can be a script that send you a mail / SMS / desktop notification / etc.

The wishlist file is just plain text file with the game name (as they appear in GOG's URLs), one game per line. You can generate it with the excellent lgogdownloader (see config.ini.sample).

Known Issues :

- Can't notify about bundle sales or a specific game in a bundle (as I don't have the time to see how to request a game name by it ID)
- The wishlist file as to be present, even if it's empty (but then, I don't think you really need this script)

If you don't have a wishlist, you can use it as a text notifier by configuring logging to INFO.
