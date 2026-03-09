from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from admin_panel.models import AdminProfile

User = get_user_model()


class Command(BaseCommand):
    help = "Create a superadmin account with full admin panel access."

    def add_arguments(self, parser):
        parser.add_argument("--email", type=str)
        parser.add_argument("--password", type=str)
        parser.add_argument("--firstname", type=str, default="")
        parser.add_argument("--lastname", type=str, default="")
        parser.add_argument(
            "--noinput",
            action="store_true",
            help="Non-interactive — requires --email and --password",
        )

    def handle(self, *args, **options):
        email = options["email"]
        password = options["password"]
        firstname = options["firstname"]
        lastname = options["lastname"]

        if not options["noinput"]:
            if not email:
                email = input("Email: ").strip().lower()
            if not password:
                import getpass

                password = getpass.getpass("Password: ")
                confirm = getpass.getpass("Confirm password: ")
                if password != confirm:
                    self.stderr.write(self.style.ERROR("Passwords do not match."))
                    return
            if not firstname:
                firstname = input("First name (optional): ").strip()
            if not lastname:
                lastname = input("Last name (optional): ").strip()

        if not email or not password:
            self.stderr.write(
                self.style.ERROR(
                    "Email and password are required. "
                    "Use --email and --password with --noinput."
                )
            )
            return

        if User.objects.filter(email=email).exists():
            self.stderr.write(
                self.style.ERROR(f"A user with email {email} already exists.")
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
                # Grant all permissions explicitly too
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
