from django.core.management.base import BaseCommand
from django.utils import timezone

from tenant.models import Job, Task


class Command(BaseCommand):
    help = "Schedule Manager"

    def handle(self, *args, **options):
        current_datetime = timezone.localtime(timezone.now())

        # Create tasks from jobs
        jobs_without_tasks = Job.objects.filter(tasks__isnull=True).order_by("sort_key")

        for job in jobs_without_tasks:
            if not job.is_visible:
                continue

            if job.month:
                if int(job.month) != current_datetime.month:
                    continue

            if job.weekday:
                if int(job.day_of_week) != current_datetime.weekday():
                    continue

            if job.time:
                job_time = timezone.datetime.strptime(job.time, "%H:%M").time()
                if (
                    current_datetime.hour != job_time.hour
                    or current_datetime.minute != job_time.minute
                ):
                    continue

            Task.objects.create(job=job, sort_key=job.sort_key, is_locked=False)

        # Execute tasks
        tasks = (
            Task.objects.select_related("job")
            .filter(is_locked=False)
            .order_by("-sort_key")
        )
        for task in tasks:
            try:
                if not task.job.is_visible:
                    continue

                task.is_locked = True
                task.save()

                if task.slug == "xxx":
                    pass

                task.delete()
            except Job.DoesNotExist:
                pass
            except Task.DoesNotExist:
                pass

        self.stdout.write(self.style.SUCCESS("Job completed successfully!"))
