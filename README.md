# CarbonInsight Backend

Welcome to the CarbonInsight backend repository! This project is designed to provide a robust backend solution for the CarbonInsight application, which focuses on carbon emissions tracking and analysis.
A comprehensive Django REST API for tracking and analyzing carbon emissions across supply chains, with support for Asset Administration Shell (AAS) standards and digital product passports.

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

### Key Features

- **Polymorphic Emissions**: Different emission types with specialized calculations
- **Reference Data**: Industry-standard emission factors for different processes
- **Lifecycle Stages**: Emissions categorized by standard lifecycle phases (A1-A3, B1-B7, C1-C4, D)
- **Override Factors**: Allow custom emission factors when precise data is available

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL (for production) or SQLite (for development)
- pip or pipenv for package management

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd CarbonInsight-backend
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

#### PyCharm
This project includes PyCharm run configurations. Simply open the project in PyCharm and click the Play button.

#### Terminal
```bash
cd CarbonInsight
python manage.py runserver
```

The API will be available at `http://localhost:8000`

### Quick Setup with Test Data

For development and testing:

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

### Key Endpoints

#### Authentication
- `POST /api/register/` - User registration
- `POST /api/login/` - Login (JWT tokens)
- `POST /api/token/refresh/` - Refresh access token

#### Companies & Products
- `GET /api/companies/` - List companies
- `GET /api/companies/{id}/products/` - Company products
- `GET /api/companies/{id}/products/{id}/emission_traces/` - Product carbon footprint

#### Emissions Management
- `GET /api/companies/{id}/products/{id}/emissions/transport/` - Transport emissions
- `GET /api/companies/{id}/products/{id}/emissions/production_energy/` - Production emissions
- `GET /api/companies/{id}/products/{id}/emissions/user_energy/` - User energy emissions

#### Data Export
- `GET /api/companies/{id}/products/{id}/export/aas_aasx` - Export to AAS AASX
- `GET /api/companies/{id}/products/{id}/export/scsn_full_xml` - Export to SCSN XML
- `GET /api/companies/{id}/products/export/csv` - Export products to CSV

#### Data Import
- `POST /api/companies/{id}/products/import/aas_aasx` - Import from AAS AASX
- `POST /api/companies/{id}/products/import/tabular` - Import from CSV/XLSX

## Testing

Run the test suite:

```bash
cd CarbonInsight
python manage.py test
```

### Test Coverage

The project includes comprehensive tests with coverage reporting:

```bash
# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

Coverage configuration is in `CarbonInsight/.coveragerc`.

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Django secret key | Auto-generated |
| `DATABASE_URL` | PostgreSQL connection string | SQLite (dev) |
| `OPENAI_API_KEY` | OpenAI API key for AI features | None |
| `RAILWAY_ENVIRONMENT_NAME` | Railway deployment environment | None |
| `FRONTEND_DOMAIN` | Frontend domain for CORS | localhost:3000 |

### Database Configuration

- **Development**: SQLite (`db.sqlite3`)
- **Production**: PostgreSQL (Railway.app)

### Security Settings

Production deployments include:
- HTTPS enforcement
- HSTS headers
- Secure cookies
- CSRF protection
- Rate limiting (django-axes)

## Data Standards

### Asset Administration Shell (AAS)
- Full AAS Digital Nameplate submodel support
- Product Carbon Footprint submodel compliance
- Export to AASX, XML, and JSON formats
- Import validation using aas-test-engines

### SCSN (Supply Chain Sustainability Network)
- UBL-compliant XML export
- Product Carbon Footprint data exchange
- Bill of Materials representation

### Lifecycle Stages
Based on EN 15804 and similar standards:
- **A1-A5**: Product stage (raw materials, transport, production, installation)
- **B1-B7**: Use stage (operation, maintenance, repair, replacement)
- **C1-C4**: End-of-life stage (deconstruction, transport, processing, disposal)
- **D**: Benefits and loads beyond system boundary

## Security Features

- JWT authentication with refresh tokens
- Rate limiting and account lockout protection
- Audit logging for all changes
- Company-based access control
- Product sharing request workflow
- Input validation and sanitization

## Deployment

### Railway.app (Recommended)

The project is configured for Railway deployment:

1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on push to main branch

Configuration is in `railway.toml`.

### Manual Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Collect static files
cd CarbonInsight
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Start with Gunicorn
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

### Code Style

- Follow Django best practices
- Use type hints where possible
- Write comprehensive docstrings
- Maintain test coverage above 80%

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues:

1. Check the [API documentation](http://localhost:8000/api/schema/swagger-ui/)
2. Review existing GitHub issues
3. Create a new issue with detailed description
4. For urgent production issues, contact the development team

## Related Projects

- **CarbonInsight Frontend**: React-based web application
- **AAS Standards**: [Asset Administration Shell specifications](https://www.plattform-i40.de/SiteGlobals/IP/Forms/Listen/Downloads/EN/Downloads_Formular.html)
- **SCSN**: [Supply Chain Sustainability Network](https://scsn.nl/)

---

**Built for sustainable supply chains**