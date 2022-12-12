from configparser import ConfigParser


class Config:
  def __init__(self):
    self.filename = 'config.ini'
    self.config = ConfigParser()
    self.read()

  @property
  def server_url(self):
    return self.config.get('server', 'url')

  def read(self):
    self.config.read(self.filename)
    changes = False

    if not self.config.has_section('server'):
      self.config.add_section('server')

    if not self.config.has_option('server', 'url'):
      self.config.set('server', 'url', input('Podaj adres serwera: '))
      changes = True

    if changes:
      self.save()

  def save(self):
    with open(self.filename, 'w') as configfile:
      self.config.write(configfile)