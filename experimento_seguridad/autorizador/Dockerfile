
FROM python:3
RUN mkdir /backend
WORKDIR /backend
ADD requirements.txt /backend/
ADD app.py /backend/
ADD ./* /backend/
COPY attemps /backend/attemps/
COPY events /backend/events/
COPY models /backend/models/
COPY views /backend/views/
RUN pip install -r requirements.txt
ADD * /backend/
EXPOSE 5000