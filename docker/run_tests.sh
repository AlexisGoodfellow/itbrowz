#!/usr/bin/env bash

set -e

BLACK_ACTION="--check"
ISORT_ACTION="--check-only"
TEST_DIRS="./tests"
COV_REPORT="--cov-report html"
IS_INTEGRATION_TEST="false"

function usage
{
    echo "usage: run_tests.sh [--format-code]"
    echo ""
    echo " --integration : Run integration tests in addition to unit tests."
    echo " --ci          : Do extra work to support CI pipeline."
    echo " --format-code : Format the code instead of checking formatting."
    exit 1
}

while [[ $# -gt 0 ]]; do
    arg="$1"
    case $arg in
        --integration)
        TEST_DIRS="./tests_integration"
        IS_INTEGRATION_TEST="true"
        ;;
        --format-code)
        BLACK_ACTION="--quiet"
        ISORT_ACTION="--apply"
        ;;
        --ci)
        COV_REPORT=""
        ;;
        -h|--help)
        usage
        ;;
        *)
        echo "Unexpected argument: ${arg}"
        usage
        ;;
        "")
        # ignore
        ;;
    esac
    shift
done

cat ~/.bashrc

# only generate html locally because the buildkite pipeline can't write to the
# working directory and writing to /tmp locally won't preserve the files after
# docker-compose run test
echo "Running pytest..."
if [[ "${IS_INTEGRATION_TEST}" == "true" ]]; then
  pytest -x -vv -c pytest-integration.ini ${TEST_DIRS} ${COV_REPORT}
else
  pytest -x -vv -c pytest.ini ${TEST_DIRS} ${COV_REPORT}

  echo "Running MyPy..."
  mypy itbrowz tests tests_integration

  echo "Running black..."
  black ${BLACK_ACTION} itbrowz tests tests_integration

  echo "Running flake8..."
  flake8 itbrowz tests tests_integration

  echo "Running bandit..."
  bandit --ini .bandit -r itbrowz

  echo "Running pydocstyle..."
  pydocstyle --config=.pydocstyle itbrowz

  echo "Running iSort..."
  isort --recursive ${ISORT_ACTION} itbrowz tests tests_integration
fi
