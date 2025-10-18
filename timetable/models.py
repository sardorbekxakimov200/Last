from django.db import models

class Class(models.Model):
    CLASS_NUMBERS = [(i, str(i)) for i in range(5, 12)]  # 5 to 11 inclusive

    number = models.IntegerField(choices=CLASS_NUMBERS)
    letter = models.CharField(max_length=1)  # e.g. 'A', 'B', 'C'

    class Meta:
        unique_together = ('number', 'letter')  # prevent duplicates like 6A twice
        ordering = ['number', 'letter']

    def __str__(self):
        return f"{self.number}{self.letter}"


GROUP_CHOICES = [
    ('1', 'Group 1'),
    ('2', 'Group 2'),
]

class Pupil(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    school_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='pupils')
    group = models.CharField(max_length=1, choices=GROUP_CHOICES, null=True, blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Teacher(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    

class Subject(models.Model):
    SUBJECT_CHOICES = [
        ('math', 'Mathematics'),
        ('physics', 'Physics'),
        ('chemistry', 'Chemistry'),
        ('biology', 'Biology'),
        ('english', 'English'),
        ('history', 'History'),
        ('geography', 'Geography'),
        ('it', 'Information Technology'),
    ]

    name = models.CharField(max_length=50, choices=SUBJECT_CHOICES, unique=True)

    def __str__(self):
        return dict(self.SUBJECT_CHOICES).get(self.name, self.name)
    

from datetime import time, timedelta, datetime
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone

# Reuse your existing models (adjust import if in different module)
# from .models import Class, Teacher, Subject, Pupil

DAY_CHOICES = [
    ('mon', 'Monday'),
    ('tue', 'Tuesday'),
    ('wed', 'Wednesday'),
    ('thu', 'Thursday'),
    ('fri', 'Friday'),
]

GROUP_CHOICES = [
    ('1', 'Group 1'),
    ('2', 'Group 2'),
    ('all', 'All students'),
]

SESSION_CHOICES = [(i, str(i)) for i in range(1, 9)]  # 1..8


# Helper: compute session start/end times based on school policy.
# School start: 08:30, lesson 45 min, short break 5 min, after 4th lesson big break 45 min.
def session_times(session_index: int):
    if session_index < 1 or session_index > 8:
        raise ValueError("session_index must be between 1 and 8")

    # base start
    start = datetime.combine(datetime.today(), time(hour=8, minute=30))

    # accumulate time up to session_index
    current = start
    for s in range(1, session_index):
        # add lesson
        current += timedelta(minutes=45)
        # break after lesson s
        if s == 4:
            current += timedelta(minutes=45)  # big break after 4th lesson
        else:
            current += timedelta(minutes=5)  # short break

    lesson_start = current.time()
    lesson_end_dt = (current + timedelta(minutes=45)).time()
    return lesson_start, lesson_end_dt


class TimeEntry(models.Model):
    """
    A single lesson slot in the timetable.
    """
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    school_class = models.ForeignKey(
        'Class', on_delete=models.CASCADE, related_name='time_entries'
    )
    session = models.PositiveSmallIntegerField(choices=SESSION_CHOICES)
    subject = models.ForeignKey(
        'Subject', on_delete=models.PROTECT, related_name='time_entries'
    )
    teacher = models.ForeignKey(
        'Teacher', on_delete=models.PROTECT, related_name='time_entries'
    )
    group = models.CharField(max_length=3, choices=GROUP_CHOICES, default='all')
    # Optional custom times if you ever want to override computed times
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['day', 'session', 'school_class', 'group']
        # Basic DB-level uniqueness to avoid exact dupes:
        constraints = [
            models.UniqueConstraint(
                fields=['day', 'session', 'school_class', 'group'],
                name='unique_entry_per_class_day_session_group'
            )
        ]

    def __str__(self):
        return f"{self.get_day_display()} {self.session} - {self.school_class} ({self.group}) {self.subject}"

    def clean(self):
        """
        Validate timetable rules:
        - computed start/end time fill if not provided
        - teacher must not be assigned to another lesson at the same day/session (overlap)
        - a class can have at most 2 groups at same day/session
        - if group='all' exists, no other group allowed for that class/session
        - if either group '1' or '2' exists and an 'all' exists, block
        """
        super().clean()

        # fill start/end if not provided using session_times
        s_time, e_time = session_times(self.session)
        if not self.start_time:
            self.start_time = s_time
        if not self.end_time:
            self.end_time = e_time

        # Query existing entries for same day/session
        qs = TimeEntry.objects.filter(day=self.day, session=self.session)

        # Exclude self when updating
        if self.pk:
            qs = qs.exclude(pk=self.pk)

        # 1) Teacher conflict: teacher can't be in two lessons at the same time
        teacher_conflict = qs.filter(teacher=self.teacher)
        if teacher_conflict.exists():
            raise ValidationError({
                'teacher': "This teacher is already scheduled for another lesson at this time."
            })

        # 2) Class/group logic:
        class_entries = qs.filter(school_class=self.school_class)

        # if there's an 'all' existing, no other entries allowed
        all_exists = class_entries.filter(group='all').exists()
        if all_exists:
            raise ValidationError("This class already has 'all' scheduled at this session; no other groups allowed.")

        # if this new entry is 'all' and any group exists, block it
        if self.group == 'all' and class_entries.exists():
            raise ValidationError("Cannot schedule 'all' for this class/session because group split already exists.")

        # allow at most 2 group entries for the class at same session
        # (group entries might be '1' and '2'—so max 2)
        groups_count = class_entries.count()
        if groups_count >= 2:
            raise ValidationError("This class already has 2 group lessons at this session.")

        # If there's 1 group already and it's same group as this one, block duplicate
        if class_entries.filter(group=self.group).exists():
            raise ValidationError(f"Group '{self.get_group_display()}' for this class is already scheduled at this session.")

    def save(self, *args, **kwargs):
        # Run full_clean to ensure validation fires on save
        self.full_clean()
        # Wrap in transaction to reduce race conditions when many concurrent writes
        with transaction.atomic():
            return super().save(*args, **kwargs)

    @property
    def computed_start_end(self):
        """Return computed (start_time, end_time) tuple based on session index (ignores stored start/end)."""
        return session_times(self.session)
