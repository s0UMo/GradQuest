import os
import csv
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db.models import Count
from core.models import Company

class Command(BaseCommand):
    help = "Imports and updates database companies using leetcode_lists.csv and cleans up database duplicates."

    def handle(self, *args, **options):
        # 1. Paths to resources
        csv_path = os.path.join(settings.BASE_DIR.parent, 'leetcode_lists.csv')
        com_dir = os.path.join(settings.BASE_DIR.parent, 'com')

        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f"File 'leetcode_lists.csv' not found at {csv_path}."))
            return

        # 2. Folder overrides
        folder_map = {
            'sap labs': 'sap',
            'hcltech': 'hcl',
            'razor pay': 'razorpay',
            'sales force': 'salesforce',
            'tech mahindra': 'tech-mahindra'
        }

        white_bg_folders = [
            'tcs', 'accenture', 'infosys', 'wipro', 'cognizant', 'capgemini', 'deloitte', 'hcl', 'sap'
        ]

        self.stdout.write(self.style.NOTICE(f"Reading companies from {csv_path}..."))

        count_created = 0
        count_updated = 0

        # 3. Read leetcode_lists.csv
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            self.stdout.write(self.style.NOTICE(f"Found {len(rows)} records in leetcode_lists.csv."))

            for row in rows:
                name = row.get('list Name', '').strip()
                link = row.get('list Link', '').strip()
                logo_url = row.get('List Image Link', '').strip()

                if not name or not link:
                    continue

                # Standardize folder/repo_folder name
                name_lower = name.lower()
                if name_lower in folder_map:
                    folder_lower = folder_map[name_lower]
                else:
                    folder_lower = name_lower.replace(' ', '-')

                # 4. Check for local CSV file to count questions
                questions_count = 0
                local_csv = os.path.join(com_dir, folder_lower, 'all.csv')
                if os.path.exists(local_csv):
                    try:
                        with open(local_csv, 'r', encoding='utf-8') as lf:
                            lreader = csv.reader(lf)
                            next(lreader, None)  # Skip header
                            questions_count = sum(1 for lrow in lreader if lrow)
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"Error reading local CSV for {name}: {e}"))

                # Fallback question count logic
                if questions_count > 0:
                    question_count_str = f"{questions_count}+ Questions"
                else:
                    # Check existing database company question count
                    try:
                        existing_comp = Company.objects.filter(repo_folder=folder_lower).first()
                        if existing_comp and "0+" not in existing_comp.question_count:
                            question_count_str = existing_comp.question_count
                        else:
                            question_count_str = "100+ Questions" if folder_lower in ['accenture', 'capgemini', 'cognizant', 'deloitte', 'infosys', 'tcs', 'wipro'] else "50+ Questions"
                    except Exception:
                        question_count_str = "50+ Questions"

                # 5. Save or update the database record (by repo_folder)
                company, created = Company.objects.update_or_create(
                    repo_folder=folder_lower,
                    defaults={
                        'name': name,
                        'link': link,
                        'logo_url': logo_url,
                        'question_count': question_count_str,
                        'needs_white_bg': folder_lower in white_bg_folders
                    }
                )

                if created:
                    count_created += 1
                else:
                    count_updated += 1

            self.stdout.write(self.style.SUCCESS(f"Seeding completed. Created: {count_created}, Updated: {count_updated}."))

            # 6. Database duplicate cleaning logic
            self.stdout.write(self.style.NOTICE("Cleaning up duplicate company entries in database..."))
            
            # Find names that have duplicate records
            duplicates = (
                Company.objects.values('name')
                .annotate(name_count=Count('id'))
                .filter(name_count__gt=1)
            )

            count_deleted = 0
            for dup in duplicates:
                dup_name = dup['name']
                records = list(Company.objects.filter(name=dup_name))
                
                # Sort records: prefer those with non-empty repo_folder and non-empty link, and keep the newest one first
                records.sort(
                    key=lambda c: (
                        1 if c.repo_folder else 0,
                        1 if c.link and c.link != '#' else 0,
                        c.id
                    ),
                    reverse=True
                )
                
                # Keep the best record (index 0) and delete all duplicates (indices 1+)
                best_record = records[0]
                duplicate_records = records[1:]
                
                for c in duplicate_records:
                    c.delete()
                    count_deleted += 1

            self.stdout.write(self.style.SUCCESS(f"Cleanup finished. Deleted {count_deleted} duplicate records."))

            # Clear cache
            from django.core.cache import cache
            cache.delete('sorted_companies')
            self.stdout.write(self.style.SUCCESS("Cache 'sorted_companies' cleared successfully."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Fail to import companies: {e}"))
