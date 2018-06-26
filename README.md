# Travelling Merchant Discord Bot

This is a bot for Discord that can be used to keep up with the [Travelling Merchant's](add link) stock. Get the current stock at any time, automatic messages to channels on your server as soon as the new stock is found, and interactive notification management for all users.

## Getting Started

Add me as a friend on Discord @ragnarak54#9413, and I'll help you invite the bot to your server! Once it's invited, you'll set up which users are authorized to use admin commands, as well as what channel you want to be your daily message channel.

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

If for some reason the stock isn't showing the correct day's stock (different from the "the new stock isn't out yet!" message), use this command to force an update.

### All users

```
?merch
```

is the most basic command. Returns an image with the day's stock (if it's been found). Aliases include `?merchant, ?shop, ?stock`

```
?addnotif <item>
?removenotif <item>
?shownotifs
```

These help you manage what you get notified for by PM, every day. There are several aliases that are fairly intuitive, like `?newnotif, ?delnotif, ?notifs`, etc. The bot also is pretty lenient when it comes to item names--so don't be worried about memorizing everything!

## Built With

* [Python](https://www.python.org/) - The base language used
* [discord.py](https://github.com/Rapptz/discord.py) - Discord API wrapper for Python
* [postgreSQL](https://www.postgresql.org/) - Database used
* [Digital Ocean](https://www.digitalocean.com/) - Sever hosting service

## Contributing

Any questions can be PM'd to me @ragnarak54#9413 on discord, or you can use the `?suggestion` command to send me a suggestion.

## Authors

* **Colton Sowers (Proclivity)** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## Acknowledgments

* My two frenchy friends who made it all possible
* The loving support of BOSSBANDS
* 

