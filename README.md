# Travelling Merchant Discord Bot

This is a bot for Discord that can be used to keep up with the [Travelling Merchant's](https://runescape.wiki/w/Travelling_Merchant%27s_Shop) stock. Get the current stock at any time, automatic messages to channels on your server as soon as the new stock is found, and interactive notification management for all users.

## Getting Started

Only the __owner__ of the server will be authorized by default!
Invite the bot to your server using [this link](https://discord.com/api/oauth2/authorize?client_id=439803413623078927&permissions=280640&scope=bot).


## Using the bot

Here's how to use all of the bot's commands

### Authorized users

You can manage server specific settings, as well as who else is authorized on your server.

```
?authorize @user
```

authorizes that user on your server

```
?set_daily_channel #channel
?toggle_daily
```

Set what channel will receive a daily message with the updated stock. Make sure the bot has write permissions in this channel. Daily messages are toggled off by default, and can be turned back off at any time after having set a channel.

```
?update
```

If for some reason the stock isn't showing the correct day's stock (note: this is not the same thing as the "the new stock isn't out yet!" message), use this command to force an update.

### All users

```
?merch
```

is the most basic command. Returns an image with the day's stock (if it's been found). The merchant bot pulls its stock from the official RS wiki's page for the travelling merchant, so if that page hasn't been updated then the bot won't know the stock! Aliases include `?merchant, ?shop, ?stock`

```
?addnotif <item>
?removenotif <item>
?shownotifs
```

These help you manage what you get notified for by PM, every day. There are several aliases that are fairly intuitive, like `?newnotif, ?delnotif, ?notifs`, etc. The bot also is pretty lenient when it comes to item names--so don't be worried about memorizing everything!


```
?worlds
```

uses a real-time updated list of worlds called in the #merch-calls channel in the [DSF discord](https://discord.gg/whirlpooldnd). If there aren't any current worlds, join the `whirlpooldnd` fc and help scout!
```
?tomorrow
?future <number>
?next <item name>
```

These commands deal with what's coming up. `?tomorrow` (and `?tmrw`), as you might guess, shows you tomorrow's stock. `?future 10` would show you the stock 10 days from now. `?next air rune` would tell you how long before the next unstable air rune is in stock.

## Privacy Policy
When you add a notification or a daily channel with the bot, your discord user data is stored. This is only used for notification purposes, and can be deleted with the relevant commands above. Server and channel IDs will be deleted within 24 hours of removing the bot from your server.

Message content is not stored by the bot except for the #merch-calls channel in the DSF discord, which is stored for 10 minutes in program memory and not persisted.

## Built With

* [Python](https://www.python.org/) - The base language used
* [discord.py](https://github.com/Rapptz/discord.py) - Discord API wrapper for Python
* [postgreSQL](https://www.postgresql.org/) - Database used
* [Digital Ocean](https://www.digitalocean.com/) - Sever hosting service

## Contributing

Any questions can be PM'd to me @ragnarak54#9413 on discord, or you can use the `?suggestion` command to send me a suggestion.

## Authors

* **Colton Sowers (Proclivity)** - *Initial work* - [github](https://github.com/ragnarak54)
* **Ming Zhang** - *HTML Parsing for items* - [website](https://mingzhang.me/)
* **Yijin Kang** - *Image generation* - [github](https://github.com/yijkan)

## Acknowledgments

* My two frenchy friends who made it all possible
* The loving support of BOSSBANDS
* Discord.py Discord server

