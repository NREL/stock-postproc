FROM python:3.12

WORKDIR /app

# This will only ever shallow clone once, unless you run `docker build --no-cache ...`
RUN git clone --depth=1 -b deploy/std_plots https://github.com/NREL/resstock.git .

WORKDIR /app/postprocessing

RUN pip install --no-cache-dir --root-user-action=ignore uv \
  && uv sync

# Cache-bust layer
ARG CACHEBUST=1
RUN echo "cache bust: $CACHEBUST" > /dev/null

# Update the branch and dependencies
RUN git fetch --depth=1 origin deploy/std_plots \
  && git reset --hard FETCH_HEAD \
  && uv sync

CMD ["uv", "run", "resstockpostproc/standard_plots/dynamic_dashboard.py"]
