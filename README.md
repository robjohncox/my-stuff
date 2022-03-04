# My Stuff

This repository contains a simple task manager that was built purely
to experiment with docker based development, along with trying out a
couple of python frameworks. This is probably not a good task manager
for actual use.

To develop and run the application, you require

* `make`
* `docker`
* `docker-compose`
* `python3`
* `virtualenv`

This was developed on Ubuntu 20 using Python 3.8, and has been tested
on MacOSX at some point in it's lifetime using Python 3.6.

## System configurations

There are two different configurations of the system:

- **dev** builds and runs a version of the system on a developers
  laptop which updates automatically when source code changes, and
  enables rapid testing of the system during development.
- **prod** builds and runs a production version of the system, which
  is used whenever we want to use a production like version of the
  system, including testing on a developers laptop, CI/CD and running
  the system in real environments.

## Developing individual services

The `services` directory contains a bunch of services which are
composed to create the whole system. Each service contains a
`Makefile` that specifies targets you can use when developing the
service. The typical targets are:

- **bootstrap** creates the virtual environment and install
  requirements.
- **format** reformats the code in a standard format.
- **lint** runs static analysis checks on the code.
- **test** runs the services automated tests.
- **clean** deletes the virtual environment.

You will notice there is nothing Docker-ish here, in my experiments
that when I wanted to focus on development of an individual service,
using a virtualenv to run automated tests in was a much faster
workflow than using docker. Docker really comes into it's own I think
when you want to run the application to test it.

## Building and testing the whole system

One of the major problems when developing a system composed of
multiple components (e.g. a web application with separate UI, API and
database components) is how you run it locally for testing - often
complex set up is required to test components in isolation, or to test
the system as a whole. However, Docker avoids this problem by making
it straightforward to specify how the system should be built and run
in different contexts, and makes it very straightforward to quickly
build and run the entire system on a developer's laptop. Testing the
system as a whole is preferable to testing individual components, you
get a much more realistic set up for testing by testing it as a whole,
especially with a Docker based system which allows you to easily spin
up realistic web servers and database servers.

As stated before, we have both dev and prod configurations, and it is
easy to build and run the application in either configuration
depending on what you want to do.

When working with the whole system, you want to change to the root
directory of the whole project; this is where the `Makefile` that
implements all the targets we refer to is found. We have limited the
makefile to targets which cover the most common operations we use when
testing the system, anyone working with this should look to become
familiar with `docker` and `docker-compose` for more fine-grained
control and debugging of the test applications.

### Testing using the dev configuration

The dev configuration is designed for quickly testing the application
whilst doing development. Each time it is run, it starts with a clean
database, and is therefore better suited to quick, ad-hoc tests. If
the source code is changed whilst it is running, it will update the
running software. The best way I found to use this configuration was
to have it running in the background whilst doing development (`make
dev-start`), so that you can very quickly access the UI in your
browser at

    http://localhost:5000
	
There are a number of targets for working with the dev configuration:

- **dev-build** performs a build of the dev system from scratch
- **dev-run** runs the system in the foreground
- **dev-start** starts the system in the background
- **dev-stop** stops the system in the background
- **dev-shell** opens a bash shell in the web container
- **dev-psql** opens a psql prompt in the db container

### Testing using the prod configuration

The prod configuration is how we run the application for real, and we
can run it in this configuration as part of development. The data is
persisted between runs, and `Makefile` targets are provided for
managing the data. The best way to use this configuration is for final
testing once a piece of development is complete.

There are equivalents for all the targets avaiable in the dev
configuration, and there are some additional targets we provide:

- **prod-data-init** Initialize a clean database, this must be run
  before running the application, and can be re-run at any time to get
  a clean database. The database contains some seed data.

The UI can be accessed in the browser at

	http://localhost:8000
