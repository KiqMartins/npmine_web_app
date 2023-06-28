# Base image
FROM continuumio/miniconda3:latest

# Set the working directory in the container
WORKDIR /app

# Copy the conda environment file
COPY environment.yml .

# Create and activate the conda environment
RUN conda env create -f environment.yml
RUN echo "source activate npmine_web_app" > ~/.bashrc
ENV PATH /opt/conda/envs/npmine_web_app/bin:$PATH

# Install PostgreSQL client
RUN apt-get update && apt-get install -y postgresql-client

# Copy the application code to the container
COPY . /app

# Set permissions for the init_db.sh script
RUN chmod +x /app/init_db.sh

# Expose the port on which the Flask app will run
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Command to run the Flask app
CMD ["flask", "run", "--host=0.0.0.0"]


