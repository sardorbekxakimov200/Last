## 1. 🧭 Clone the repository

```bash
git clone https://github.com/sardorbekxakimov200/Last.git
cd Last
````

---

## 2. 🐍 (Optional) Create and activate a virtual environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```



## 3. ⚙️ Apply database migrations

### Windows

```bash
python manage.py makemigrations
python manage.py migrate
```

### Linux / macOS

```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

---

## 4. 👤 Create a superuser (for admin access)

### Windows

```bash
python manage.py createsuperuser
```

### Linux / macOS

```bash
python3 manage.py createsuperuser
```

---

## 5. 🌐 Run the development server

### Windows

```bash
python manage.py runserver
```

### Linux / macOS

```bash
python3 manage.py runserver
```

Then open your browser and go to:

👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 🛠 Notes

* Make sure **Python 3.8+** is installed.
* Install dependencies inside a **virtual environment** to avoid version conflicts.
* Default admin panel URL: **[http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)**
* You can stop the server anytime with **Ctrl + C**.

