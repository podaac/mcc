#!/bin/sh

if [ -f "./.env" ]
then
   echo ".env file found"
   source ./.env
else
   echo ".env file not found. create it or link to an existing .env file to execute properly."
   exit 1
fi

if [[ -z "${ENV_TARGET}" ]]; then
  echo ERROR: missing ENV_TARGET environment variable
  exit 1 # terminate and indicate error
fi

if [[ -z "${NETRC_PATH}" ]]; then
  echo ERROR: missing NETRC_PATH environment variable
  exit 1 # terminate and indicate error
fi

if [[ -z "${MCC_BASEURL}" ]]; then
  echo ERROR: Missing MCC_BASEURL environment variable
  exit 1 # terminate and indicate error
fi

if [[ -z "${TESTRAIL_API_BASEURL}" ]]; then
  echo ERROR: Missing TESTRAIL_API_BASEURL environment variable
  exit 1 # terminate and indicate error
fi

if [[ -z "${TESTRAIL_USER}" ]]; then
  echo ERROR: Missing TESTRAIL_USER environment variable
  exit 1 # terminate and indicate error
fi

if [[ -z "${TESTRAIL_APIKEY}" ]]; then
  echo ERROR: Missing TESTRAIL_APIKEY environment variable
  exit 1 # terminate and indicate error
fi

if [[ -z "${ARTIFACTORY_BASEURL}" ]]; then
  echo ERROR: Missing ARTIFACTORY_BASEURL environment variable
  exit 1 # terminate and indicate error
fi


cp ./../VERSION .

export pwd=$(pwd)
export PROJECT_ID_TARGET="${1?Please define Testrail Project Id}"
export SUITE_ID_TARGET="${2?Please define Testrail Test Suite Id}"
export OPTIONAL_BEHAVE_PARAM="${3?Please use \"\" as placeholder if wanting to leave it empty}"

cd $pwd

DOCKER_TAG="latest"
DOCKER_PATH="${ARTIFACTORY_BASEURL}/podaac/test/python-behave-test"

docker pull ${DOCKER_PATH}:${DOCKER_TAG}
docker run -u root -i \
  -v ${pwd}:/podaac/test:rw \
  -v ${NETRC_PATH}:/home/seluser/.netrc \
  -e ENV_TARGET=${ENV_TARGET} \
  -e MCC_BASEURL=${MCC_BASEURL} \
  -e TESTRAIL_API_BASEURL=${TESTRAIL_API_BASEURL} \
  -e TESTRAIL_USER=${TESTRAIL_USER} \
  -e TESTRAIL_APIKEY=${TESTRAIL_APIKEY} \
  ${DOCKER_PATH}:${DOCKER_TAG} /bin/bash -c \
    "cd /podaac/test &&
    pip3 list &&
    behave -D projectId=${PROJECT_ID_TARGET} -D suiteId=${SUITE_ID_TARGET} ${OPTIONAL_BEHAVE_PARAM} -D createReport=$4 -D browser=$5"

docker rm -v $(docker ps -a -q -f status=exited)
