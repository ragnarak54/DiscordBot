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

### All users

```
?merch
```

is the most basic command. Returns an image with the day's stock (if it's been found). Aliases include `?merchant, ?shop, ?stock`



### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc

