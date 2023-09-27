#Import python
FROM python:3.10.8

#set working dir
WORKDIR /app

#copy contents to workdir
COPY . /app

#install dependencies/requirements
RUN pip install -r requirements.txt

#expose port for flask
EXPOSE 5000

#run app
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]


