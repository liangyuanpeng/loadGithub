FROM python:3.7
ADD load.py /job/load.py
RUN pip install sgqlc
RUN pip install pymongo
RUN pip install pylru
CMD ["python","/job/load.py"]