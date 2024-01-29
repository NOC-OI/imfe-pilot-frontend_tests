# Frontend-test

- This is a repository for applying two integration tests

- For every new feature implemented on the site, a new repository integration test should be included.

- The tests are based on no pytest along with selenium

## INSTALL

Go to `https://git.noc.ac.uk/ocean-informatics/imfepilot/frontend-test` to see the project, manage issues, setup you ssh public key, ...

Create a python3 virtualenv and activate it:

```bash
pyenv virtualenv frontend_test
```

Clone the project and install it:

```bash
git clone  git@git.noc.ac.uk:ocean-informatics/imfepilot/frontend-test.git
cd frontend-test
pyenv local frontend_test
pip install -e .
```
## TESTS

- The tests are listed in the file tests/test_with_pytest.py
### Apply test

- To run all tests, use or following command:

```bash
make test
```

- If you want to apply a specific test, use or following command:

```bash
pytest --verbose --capture=no tests/test_with_pytest.py::Test_URL::{TEST_NAME}
```
In this case, substitute {TEST_NAME} for the name of the test function in the test file.

### Important

You need to set the following environment variables:
- FRONTEND_URL: the URL of the public website
- FRONTEND_URL_LOCAL: the URL of the localhost website

Please save then on a .env file on the root of the ropository, as the example below:

```
FRONTEND_URL=https://imfe-pilot.noc.ac.uk/
FRONTEND_URL_LOCAL=https://localhost:8080/
```

If you want to run the tests in a serveless mode, you need to add one more env variable to the .ENV file:

```
SELENIUM_MODE=HEADLESS
```

## RUN THE SERVER AS A DOCKER COMPOSE

First, you need to build the docker image:

```bash
docker build --progress=plain -t frontend_test .
```
Then, you can pass run the tests on the container:

```bash
docker run --net=host frontend_test make test
```
