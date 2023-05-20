FROM mambaorg/micromamba:latest as mamba
# Install IJava dependencies 
COPY --chown=$MAMBA_USER:$MAMBA_USER env.yaml /tmp/env.yaml
RUN micromamba install -y -f /tmp/env.yaml && \
    micromamba clean --all --yes
# Config to find executables
ARG MAMBA_DOCKERFILE_ACTIVATE=1
# Set up jupyterlab
#RUN jupyter lab build --dev-build=False --minimize=False
# Bootstrap environment
<<<<<<< HEAD
#WORKDIR /workspace
#EXPOSE 8888
=======
WORKDIR /workspace
EXPOSE 8888
CMD ["jupyter", "lab", "--ip=*", "--port=8888", "--no-browser", "--allow-root", "--LabApp.token=''"]
#CMD ["pyrhon", "./script.py"]
>>>>>>> 6ba6168619a45004032c5493ec81fee1792370dd
