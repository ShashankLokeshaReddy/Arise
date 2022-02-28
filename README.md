# ARISE prototype

Code for the ARISE prototype.

Status of Main:
[![pipeline status](https://gitlab.cc-asp.fraunhofer.de/arise-project/arise-prototype/badges/main/pipeline.svg)](https://gitlab.cc-asp.fraunhofer.de/arise-project/arise-prototype/-/commits/main)
[![coverage report](https://gitlab.cc-asp.fraunhofer.de/arise-project/arise-prototype/badges/main/coverage.svg)](https://gitlab.cc-asp.fraunhofer.de/arise-project/arise-prototype/-/commits/main)

## Starting the Django Server

Open the console and navigate into the folder `django_prototype` and (depending on your system) type `docker compose up`
or `docker-compose up`. To shutdown, open a separate terminal tab or window and type `docker compose down`
or `docker-compose down`
respectively.

## Code Metrics

If you want information about passed tests, test coverage, and linting, you can do so by creating a merge request. The
merge request will then contain the desired information:

![Merge-Request](attachments/merge-request.png)

As long as the merge request title begins with `Draft:`, it will not be merged. The test coverage can be viewed in the
diff (click on changes):

A line that has a hit or is just a definition:

![Coverage-1](attachments/test-coverage-1.png)

A line that is untested:

![Coverage-2](attachments/test-coverage-2.png)

# Installation local package

Gehe in den Ornder darüber und schreibe pip install -e arise-prototype importiere das package dann mit arise_prototype
Code for the ARISE prototype