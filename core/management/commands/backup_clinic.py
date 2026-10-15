import os
import shutil
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = "Creates a timestamped snapshot backup of database and media uploads"

    def handle(self, *args, **options):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)

        # Backup Database
        db_path = settings.DATABASES['default']['NAME']
        if os.path.exists(db_path):
            dest_db = os.path.join(backup_dir, f'vetcare_db_{timestamp}.sqlite3')
            shutil.copy2(db_path, dest_db)
            self.stdout.write(self.style.SUCCESS(f"Database backed up to: {dest_db}"))

        # Backup Media Files
        if hasattr(settings, 'MEDIA_ROOT') and os.path.exists(settings.MEDIA_ROOT):
            dest_media = os.path.join(backup_dir, f'media_{timestamp}')
            shutil.copytree(settings.MEDIA_ROOT, dest_media, dirs_exist_ok=True)
            self.stdout.write(self.style.SUCCESS(f"Media folder backed up to: {dest_media}"))

        self.stdout.write(self.style.SUCCESS("Clinic backup completed successfully!"))
