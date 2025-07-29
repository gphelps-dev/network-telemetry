FROM python:3.11-slim

WORKDIR /app
COPY . .

# 🔧 Install ping and traceroute
RUN apt-get update && apt-get install -y iputils-ping traceroute curl

RUN pip install --no-cache-dir -r requirements.txt

# Make the shell script executable
RUN chmod +x run_telemetry.sh

CMD ["./run_telemetry.sh"]
