find . -maxdepth 3 -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -maxdepth 3 -path "*/migrations/*.pyc"  -delete