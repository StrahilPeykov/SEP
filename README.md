# CarbonInsight Backend

A comprehensive Django REST API for tracking and analyzing carbon emissions across supply chains, with support for Asset Administration Shell (AAS) standards and digital product passports.

🌐 **Live Demo**: [https://www.carboninsight.strahilpeykov.com/](https://www.carboninsight.strahilpeykov.com/)

## Overview

CarbonInsight helps companies track, calculate, and reduce their carbon footprint across complex supply chains. Built for SMEs who need accessible tools for Product Carbon Footprint (PCF) calculations and Digital Product Passport (DPP) creation using open standards like Asset Administration Shell (AAS).

## Features

- **Supply Chain Emissions Tracking**: Track carbon emissions across complex product Bill of Materials (BoM)
- **Multiple Emission Types**: Support for transport, production energy, and user energy emissions
- **Standards Compliance**: Export to Asset Administration Shell (AAS) formats (AASX, XML, JSON)
- **SCSN Integration**: Export Product Carbon Footprint data in SCSN XML format
- **Company & Product Management**: Multi-tenant architecture with company-based product ownership
- **Data Sharing**: Request and approve access to supplier emission data
- **Import/Export**: Bulk import/export via CSV, XLSX, and standardized formats
- **AI Recommendations**: OpenAI-powered suggestions for emission reduction
- **Audit Logging**: Complete audit trail of all changes
- **Authentication**: JWT-based authentication with rate limiting

## Tech Stack

- **Backend**: Django 5.0, Django REST Framework
- **Database**: PostgreSQL (production), SQLite (development)
- **Authentication**: JWT tokens with SimpleJWT
- **Standards**: AAS (Asset Administration Shell), SCSN (Smart Connected Supplier Network)
- **AI**: OpenAI integration for recommendations
- **Deployment**: Railway.app, Vercel compatible

## Architecture

### Core Models

- **Company**: Organizations that own products and manage users
- **Product**: Items with associated emissions and Bill of Materials
- **Emission**: Abstract base for different emission types:
  - `TransportEmission`: Shipping and logistics emissions
  - `ProductionEnergyEmission`: Manufacturing energy consumption
  - `UserEnergyEmission`: End-user energy consumption
- **ProductBoMLineItem**: Bill of Materials relationships between products
- **ProductSharingRequest**: Mechanism for requesting access to supplier emission data

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL (for production) or SQLite (for development)
- pip for package management

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/StrahilPeykov/carboninsight-backend.git
   cd carboninsight-backend
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment setup**
   ```bash
   # Copy and configure environment variables
   export DJANGO_SECRET_KEY="your-secret-key"
   export DATABASE_URL="your-database-url"  # Optional for production
   export OPENAI_API_KEY="your-openai-key"  # Optional for AI features
   ```

4. **Database setup**
   ```bash
   cd CarbonInsight
   python manage.py migrate
   ```

5. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

### Running the Server

```bash
cd CarbonInsight
python manage.py runserver
```

The API will be available at `http://localhost:8000`

### Quick Setup with Test Data

```bash
# Populate database with sample companies, users, and products
POST http://localhost:8000/api/populate_db/
# Login: admin@example.com / 1234567890

# Clean database when needed
POST http://localhost:8000/api/destroy_db/
```

## API Documentation

- **Swagger UI**: `http://localhost:8000/api/schema/swagger-ui/`
- **ReDoc**: `http://localhost:8000/api/schema/redoc/`
- **OpenAPI Schema**: `http://localhost:8000/api/schema/`

## Testing

```bash
cd CarbonInsight
python manage.py test

# With coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## Deployment

### Railway.app (Current)

The project is configured for Railway deployment with automatic deployment from the main branch.

### Manual Deployment

```bash
pip install -r requirements.txt
cd CarbonInsight
python manage.py collectstatic --noinput
python manage.py migrate
gunicorn CarbonInsight.wsgi:application --bind 0.0.0.0:8000
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`python manage.py test`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Django secret key | Auto-generated |
| `DATABASE_URL` | PostgreSQL connection string | SQLite (dev) |
| `OPENAI_API_KEY` | OpenAI API key for AI features | None |
| `RAILWAY_ENVIRONMENT_NAME` | Railway deployment environment | None |
| `FRONTEND_DOMAIN` | Frontend domain for CORS | localhost:3000 |

## Standards Compliance

### Asset Administration Shell (AAS)
- Full AAS Digital Nameplate submodel support
- Product Carbon Footprint submodel compliance
- Export to AASX, XML, and JSON formats

### SCSN (Supply Chain Sustainability Network)
- UBL-compliant XML export
- Product Carbon Footprint data exchange
- Bill of Materials representation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built in collaboration with Brainport Industries & TU Eindhoven
- Supports Dutch government and European Commission initiatives for Digital Product Passports
- Implements OPC Foundation Asset Administration Shell standards

## Contact

- **Author**: Strahil Peykov
- **Live Demo**: [https://www.carboninsight.strahilpeykov.com/](https://www.carboninsight.strahilpeykov.com/)
- **Issues**: [GitHub Issues](https://github.com/StrahilPeykov/carboninsight-backend/issues)

---

**Empowering SMEs to create sustainable supply chains through accessible carbon footprint tracking and standards-compliant digital product passports.**