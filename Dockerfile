FROM tiangolo/uwsgi-nginx:python3.8
RUN pip install flask
COPY . /mafia-app
ENV UWSGI_INI /mafia-app/uwsgi.ini
COPY ./requirements.txt /mafia-app/requirements.txt
WORKDIR /mafia-app
ENV PYTHONPATH=/mafia-app
RUN pip install -r /mafia-app/requirements.txt
