from io import StringIO
from django.core.management import call_command
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gob.settings")
django.setup()

def test_greeting_command_without_name(capsys):


    call_command('simple')
    captured = capsys.readouterr()
    assert captured.out == 'Hello, world!\n'
