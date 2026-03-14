---
description: "Use when creating or modifying Django management commands, seeders, fixtures, or database population scripts. Covers idempotency patterns, get_or_create usage, and permission seeding."
applyTo: "sitetibl/management/commands/seed_*.py"
---

# Seeder / Management Command Conventions

## Idempotency

All seeders MUST be safe to run multiple times without duplicating data:

```python
obj, created = Model.objects.get_or_create(
    unique_field=value,
    defaults={...}
)
self.stdout.write(f'{Model.__name__}: {"criado" if created else "já existia"}')
```

## Structure

Follow the pattern in `seed_base_data.py`:

1. `handle()` calls individual seed methods in dependency order
2. Each method prints its own summary (created count + total count)
3. Support `--skip-*` flags for optional sections (e.g. `--skip-demo`)

## Group Permission Assignment

When creating or updating groups, always assign Django permissions:

```python
from django.contrib.auth.models import Permission

perms = Permission.objects.filter(
    content_type__app_label='sitetibl',
    codename__in=[...],
)
group.permissions.set(perms)
```

Update `_assign_group_permissions()` in `seed_base_data.py` when adding new models.

## Database Compatibility

Seeders must work on both SQLite (dev) and MySQL (prod). Avoid raw SQL; use the ORM exclusively.
