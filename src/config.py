from configparser import ConfigParser


class Config:
    def __init__(self):
        self.filename = 'config.ini'
        self.config = ConfigParser()
        self.read()

    @property
    def server_url(self):
        return self.config.get('server', 'url')

    def get_device_connection_string(self, device_name):
        if not self.config.has_option('devices', device_name):
            self.config.set('devices', device_name, input(f'Podaj connection string dla urządzenia {device_name}: '))
            self.save()
        return self.config.get('devices', device_name)

    def read(self):
        self.config.read(self.filename)
        changes = False

        if not self.config.has_section('server'):
            self.config.add_section('server')
            changes = True

        if not self.config.has_option('server', 'url'):
            self.config.set('server', 'url', input('Podaj adres serwera: '))
            changes = True

        if not self.config.has_section('devices'):
            self.config.add_section('devices')
            changes = True

        if changes:
            self.save()

    def save(self):
        with open(self.filename, 'w') as configfile:
            self.config.write(configfile)
