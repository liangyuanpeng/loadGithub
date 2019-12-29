FROM loadgithub-base
ADD load.py /job/load.python
CMD ["python","/job/load.py"]