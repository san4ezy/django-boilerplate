from django.contrib.auth import get_user_model
from django.core.management import BaseCommand


User = get_user_model()


class Command(BaseCommand):
    help = "Example command"

    # def add_arguments(self, parser):
    #     parser.add_argument("-f", "--file", type=str, help="file")
    #     parser.add_argument("-s", "--strings", type=str)

    def handle(self, *args, **options):

        self.stdout.write(
            self.style.SUCCESS("Success")
        )
