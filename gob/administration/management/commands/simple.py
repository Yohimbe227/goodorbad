from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Prints a greeting message"

    def add_arguments(self, parser):
        parser.add_argument("--name", type=str, help="The name to greet")

    def handle(self, *args, **options):
        name = options["name"]
        if name:
            self.stdout.write(f"Hello, {name}!")
        else:
            self.stdout.write("Hello, world!")
