from django.db import migrations


class Migration(migrations.Migration):
    """Repair schema drift for accounts_user in environments with old/faked migrations."""

    dependencies = [
        ("accounts", "0003_artisanstory"),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                "ALTER TABLE accounts_user ADD COLUMN IF NOT EXISTS phone_number varchar(15);",
                "ALTER TABLE accounts_user ADD COLUMN IF NOT EXISTS bio text NOT NULL DEFAULT '';",
                "ALTER TABLE accounts_user ADD COLUMN IF NOT EXISTS region varchar(150) NOT NULL DEFAULT '';",
                "ALTER TABLE accounts_user ADD COLUMN IF NOT EXISTS experience_years integer NOT NULL DEFAULT 0;",
                "ALTER TABLE accounts_user ADD COLUMN IF NOT EXISTS profile_image varchar(100);",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
