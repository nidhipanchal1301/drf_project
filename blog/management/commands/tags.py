from django.core.management.base import BaseCommand
from blog.models import Tag



class Command(BaseCommand):
    help = "tags"

    def add_arguments(self, parser):
        parser.add_argument(
            '--total', type=int, default=1000,
            help='Number of tags to create (default 1000)'
        )

    def handle(self, *args, **options):
        total = options['total']
        tags = []

        for i in range(1, total + 1):
            tag_name = f"django{i}"
            if not Tag.objects.filter(name=tag_name).exists():
                tags.append(Tag(name=tag_name))

        Tag.objects.bulk_create(tags)
        self.stdout.write(self.style.SUCCESS(f"Successfully created {len(tags)} tags"))
