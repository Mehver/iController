docker run -it --rm -p 3000:3000 -v %cd%\..\..:/docker -w /docker python:3.10-bullseye bash -c "pip install -r requirements.txt; exec bash"