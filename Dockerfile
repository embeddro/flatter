FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN apt-get update -y && apt-get install -y libpq-dev python3-dev 

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

COPY . . 

ENTRYPOINT ["./entrypoint.sh"]

CMD ["avito_picker"]

