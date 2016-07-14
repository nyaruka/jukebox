JukeBox 
-----------

Django project that will manage the kLab music selection, via both web and SMS.

## Getting Started

These instructions are for Unix/OS X, you will have to modify these a bit to get going on Windows.  Consult your favorite Windows Python guru for details.

#### 1. Check out the repository:

```
  % git clone git://github.com/nyaruka/jukebox.git
  % cd jukebox
```

#### 2. Create a virtual environment and active it:

```  
  % virtualenv env
  % source env/bin/activate
```

#### 3. Initialize it with all the required libraries:

```   
  % pip install -r pip-requires.txt
```

#### 4. Initialize our database:

```
  % python manage.py makemigrations thumbnail
  % python manage.py migrate
```

#### 5. Start the server:

```
  % python manage.py runserver
```

You should now be able to load and interact with the jukebox webapp at: http://localhost:8000/