import os
import csv
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Company

class Command(BaseCommand):
    help = "Imports and registers all companies dynamically from the local com/ folder, parsing their question counts."

    def handle(self, *args, **options):
        # 1. Path to the com/ directory
        com_dir = os.path.join(settings.BASE_DIR.parent, 'com')
        if not os.path.exists(com_dir):
            self.stdout.write(self.style.ERROR(f"Directory 'com/' not found at {com_dir}."))
            return

        # 2. Comprehensive Name overrides
        name_overrides = {
            'tcs': 'TCS',
            'ibm': 'IBM',
            'sap': 'SAP',
            'hcl': 'HCL',
            'siemens': 'Siemens',
            'intel': 'Intel',
            'amd': 'AMD',
            'bcg': 'BCG',
            'bookingcom': 'Booking.com',
            'de-shaw': 'D. E. Shaw',
            'goldman-sachs': 'Goldman Sachs',
            'jpmorgan': 'J.P. Morgan',
            'bny-mellon': 'BNY Mellon',
            'applied-intuition': 'Applied Intuition',
            'persistent-systems': 'Persistent Systems',
            'fractal-analytics': 'Fractal Analytics',
            'general-motors': 'General Motors',
            'pocket-gems': 'Pocket Gems',
            'palo-alto-networks': 'Palo Alto Networks',
            'deutsche-bank': 'Deutsche Bank',
            'epam-systems': 'EPAM Systems',
            'walmart-labs': 'Walmart Global Tech',
            'wells-fargo': 'Wells Fargo',
            'zs-associates': 'ZS Associates',
            'arista-networks': 'Arista Networks',
            'applied-intuition': 'Applied Intuition',
            'dream11': 'Dream11',
            'ola': 'Ola',
            'meesho': 'Meesho',
            'paytm': 'Paytm',
            'phonepe': 'PhonePe',
            'razorpay': 'Razorpay',
            'swiggy': 'Swiggy',
            'zomato': 'Zomato',
            'zepto': 'Zepto',
            'juspay': 'Juspay',
            'hashedin': 'HashedIn',
            'makemytrip': 'MakeMyTrip'
        }

        # 3. Comprehensive Domain overrides for Logo.dev
        domain_overrides = {
            'bookingcom': 'booking.com',
            'de-shaw': 'deshaw.com',
            'goldman-sachs': 'goldmansachs.com',
            'jpmorgan': 'jpmorganchase.com',
            'bny-mellon': 'bnymellon.com',
            'applied-intuition': 'appliedintuition.com',
            'palo-alto-networks': 'paloaltonetworks.com',
            'deutsche-bank': 'db.com',
            'epam-systems': 'epam.com',
            'walmart-labs': 'walmart.com',
            'wells-fargo': 'wellsfargo.com',
            'zs-associates': 'zs.com',
            'arista-networks': 'arista.com',
            'applied-intuition': 'appliedintuition.com',
            'pocket-gems': 'pocketgems.com',
            'general-motors': 'gm.com',
            'fractal-analytics': 'fractal.ai',
            'hcl': 'hcltech.com',
            'infosys': 'infosys.com',
            'expedia': 'expediagroup.com',
            'datadog': 'datadoghq.com',
            'zepto': 'zepto.co',
            'swiggy': 'swiggy.co',
            'ola': 'olacabs.com',
            'juspay': 'juspay.in',
            'dream11': 'dream11.com',
            'bytedance': 'bytedance.com'
        }

        # 4. Scan subdirectories in com/
        items = os.listdir(com_dir)
        company_folders = [item for item in items if os.path.isdir(os.path.join(com_dir, item)) and not item.startswith('.')]

        self.stdout.write(self.style.NOTICE(f"Found {len(company_folders)} company directories to process."))

        count_created = 0
        count_updated = 0

        for folder in sorted(company_folders):
            folder_lower = folder.lower()

            # Resolve Display Name
            if folder_lower in name_overrides:
                display_name = name_overrides[folder_lower]
            else:
                display_name = folder.replace('-', ' ').title()

            # Resolve Domain for Logo.dev
            if folder_lower in domain_overrides:
                domain = domain_overrides[folder_lower]
            else:
                clean_name = folder_lower.replace('-', '')
                domain = f"{clean_name}.com"

            # 5. Parse all.csv to calculate correct question count
            questions_count = 0
            csv_path = os.path.join(com_dir, folder, 'all.csv')
            if os.path.exists(csv_path):
                try:
                    with open(csv_path, 'r', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        # Skip header row
                        next(reader, None)
                        # Count remaining data rows
                        questions_count = sum(1 for row in reader if row)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Could not parse all.csv for {display_name}: {e}"))

            question_count_str = f"{questions_count}+ Questions" if questions_count > 0 else "0+ Questions"

            # 6. Seed/Update Company in database
            company, created = Company.objects.update_or_create(
                repo_folder=folder_lower,
                defaults={
                    'name': display_name,
                    'domain': domain,
                    'link': '#',  # Dynamic local detail url will override this link entirely
                    'question_count': question_count_str,
                    'needs_white_bg': folder_lower in ['tcs', 'accenture', 'infosys', 'wipro', 'cognizant', 'capgemini', 'deloitte', 'blackrock', 'barclays', 'blackrock']
                }
            )

            if created:
                count_created += 1
            else:
                count_updated += 1

        self.stdout.write(self.style.SUCCESS(f"Finished processing companies. Created: {count_created}, Updated: {count_updated}."))
