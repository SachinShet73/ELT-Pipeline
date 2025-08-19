# Airbyte Setup Instructions

The Airbyte Docker Compose integration has been simplified to avoid complex dependency issues. 

## Current Status
- **Attempted**: Multiple complex configurations with temporal, bootloader, and multiple services
- **Issue**: Version compatibility and dependency chain problems between services
- **Resolution**: Use standalone Airbyte installation method

## Recommended Setup Method

### Option 1: Official Airbyte Docker Installation (Recommended)

1. **Clone the official Airbyte repository:**
   ```bash
   git clone https://github.com/airbytehq/airbyte.git
   cd airbyte
   ```

2. **Run the official setup script:**
   ```bash
   ./run-ab-platform.sh
   ```

3. **Access Airbyte:**
   - Web UI: http://localhost:8000
   - Default credentials: airbyte/password

### Option 2: Docker Run Method (Simple)

```bash
# Run Airbyte as a single container (for development)
docker run -it --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /tmp/airbyte_local:/tmp/airbyte_local \
  -p 8000:8000 \
  airbyte/quickstart:latest
```

### Option 3: Add to Current Docker Compose (Manual Integration)

If you want to integrate with your existing setup:

1. Follow Option 1 first to get Airbyte running
2. Note the successful configuration from the official repository
3. Manually merge the working configuration into your docker-compose.yml

## Integration with Your ELT Pipeline

Once Airbyte is running:

1. **Configure Source Connection**: Connect to your source PostgreSQL (port 5433)
2. **Configure Destination**: Connect to your destination PostgreSQL (port 5434) 
3. **Create Sync**: Set up data pipeline between source and destination
4. **Airflow Integration**: Use Airbyte operators in your Airflow DAGs

## Current ELT Pipeline Status

- ✅ **Source PostgreSQL**: Running on port 5433
- ✅ **Destination PostgreSQL**: Running on port 5434
- ✅ **Airflow**: Running on port 8080
- 🔧 **Airbyte**: Follow instructions above to set up

## Network Configuration

All services use the `elt_network` Docker network, so they can communicate with each other using service names:
- `source_postgres:5432` (internal)
- `destination_postgres:5432` (internal)  
- `airflow:8080` (internal)