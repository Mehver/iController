#!/bin/bash
docker run -it --rm -p 3000:3000 -v $(pwd)/../..:/docker -w /docker node:16-bullseye bash