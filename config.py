import yaml
from decouple import config as cenv

__config = None

def config():
    if not __config:
        with open('./places.yml') as f:
            config = yaml.safe_load(f)

    config['twitter_username'] = cenv('twitter_username')
    config['twitter_password'] = cenv('twitter_password')
    config['twitter_mail'] = cenv('twitter_mail')
    config['rmq_username'] = cenv('rmq_username')
    config['rmq_password'] = cenv('rmq_password')
    config['mysql_user'] = cenv('mysql_user')
    config['mysql_password'] = cenv('mysql_password')

    return config
