@call Scripts\activate
@set PYTHONPATH=%PYTHONPATH%;%~dp0;%~dp0\src\;%~dp0\sam-app\tests;
REM mypy src\composerstoolkit
REM if errorlevel 1 msg "%username%"  "Static type checking failed. Please review before pushing."
REM pylint --rcfile=.pylintrc composerstoolkit
REM if errorlevel 1 msg "%username%"  "Linting failed. Please review before pushing."
coverage run -m unittest discover tests
if errorlevel 1 msg "%username%"  "One or more tests failed. Please review these before pushing."
coverage html --omit="tests/*,src/composerstoolkit/composers/*"
REM pydoctor src\composerstoolkit --html-output docs\