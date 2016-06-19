## autopkg-ci

This project contains the components of a Jenkins setup for doing automated runs of [AutoPkg](https://github.com/autopkg/autopkg) recipes. I've since stopped maintaining this project, mainly because users tended to report broken recipes before this system was able to catch them (given a run frequency of every 8 hours). It's here as a reference of how to dynamically generate Jenkins jobs as well as how to run AutoPkg recipes in the context of a CI system, so that recipe failures could be caught and users notified.

There are two main reasons a recipe could break, and we'd like to be able to catch these early: 1) a software vendor changes their metadata feed, website, or whatever a recipe depends on to extract versions, and 2) changes in the AutoPkg code itself. We can detect breakages from AutoPkg code changes because we run AutoPkg out of Git.

## Job workflow

There exists a job for every that exists in the main AutoPkg [recipes](https://github.com/autopkg/recipes) repo. These jobs are generated automatically via a "seed" job that leverages the [Job DSL plugin](https://wiki.jenkins-ci.org/display/JENKINS/Job+DSL+Plugin). With a short script using this DSL, we can effectively template a job at a higher level than raw config XML and parameterize which actual recipe that will be run in addition to any other variables.

The jobs run on a randomized repeating 4-hour window, and essentially run one script, located in `steps/autopkg_run.py`, which does a run of a single recipe.

The run doesn't make use of shared AutoPkg preferences in order to keep isolated from one another, and instead explicitly uses temporary cache/Munki repo directories. It also tries to report the software version number of the result of the run, so that this information is a part of the build results.

## Plugin requirements

This setup requires at least the following plugins:

- JobDSL
- EmailExt
- EnvInject
- Multiple SCMs
- Git
- Build Description Setter
