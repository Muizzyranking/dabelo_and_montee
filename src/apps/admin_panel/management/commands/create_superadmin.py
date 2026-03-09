from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.admin_panel.models import AdminProfile

User = get_user_model()


class Command(BaseCommand):
    help = "Create a superadmin. Reads from env if --noinput is passed."

    def add_arguments(self, parser):
        parser.add_argument("--email", type=str, default="")
        parser.add_argument("--password", type=str, default="")
        parser.add_argument("--firstname", type=str, default="")
        parser.add_argument("--lastname", type=str, default="")
        parser.add_argument(
            "--noinput",
            action="store_true",
            help="Read credentials from env vars — no prompts.",
        )
        parser.add_argument(
            "--skip-existing",
            action="store_true",
            help="Exit silently if a superadmin already exists.",
        )

    def handle(self, *args, **options):
        # --skip-existing — useful in docker entrypoints so re-runs don't fail
        if options["skip_existing"] and AdminProfile.objects.filter(is_superadmin=True).exists():
            self.stdout.write("Superadmin already exists — skipping.")
            return

        if options["noinput"]:
            email = options["email"] or getattr(settings, "SUPERADMIN_EMAIL", "")
            password = options["password"] or getattr(settings, "SUPERADMIN_PASSWORD", "")
            firstname = options["firstname"] or getattr(settings, "SUPERADMIN_FIRST_NAME", "Super")
            lastname = options["lastname"] or getattr(settings, "SUPERADMIN_LAST_NAME", "Admin")

            if not email or not password:
                self.stderr.write(
                    self.style.ERROR(
                        "SUPERADMIN_EMAIL and SUPERADMIN_PASSWORD must be set "
                        "in .env when using --noinput."
                    )
                )
                return
        else:
            import getpass

            email = options["email"] or input("Email: ").strip().lower()
            firstname = options["firstname"] or input("First name (optional): ").strip()
            lastname = options["lastname"] or input("Last name (optional): ").strip()

            if options["password"]:
                password = options["password"]
            else:
                password = getpass.getpass("Password: ")
                confirm = getpass.getpass("Confirm password: ")
                if password != confirm:
                    self.stderr.write(self.style.ERROR("Passwords do not match."))
                    return

        if not email or not password:
            self.stderr.write(self.style.ERROR("Email and password are required."))
            return

        if User.objects.filter(email=email).exists():
            self.stderr.write(
                self.style.ERROR(
                    f"User {email} already exists. Use --skip-existing to suppress this error."
                )
            )
            return

        with transaction.atomic():
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=firstname,
                last_name=lastname,
                is_staff=True,
            )
            AdminProfile.objects.create(
                user=user,
                is_superadmin=True,
                can_view_dabelo_products=True,
                can_edit_dabelo_products=True,
                can_view_montee_products=True,
                can_edit_montee_products=True,
                can_view_orders=True,
                can_edit_orders=True,
                can_view_quotes=True,
                can_edit_quotes=True,
                can_manage_images=True,
            )

        self.stdout.write(self.style.SUCCESS(f"Superadmin created: {email}"))
