# Release process

This is a description of a source release process. This tutorial is meant to be for core developers oly. 

1. Branch the code with release version e.g. 0.7.3
2. Find all occurrences of old version e.g 0.7.3-dev and replace it with release version 0.7.3
3. Commit the code to the branch (0.7.3)
4. Checkout the master branch
5. Find all occurrences of old version e.g 0.7.3-dev and replace it with next development version 0.7.4-dev
6. Commit the code to the master branch
7. Check out the release version (e.g. 0.7.3) and run bash ./build.http to build the docker image.
