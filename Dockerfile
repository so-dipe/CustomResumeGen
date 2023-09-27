#Import python
FROM python:3.10.8

#set working dir
WORKDIR /app

#copy contents to workdir
COPY . /app

#install dependencies/requirements
RUN pip install -r requirements.txt

#expose port for flask
EXPOSE 80

#run app
CMD ["python", "run.py", "--host=0.0.0.0"]


