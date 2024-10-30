FROM continuumio/miniconda3:latest

WORKDIR /app

# Copy the environment.yml file and create the conda environment
COPY environment.yml environment.yml
RUN conda env create -f environment.yml

# Set the shell to use the conda environment
SHELL ["conda", "run", "-n", "npmine_web_app", "/bin/bash", "-c"]

# Copy the application code
COPY . .

# Install Flask in the conda environment
RUN conda install -n npmine_web_app -c conda-forge flask

# Expose port 5000
EXPOSE 5000

# Set the command to initialize the database, run the population script, and start the app
CMD bash -c "if [ ! -d /app/migrations ]; then flask db init; fi && flask db upgrade && python populate_database.py && flask db upgrade && gunicorn --bind 0.0.0.0:5000 'websiteNPMINE:create_app()'"

