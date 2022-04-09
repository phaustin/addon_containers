FROM phaustin/base_addon:apr9

USER ${NB_USER}

RUN mkdir -p ${HOME}/dashdir

RUN touch ${HOME}/dashdir/version_apr_9.txt

RUN echo "conda activate ${CONDA_ENV}" >> ${HOME}/.bashrc

# Command to run this program
# CMD [ "gunicorn", "--workers=5", "--threads=1", "-b 0.0.0.0:8000", "app:server"]
CMD ["python", "app.py"]