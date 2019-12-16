# strawberry-prototype
Learning exercise for python strawberry-graphql library.

# Setup
clone repository:
```
git clone git@github.com:brentcklein/strawberry-prototype.git
```

install requirements*:
```
cd strawberry-prototype
pip install -r requirements.txt
```

check typing with mypy:
```
mypy .
```

run ASGI server using `uvicorn`:
```
uvicorn app:app
```

view the test client at http://127.0.0.1:8000

*NOTE: strawberry requires python 3.7+. If you see the following error message:
```
ERROR: Could not find a version that satisfies the requirement requirements.txt (from versions: none)
ERROR: No matching distribution found for requirements.txt
```
that likely means you're on python <3.7.
