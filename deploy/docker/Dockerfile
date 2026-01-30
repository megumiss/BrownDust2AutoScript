# docker build -t nkas:latest .
# docker run -v ${PWD}:/app/BrownDust2AutoScript -p 12283:12283 --name nkas -it --rm bd2as

FROM python:3.10-slim-bookworm

WORKDIR /app/BrownDust2AutoScript

COPY requirements.txt /tmp/requirements.txt

# Initial download of UiAutomator2 is slow outside of China using appetizer mirror, switch to GitHub
RUN apt update \
 && apt install -y git adb libgomp1 openssh-client libgl1 libglib2.0-0 libsm6\
 && git config --global --add safe.directory '*' \
 && pip install -r /tmp/requirements.txt \
 && rm /tmp/requirements.txt \
 && rm -r ~/.cache/pip

CMD python gui.py