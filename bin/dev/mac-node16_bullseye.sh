#!/bin/bash
docker run -it --rm -v $(pwd)/../..:/docker -w /docker node:16-bullseye bash