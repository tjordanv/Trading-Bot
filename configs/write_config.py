from configparser import ConfigParser

config = ConfigParser()

config.add_section('main')
config.set('main', 'CLIENT_ID', 'UQ3PAMGKASVKXJPCZS2VAWAQWBX4FUXB')
config.set('main', 'REDIRECT_URI', 'http://localhost:3000/callback')
config.set('main', 'JSON_PATH', 'C:/Users/Tyler/Desktop/td_state.json')
config.set('main', 'ACCOUNT_NUMBER', '232110356')

with open('config.ini', 'w+') as f:
    config.write(f)
