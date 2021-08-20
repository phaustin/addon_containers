FROM phaustin/base_image:aug07

USER ${NB_USER}

RUN mkdir -p ${HOME}/dashdir

COPY dashdir/ ${HOME}/dashdir/

RUN echo "conda activate ${CONDA_ENV}" >> ${HOME}/.bashrc

# Command to run this program
#CMD [ "gunicorn", "--workers=5", "--threads=1", "-b 0.0.0.0:8000", "app:server"]
CMD ["python", "app.py"]