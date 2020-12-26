FROM tiangolo/meinheld-gunicorn:python3.8
RUN pip install flask
COPY . /mafia-app
ENV UWSGI_INI /mafia-app/uwsgi.ini
COPY ./requirements.txt /mafia-app/requirements.txt
WORKDIR /mafia-app
ENV PYTHONPATH=/mafia-app
ENV PORT 5000
ENV HOST 0.0.0.0
ENV BIND 0.0.0.0:5000
EXPOSE 5000
RUN pip install -r /mafia-app/requirements.txt
