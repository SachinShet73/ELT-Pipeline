# ELT Pipeline with Airflow, Airbyte, and dbt

A comprehensive Extract, Load, Transform (ELT) pipeline that demonstrates modern data engineering practices using Docker, Apache Airflow, Airbyte, and dbt with PostgreSQL databases.

## 🏗️ Architecture Overview

This pipeline implements an ELT (Extract, Load, Transform) pattern with the following components:

- **Source Database**: PostgreSQL with sample film and user data
- **Destination Database**: PostgreSQL for processed data
- **Orchestration**: Apache Airflow for workflow management
- **Data Integration**: Airbyte for data replication
- **Transformation**: dbt for data modeling and transformation
- **Containerization**: Docker and Docker Compose for easy deployment

## 📁 Project Structure

```
├── airflow/
│   └── dags/
│       └── etl_dag.py              # Airflow DAG definition
├── custom_postgres/                # dbt project
│   ├── macros/                     # dbt macros
│   ├── models/                     # dbt models
│   │   └── example/
│   │       ├── actors.sql
│   │       ├── films.sql
│   │       ├── film_actors.sql
│   │       ├── film_ratings.sql
│   │       └── specific_movie.sql
│   ├── dbt_project.yml
│   ├── profiles.yml
│   └── schema.yml
├── elt/
│   ├── Dockerfile
│   └── elt_script.py               # Legacy ELT script
├── source_db_init/
│   └── init.sql                    # Source database initialization
├── temporal/
│   └── dynamicconfig/
│       └── development.yaml        # Temporal configuration
├── docker-compose.yml              # Main Docker Compose file
├── airbyte-docker-compose.yml      # Airbyte services
├── start.sh                        # Startup script
└── stop.sh                         # Shutdown script
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- At least 8GB RAM available for containers
- Ports 5433, 5434, 8000, 8001, 8080 available

### 1. Clone and Start Services

```bash
# Make scripts executable
chmod +x start.sh stop.sh

# Start all services
./start.sh
```

### 2. Access the Applications

- **Airflow UI**: http://localhost:8080
  - Username: `airflow`
  - Password: `password`

- **Airbyte UI**: http://localhost:8000

### 3. Database Connections

**Source Database (PostgreSQL)**:
- Host: `localhost`
- Port: `5433`
- Database: `source_db`
- Username: `postgres`
- Password: `secret`

**Destination Database (PostgreSQL)**:
- Host: `localhost`
- Port: `5434`
- Database: `destination_db`
- Username: `postgres`
- Password: `secret`

## 🔄 Pipeline Workflow

### Current Implementation

The pipeline consists of three main stages:

1. **Extract & Load (Airbyte)**:
   - Connects to source PostgreSQL database
   - Replicates data to destination PostgreSQL database
   - Configured through Airbyte UI

2. **Transform (dbt)**:
   - Creates staging models from raw data
   - Applies business logic transformations
   - Generates film ratings with categorization
   - Combines film and actor information

3. **Orchestration (Airflow)**:
   - Manages pipeline execution
   - Triggers Airbyte sync jobs
   - Runs dbt transformations
   - Handles dependencies and scheduling

### Data Models

The dbt project includes several models:

- **actors.sql**: Raw actor data
- **films.sql**: Raw film data with ratings
- **film_actors.sql**: Film-actor relationships
- **film_ratings.sql**: Enhanced film data with rating categories and actor information
- **specific_movie.sql**: Example of parameterized queries

### Macros

- **generate_ratings()**: Categorizes user ratings into Excellent/Good/Average/Poor
- **generate_film_ratings()**: Complex macro combining films with actors and ratings

## 🛠️ Configuration

### Airbyte Setup

1. Access Airbyte UI at http://localhost:8000
2. Create source connection to PostgreSQL (port 5433)
3. Create destination connection to PostgreSQL (port 5434)
4. Set up sync connection between source and destination
5. Update the `CONN_ID` in `airflow/dags/etl_dag.py`

### dbt Configuration

The dbt profile is automatically configured to connect to the destination database. Models are materialized as tables by default.

### Airflow Configuration

- DAG runs daily starting from August 19, 2025
- Includes Docker operators for dbt execution
- Configured with PostgreSQL backend

## 📊 Sample Data

The source database includes:

- **Users**: 14 sample users with personal information
- **Films**: 20 popular movies with ratings and pricing
- **Film Categories**: Genre classifications
- **Actors**: Associated actors for each film
- **Film-Actor Relationships**: Many-to-many mapping

## 🔧 Development

### Running dbt Locally

```bash
# Navigate to dbt project
cd custom_postgres

# Install dependencies
dbt deps

# Run models
dbt run

# Run tests
dbt test

# Generate documentation
dbt docs generate
dbt docs serve
```

### Adding New Models

1. Create SQL files in `custom_postgres/models/`
2. Add model documentation in `schema.yml`
3. Define sources in `sources.yml`
4. Test your models with `dbt run`

### Custom Macros

Create reusable SQL code in `custom_postgres/macros/` and reference them in models using `{{ macro_name() }}`.

## 🧪 Testing

The project includes dbt tests for data quality:

- **Uniqueness**: Ensuring primary keys are unique
- **Not Null**: Validating required fields
- **Referential Integrity**: Checking foreign key relationships

Run tests with:
```bash
dbt test
```

## 🚨 Troubleshooting

### Common Issues

1. **Port Conflicts**: Ensure ports 5433, 5434, 8000, 8001, 8080 are available
2. **Memory Issues**: Increase Docker memory allocation to 8GB+
3. **Connection Issues**: Wait for all services to fully start (can take 2-3 minutes)

### Checking Logs

```bash
# View all service logs
docker-compose logs

# View specific service logs
docker-compose logs airflow
docker-compose logs airbyte-server
```

### Restarting Services

```bash
# Stop all services
./stop.sh

# Clean up volumes (optional - will delete data)
docker-compose down -v

# Restart
./start.sh
```

## 🛡️ Security Notes

- Default passwords are used for demonstration purposes
- In production, use environment variables for sensitive credentials
- Configure proper network security and access controls
- Enable SSL/TLS for database connections

## 📈 Monitoring

- Airflow provides built-in monitoring for DAG runs
- Airbyte tracks sync job success/failure rates
- dbt generates data lineage and documentation
- PostgreSQL logs available through Docker logs

## 🚀 Production Considerations

1. **Secrets Management**: Use proper secret management (HashiCorp Vault, AWS Secrets Manager)
2. **Resource Limits**: Configure appropriate CPU/memory limits
3. **Backup Strategy**: Implement database backup and recovery procedures
4. **Monitoring**: Add comprehensive logging and alerting
5. **Scaling**: Consider using Kubernetes for production deployments

