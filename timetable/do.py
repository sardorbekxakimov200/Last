def do():
    from timetable.models import Class, TimeEntry, Teacher, Subject, Pupil
    from datetime import time

    # --- Classes ---
    cls5a, _ = Class.objects.get_or_create(number=5, letter='A')
    cls6a, _ = Class.objects.get_or_create(number=6, letter='A')
    cls7b, _ = Class.objects.get_or_create(number=7, letter='B')

    # --- Teachers ---
    t1, _ = Teacher.objects.get_or_create(first_name="Alice", last_name="Johnson")
    t2, _ = Teacher.objects.get_or_create(first_name="Mark", last_name="Stone")
    t3, _ = Teacher.objects.get_or_create(first_name="Sara", last_name="Lee")
    t4, _ = Teacher.objects.get_or_create(first_name="David", last_name="Nguyen")
    t5, _ = Teacher.objects.get_or_create(first_name="Emily", last_name="Harris")

    # --- Subjects ---
    subjects = {
        "math": Subject.objects.get_or_create(name="math")[0],
        "physics": Subject.objects.get_or_create(name="physics")[0],
        "chemistry": Subject.objects.get_or_create(name="chemistry")[0],
        "biology": Subject.objects.get_or_create(name="biology")[0],
        "english": Subject.objects.get_or_create(name="english")[0],
        "history": Subject.objects.get_or_create(name="history")[0],
        "geography": Subject.objects.get_or_create(name="geography")[0],
        "it": Subject.objects.get_or_create(name="it")[0],
    }

    # --- Pupils ---
    pupils = [
        ("John", "Smith", cls5a, '1'),
        ("Anna", "Brown", cls5a, '2'),
        ("Michael", "Green", cls6a, '1'),
        ("Lucy", "White", cls6a, '2'),
        ("Daniel", "Black", cls7b, '1'),
        ("Olivia", "Gray", cls7b, '2'),
    ]
    for fn, ln, cl, gr in pupils:
        Pupil.objects.get_or_create(first_name=fn, last_name=ln, school_class=cl, group=gr)

    # --- TimeEntries ---
    entries = [
        # Weekday lessons
        ("mon", cls5a, 1, "math", t1, "all"),
        ("mon", cls6a, 2, "english", t2, "all"),
        ("mon", cls7b, 3, "physics", t3, "all"),
        ("tue", cls5a, 4, "biology", t4, "all"),
        ("tue", cls6a, 5, "chemistry", t5, "all"),
        ("wed", cls7b, 6, "it", t2, "all"),
        ("thu", cls5a, 7, "geography", t3, "all"),
        ("fri", cls6a, 8, "history", t1, "all"),

        # Weekend lessons — to test Saturday/Sunday simulation
        ("sat", cls7b, 8, "biology", t3, "all"),
        ("sun", cls5a, 8, "english", t2, "all"),
        ("sun", cls6a, 8, "math", t1, "all"),
    ]

    for day, cl, sess, subj, teacher, group in entries:
        TimeEntry.objects.get_or_create(
            day=day,
            school_class=cl,
            session=sess,
            subject=subjects[subj],
            teacher=teacher,
            group=group,
            start_time=None,  # will be auto-computed
            end_time=None
        )

    print("✅ Sample timetable, pupils, and subjects successfully created!")
