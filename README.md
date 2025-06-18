# CarbonInsight Backend

Welcome to the CarbonInsight backend repository! This project is designed to provide a robust backend solution for the CarbonInsight application, which focuses on carbon emissions tracking and analysis.

## Table of Contents
- [Running locally](#running-locally)
- [Running tests](#running-tests)

## Running locally
### PyCharm
This project has configuration files for one-click runs from PyCharm. Just open the project up in PyCharm, and click on the Play button in the top right corner. This will run the server for you.

### Terminal
To run the backend locally from a terminal, follow these steps:
1. Clone the repository
2. Navigate to the project directory
3. Install the required dependencies
```
pip install -r requirements.txt
```
4. Go to the CarbonInsight directory
```
cd CarbonInsight
```
5. Start the server
```
python manage.py runserver
```
6. Open your browser and navigate to `http://localhost:8000` to access the application.

## Running tests
To run the tests, follow these steps:
1. Ensure you have all the dependencies installed (as mentioned in the "Running locally" section).
2. Navigate to the CarbonInsight directory.
3. Run the tests using the following command:
```
python manage.py test
```