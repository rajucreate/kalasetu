from django.db import migrations


class Migration(migrations.Migration):
    """Allow inserts when legacy accounts_user.username column still exists."""

    dependencies = [
        ("accounts", "0004_repair_user_schema_drift"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_name = 'accounts_user' AND column_name = 'username'
                ) THEN
                    ALTER TABLE accounts_user ALTER COLUMN username DROP NOT NULL;
                END IF;
            END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
