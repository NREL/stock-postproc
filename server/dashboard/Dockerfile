FROM python:3.12

WORKDIR /app

# Cache-bust layer
ARG CACHEBUST=1
RUN echo "cache bust: $CACHEBUST" > /dev/null

ADD https://raw.githubusercontent.com/NREL/resstock/refs/heads/deploy/std_plots/postprocessing/resstockpostproc/standard_plots/dashboard.py ./dashboard.py

RUN pip install --no-cache-dir dash dash-bootstrap-components dash-extensions polars-lts-cpu

CMD ["python", "dashboard.py"]
