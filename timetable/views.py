# timetable/views.py
from datetime import datetime, time, timedelta
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Q

from .models import Pupil, TimeEntry





# session_times copied from your models file (keeps logic consistent)
def session_times(session_index: int):
    if session_index < 1 or session_index > 8:
        raise ValueError("session_index must be between 1 and 8")

    start = datetime.combine(datetime.today(), time(hour=8, minute=30))

    current = start
    for s in range(1, session_index):
        current += timedelta(minutes=45)
        if s == 4:
            current += timedelta(minutes=45)  # big break after 4
        else:
            current += timedelta(minutes=5)
    lesson_start = current.time()
    lesson_end_dt = (current + timedelta(minutes=45)).time()
    return lesson_start, lesson_end_dt

# create a mapping of session -> (start, end) for quick lookup
SESSION_RANGES = {i: session_times(i) for i in range(1, 9)}

# map python weekday() -> your day code (0=Monday)
WEEKDAY_TO_CODE = {
    0: 'mon',
    1: 'tue',
    2: 'wed',
    3: 'thu',
    4: 'fri',
    5: None,  # weekend
    6: None,
}


def get_current_session(now_time):
    """
    now_time: datetime.time
    Return session index (int) or None if outside sessions.
    """
    for i, (start, end) in SESSION_RANGES.items():
        if start <= now_time < end:
            return i
    return None


def pupil_now(request):
    """
    GET params:
      q=search string for pupil (first or last name). If omitted shows an empty form.
    """
    q = request.GET.get('q', '').strip()
    results = []
    message = ''
    now = timezone.localtime(timezone.now())
    weekday = now.weekday()  # 0..6
    day_code = WEEKDAY_TO_CODE.get(weekday)

    if day_code is None:
        message = "Today is weekend — no lessons scheduled."
    else:
        current_session = get_current_session(now.time())
        if current_session is None:
            message = f"No lesson right now. Current time {now.time().strftime('%H:%M')} is outside defined session ranges."
        else:
            # If q is provided, find matching pupils (search first or last)
            if q:
                pupils = Pupil.objects.filter(
                    Q(first_name__icontains=q) |
                    Q(last_name__icontains=q) |
                    Q(first_name__icontains=q.split(' ')[0]) |
                    Q(last_name__icontains=q.split(' ')[-1])
                ).select_related('school_class')[:50]
                if not pupils.exists():
                    message = "No pupils found for that search."
                else:
                    for pupil in pupils:
                        # fetch TimeEntry items for this pupil's class at this day/session
                        # because there's no pupil.group, we return:
                        #  - entries with group='all'
                        #  - entries with group '1' or '2' (both)
                        entries = TimeEntry.objects.filter(
                            day=day_code,
                            session=current_session,
                            school_class=pupil.school_class
                        ).select_related('subject', 'teacher').order_by('group')

                        # Format entries for template
                        formatted = []
                        for e in entries:
                            start, end = e.start_time or e.computed_start_end[0], e.end_time or e.computed_start_end[1]
                            formatted.append({
                                'subject': str(e.subject),
                                'teacher': str(e.teacher),
                                'group': e.get_group_display(),
                                'start': start.strftime("%H:%M") if start else '',
                                'end': end.strftime("%H:%M") if end else '',
                            })

                        results.append({
                            'pupil': f"{pupil.first_name} {pupil.last_name}",
                            'class': str(pupil.school_class),
                            'entries': formatted,
                        })
            else:
                message = "Enter a pupil's first or last name to search."

    context = {
        'query': q,
        'now': now,
        'day_code': day_code,
        'session': current_session if day_code else None,
        'results': results,
        'message': message,
    }
    return render(request, 'timetable/pupil_results.html', context)









from django.shortcuts import render
from datetime import datetime
from django.db.models import Q
from .models import Class, Pupil
from .models import TimeEntry as TimetableEntry

def timetable_simulator(request):
    classes = Class.objects.all()
    entries = []
    selected_class = None
    selected_day = None
    selected_time = None

    if request.method == "POST":
        selected_class_id = request.POST.get("class_id")
        selected_day = request.POST.get("day")
        selected_time = request.POST.get("time")

        if selected_class_id and selected_day and selected_time:
            selected_class = Class.objects.get(id=selected_class_id)
            # Simulate a weekday date just to combine with time
            fake_date = datetime.strptime("2025-10-13", "%Y-%m-%d")  # Monday
            hour, minute = map(int, selected_time.split(":"))
            now = fake_date.replace(hour=hour, minute=minute)
            entries = TimetableEntry.objects.filter(
                day=selected_day,
                school_class=selected_class,
                start_time__lte=now.time(),
                end_time__gte=now.time(),
            )

    return render(request, "timetable_simulator.html", {
        "classes": classes,
        "entries": entries,
        "selected_class": selected_class,
        "selected_day": selected_day,
        "selected_time": selected_time,
    })
