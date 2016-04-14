# README #

### What is this repository? ###

* This repository stores the changes made to the mrv system. It also contains branches for moving code to beta and eventually live.
* 2.0.1
* [Development Server](http://dev.carbon2markets.org)
* [Beta Server](http://beta.carbon2markets.org)
* [Live Server](http://fmrv2.carbon2markets.org)

### Branch Outline ###

* There are 3 main branches that will be used for moving code between our servers: nevis, beta, and master.
* Nevis Branch -- Stores the last stable version developed on NewNevis. This branch should match, or closely match the beta branch.
* Beta Branch -- The branch used to store code on the beta server. The beta server will pull from this branch only.
* Master Branch -- Holds the most stable version of the code. The live server will pull from the master branch. Nothing should be pushed to the master branch without approval of Jay Samek, Brian Jurgess, of Linda. All code should have gone through the beta server for testing.

### Contribution guidelines ###

* Writing tests
* Code review
* Other guidelines