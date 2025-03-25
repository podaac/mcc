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

cp ./../VERSION .

# cd ~/.aws
export AWS_CRED_FILE_DIR=$(pwd)
export ENV_TARGET=${ENV_TARGET}
export PROJECT_ID_TARGET="${1?Please define Testrail Project Id}"
export SUITE_ID_TARGET="${2?Please define Testrail Test Suite Id}"
export OPTIONAL_BEHAVE_PARAM="${3?Please use \"\" as placeholder if wanting to leave it empty}"
export MCC_BASEURL=${MCC_BASEURL}
export TESTRAIL_API_BASEURL=${TESTRAIL_API_BASEURL}
export TESTRAIL_USER=${TESTRAIL_USER}
export TESTRAIL_APIKEY=${TESTRAIL_APIKEY}

behave -D projectId=${PROJECT_ID_TARGET} -D suiteId=${SUITE_ID_TARGET} ${OPTIONAL_BEHAVE_PARAM} -D createReport=$4 -D browser=$5