
FROM python:3
RUN mkdir /backend
WORKDIR /backend
ADD requirements.txt /backend/
ADD api.py /backend/
ADD ./* /backend/
RUN pip install -r requirements.txt
ADD * /backend/
EXPOSE 5000