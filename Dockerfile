# install python on docker image
# using v3.9.16 for open-source gis libraries
FROM python:3.9.alpine

# make working directory
RUN mkdir -p /app

# copy all content to the docker image (including requirements.txt)
COPY . /app

# copy the requirements file into the image
# COPY ./requirements.txt ./app/requirements.txt

# switch working directory
WORKDIR /app

# install dependencies
RUN pip install -r requirements.txt

# listen on port 2000 by default
# this is the same port that the flask app uses
# where does this go in the dockerfile?
EXPOSE 8080

# run the application in the container
# do we need this?
ENTRYPOINT ["python"]

# run the app
CMD ["app.py"]