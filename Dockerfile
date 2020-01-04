FROM lgh-base
ADD *.py /job/
#ADD *.proto /job
CMD ["python","/job/load.py"]