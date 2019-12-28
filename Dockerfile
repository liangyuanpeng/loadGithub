FROM loadgithub-base
ADD load.py /job/load.py
ADD conf/config.ini /conf/config.ini
ADD conf/config.ini /job/conf/config.ini
CMD ["python","/job/load.py"]