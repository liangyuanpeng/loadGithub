FROM python:3.7
ADD load.py /job/load.py
ADD conf/config.ini /conf/config.ini
ADD conf/config.ini /job/conf/config.ini
RUN pip install --upgrade pip
RUN pip install sgqlc
RUN pip install pymongo
#RUN pip install pylru
RUN pip install configparser
RUN pip install redis
CMD ["python","/job/load.py"]