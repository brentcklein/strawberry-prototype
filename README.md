# strawberry-prototype
Learning exercise for python strawberry-graphql library.

# Setup
clone repository:
```
git clone git@github.com:brentcklein/strawberry-prototype.git
```

install requirements (NOTE: strawberry requires python 3.7+):
```
cd strawberry-prototype
pip install requirements.txt
```

check typing with mypy:
```
mypy .
```

run ASGI server using `uvicorn`:
```
uvicorn app:app
```
