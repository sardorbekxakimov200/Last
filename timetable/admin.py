from django.contrib import admin
from .models import Class, Pupil, Teacher, Subject, TimeEntry


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name')
    search_fields = ('first_name', 'last_name')


class PupilInline(admin.TabularInline):
    model = Pupil
    extra = 1


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('number', 'letter')
    list_filter = ('number',)
    search_fields = ('letter',)
    ordering = ('number', 'letter')
    inlines = [PupilInline]


@admin.register(Pupil)
class PupilAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'school_class')
    list_filter = ('school_class__number', 'school_class__letter')
    search_fields = ('first_name', 'last_name')
    ordering = ('school_class__number', 'school_class__letter', 'last_name')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('get_full_name',)
    search_fields = ('name',)

    def get_full_name(self, obj):
        return obj.__str__()
    get_full_name.short_description = "Subject"


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = (
        'day_display',
        'session',
        'school_class',
        'subject',
        'teacher',
        'group',
        'start_time_display',
        'end_time_display',
    )
    list_filter = (
        'day',
        'session',
        'school_class__number',
        'school_class__letter',
        'subject',
        'teacher',
        'group',
    )
    search_fields = (
        'school_class__letter',
        'teacher__first_name',
        'teacher__last_name',
        'subject__name',
    )
    ordering = (
        'day',
        'session',
        'school_class__number',
        'school_class__letter',
        'group',
    )
    autocomplete_fields = ('teacher', 'school_class', 'subject')

    # Display methods
    def start_time_display(self, obj):
        return obj.start_time or obj.computed_start_end[0]
    start_time_display.short_description = "Start Time"

    def end_time_display(self, obj):
        return obj.end_time or obj.computed_start_end[1]
    end_time_display.short_description = "End Time"

    def day_display(self, obj):
        return obj.get_day_display()
    day_display.short_description = "Day"
