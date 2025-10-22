from datetime import datetime, time, timedelta
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Q
from .models import Pupil, TimeEntry

def session_times(session_index: int):
    if session_index < 1 or session_index > 8:
        raise ValueError("session_index must be between 1 and 8")
    start = datetime.combine(datetime.today(), time(hour=8, minute=30))
    current = start
    for s in range(1, session_index):
        current += timedelta(minutes=45)
        if s == 4:
            current += timedelta(minutes=45)
        else:
            current += timedelta(minutes=5)
    lesson_start = current.time()
    lesson_end_dt = (current + timedelta(minutes=45)).time()
    return lesson_start, lesson_end_dt

SESSION_RANGES = {i: session_times(i) for i in range(1, 9)}

WEEKDAY_TO_CODE = {
    0: 'mon',
    1: 'tue',
    2: 'wed',
    3: 'thu',
    4: 'fri',
}

def get_current_session(now_time):
    for i, (start, end) in SESSION_RANGES.items():
        if start <= now_time < end:
            return i
    return None

def pupil_now(request):     
    q = request.GET.get('q', '').strip()
    results = []
    message = ''
    now = timezone.localtime(timezone.now())
    weekday = now.weekday()
    day_code = WEEKDAY_TO_CODE.get(weekday)
    current_session = get_current_session(now.time())
    if current_session is None:
        message = f"No lesson right now. Current time {now.time().strftime('%H:%M')} is outside defined session ranges."
    elif not q:
        message = "SPECIAL-CASE"
    else:
        parts = q.split()
        if len(parts) < 2:
            message = "Please enter both first and last name for privacy reasons."
        else:
            first, last = parts[0], parts[-1]
            pupils = Pupil.objects.filter(
                first_name__iexact=first,
                last_name__iexact=last
            ).select_related('school_class')
            if not pupils.exists():
                message = "No pupil found with that full name."
            else:
                pupils_with_lessons = 0
                for pupil in pupils:
                    entries = TimeEntry.objects.filter(
                        day=day_code,
                        session=current_session,
                        school_class=pupil.school_class
                    ).select_related('subject', 'teacher').order_by('group')
                    formatted = []
                    for e in entries:
                        start, end = (
                            e.start_time or e.computed_start_end[0],
                            e.end_time or e.computed_start_end[1],
                        )
                        formatted.append({
                            'subject': str(e.subject),
                            'teacher': str(e.teacher),
                            'group': e.get_group_display(),
                            'start': start.strftime("%H:%M") if start else '',
                            'end': end.strftime("%H:%M") if end else '',
                        })
                    if formatted:
                        pupils_with_lessons += 1
                    results.append({
                        'pupil': f"{pupil.first_name} {pupil.last_name}",
                        'class': str(pupil.school_class),
                        'entries': formatted,
                    })
                if pupils_with_lessons == 0:
                    message = "This pupil is not in any lesson right now."
    context = {
        'query': q,
        'now': now,
        'day_code': day_code,
        'session': current_session,
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
            fake_date = datetime.strptime("2025-10-13", "%Y-%m-%d")
            hour, minute = map(int, selected_time.split(":"))
            now = fake_date.replace(hour=hour, minute=minute)
            entries = TimetableEntry.objects.filter(
                day=selected_day,
                school_class=selected_class,
                start_time__lt=now.time(),
                end_time__gte=now.time(),
            )
    return render(request, "timetable_simulator.html", {
        "classes": classes,
        "entries": entries,
        "selected_class": selected_class,
        "selected_day": selected_day,
        "selected_time": selected_time,
    })
