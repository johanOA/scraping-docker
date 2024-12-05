FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /scraping

# Instala las dependencias necesarias
RUN apt-get update && apt-get install -y bash cron

# Copia los archivos necesarios al contenedor
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY script.sh .
COPY prueba.sh .
COPY . .

# Permisos para hacerlos ejecutables
RUN chmod +x ./script.sh ./prueba.sh

# Configura las tareas de crontab
RUN echo "* * * * * bash /scraping/script.sh >> /scraping/script.log 2>&1" > /etc/cron.d/scraping-task
RUN echo "* * * * * bash /scraping/prueba.sh >> /scraping/prueba.log 2>&1" >> /etc/cron.d/scraping-task

RUN chmod 0644 /etc/cron.d/scraping-task

# Aplica el archivo de cron
RUN crontab /etc/cron.d/scraping-task



# Inicia cron y el contenedor
CMD ["cron", "-f"]
