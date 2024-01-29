#!/bin/bash

docker_version=`docker-compose --version | grep -o [0-9]* | tr -d '\n'`
if [ "$docker_version" -ge "1270" ] ; then
    DOCKERCOMPOSE="docker-compose"
else
    DOCKERCOMPOSE="docker compose"
fi

echo "docker-compose command is $DOCKERCOMPOSE, version number $docker_version"

./make_env_files.sh
pwd
ls -al .env*
if [ "-d" tileserver ] ; then
    rm -rf tileserver
fi

if [ "-d" api_calculations_use_cases ] ; then
    rm -rf api_calculations_use_cases
fi


cp -r ../api_calculations_use_cases .
cp -r ../tileserver .


cp .env-tileserver tileserver/.env
cp .env-api api_calculations_use_cases/.env

docker build -t frontend_test:latest .

# frontend container needs to be rebuilt with our new environment variables in order to disable the orcid login
cp -r ../frontend .
cp .env-frontend frontend
cd frontend
cp .env-frontend .env
# call the new container something different

#turn off upgrade-insecure-requests since it breaks chrome
sed -i 's/<meta http-equiv="Content-Security-Policy" content="upgrade-insecure-requests">//' index.html

docker build -t docker-repo.bodc.me/oceaninfo/imfe-pilot/frontend:test .
docker run --rm -d -p 8080:80 --env-file .env-frontend --name frontend docker-repo.bodc.me/oceaninfo/imfe-pilot/frontend:test 

cd ../tileserver
$DOCKERCOMPOSE up -d

cd ../api_calculations_use_cases
$DOCKERCOMPOSE up -d
cd ..

docker ps
echo "FRONTEND_URL_LOCAL=http://localhost:8080/" > .env
#    - docker run --rm --net=host --env-file .env frontend_test:latest pytest tests/test_with_pytest.py::Test_URL::test_infobox tests/test_with_pytest.py::Test_URL::test_open_url tests/test_with_pytest.py::Test_URL::test_close_open_popup
docker run --rm --net=host --env-file .env frontend_test:latest /startup.sh
