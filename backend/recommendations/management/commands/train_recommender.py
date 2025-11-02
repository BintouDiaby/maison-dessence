from django.core.management.base import BaseCommand
from recommendations.recommender import train


class Command(BaseCommand):
    help = 'Train the TF-IDF recommender using products data or DB.'

    def handle(self, *args, **options):
        res = train()
        self.stdout.write(self.style.SUCCESS(f"Trained recommender: {res}"))
