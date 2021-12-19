@call Scripts\activate
@set PYTHONPATH=%PYTHONPATH%;%~dp0;%~dp0\src\;%~dp0\sam-app\tests;
mypy src\composerstoolkit
if errorlevel 1 msg "%username%"  "Static type checking failed. Please review before pushing."
pylint --rcfile=.pylintrc composerstoolkit
if errorlevel 1 msg "%username%"  "Linting failed. Please review before pushing."
coverage run -m unittest discover tests
if errorlevel 1 msg "%username%"  "One or more tests failed. Please review these before pushing."
coverage html