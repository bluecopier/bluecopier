# TODO: Should come from project
FROM public.ecr.aws/lambda/python:3.11

# TODO: Should come from package manager abstraction
# COPY {runtime.package_files} .
COPY pyproject.toml .

# TODO: Generate .dockerignore
# TODO: Only copy over __version__.py
COPY . ${LAMBDA_TASK_ROOT}

# TODO: Should come from package manager abstraction
# RUN {runtime.install_packages(target=${LAMBDA_TASK_ROOT}")}
RUN pip3 install -e . --target "${LAMBDA_TASK_ROOT}"

ENV PYTHONPATH=${LAMBDA_TASK_ROOT}/src:$PYTHONPATH

# note: specific for this blueprint, could be abstracted
CMD ["handler.lambda_handler"]
