# Trends Scraper from Tweetdeck

A simple trend scrapper from Tweetdeck, based on the work of [Mateo Grella](https://github.com/matteo-grella/tweetdeck-scraper).

## Why

For research purposes only.

## Requirements

- Ubuntu Server
- MySQL Server
- Rabbit MQ Server
- Google Chrome

## Installation

- For RabbitMQ Server check https://www.rabbitmq.com/install-debian.html

### Google Chrome

  ```bash
  $ wget -c https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  $ sudo apt-get update
  $ sudo dpkg -i google-chrome-stable_current_amd64.deb
  ```


### Essentials

  ```bash
  $ sudo apt-get install virtualenv build-essential python3-dev
  ```

### Configuration

Rename <code>example.env</code> to <code>.env</code> and fill credentials. You can change settings on places.yml too.

### Database

Create mysql database and table:

```mysql
    CREATE TABLE `trends` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `location` varchar(50) NOT NULL,
    `hashtag` varchar(100) NOT NULL,
    `tweets_counter` int(11) NOT NULL,
    `position` int(11) NOT NULL,
    `trend_date` datetime NOT NULL,
    PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```


## Running

  ```bash
  $ virtualenv trends
  $ cd trends

  # Clone this repository
  $ cd trends-scraper
  $ pip install -r requirements.txt

  # Run the script
  $ python scraper.py
  ```
  
## Legal
It is your responsibility to ensure that your use of tweetdeck-scraper does not violate applicable laws.

## License

Tweetdeck Scraper is licensed under the Apache License, Version 2.0. See
[LICENSE](https://github.com/soncco/trends-scraper/blob/master/LICENSE) for the full
license text.
