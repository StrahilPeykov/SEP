# CarbonInsight Backend

> **Automated Carbon Footprint Calculator with Digital Product Passport (DPP) generation for manufacturing SMEs**

CarbonInsight is a web-based application designed to help manufacturing Small and Medium-sized Enterprises (SMEs) calculate their Product Carbon Footprint (PCF) and generate standards-compliant Digital Product Passports. The application enables users to input manufacturing data, calculate PCF using standardized methodologies, and generate DPPs in Asset Administration Shell (AAS) format.

## 🌟 Features

### Core Functionality
- **Product Carbon Footprint Calculation** - Calculate PCF using IDTA-supported methodologies (ISO 14040/14044, ISO 14067, etc.)
- **Digital Product Passport Generation** - Generate standards-compliant DPPs in AASX, XML, and JSON formats
- **Supply Chain Data Management** - Handle supplier relationships and data sharing requests
- **Multi-format Import/Export** - Support for AASX, XML, JSON, CSV, XLSX, and PDF formats
- **SCSN Compatibility** - Generate SCSN-compatible payloads for supply chain integration

### Advanced Features
- **AI-Powered Recommendations** - Get AI-driven suggestions for carbon footprint reduction
- **Bill of Materials (BoM) Management** - Comprehensive product composition tracking
- **Emission Factor Database** - Reference libraries for materials, transport, and energy emissions
- **Multi-Company Support** - Manage multiple companies and user authorizations
- **Data Sharing Workflows** - Secure supplier data sharing with approval mechanisms

### Standards Compliance
- **ISO 14067** - Carbon footprint of products
- **Asset Administration Shell (AAS)** - IDTA specifications v0.9/v1.0
- **SCSN (Smart Connected Supplier Network)** - Supply chain data exchange
- **GDPR** - Data protection and privacy compliance

## 🏗️ Architecture

### Technology Stack
- **Backend Framework**: Django 5.2 + Django REST Framework
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: JWT tokens with django-rest-framework-simplejwt
- **API Documentation**: OpenAPI 3.0 with drf-spectacular
- **File Processing**: Import/Export with django-import-export
- **AI Integration**: OpenAI GPT-4 for recommendations
- **Standards Support**: basyx-python-sdk for AAS compliance

### Key Components
- **Models**: Polymorphic emission types, product hierarchies, company management
- **Serializers**: DRF serializers with nested relationship support
- **ViewSets**: RESTful API endpoints with comprehensive CRUD operations
- **Permissions**: Role-based access control with company membership validation
- **Exporters**: AAS and SCSN format generators
- **Importers**: AAS file validation and parsing

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd CarbonInsight
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
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

6. **Start development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - API Root: http://localhost:8000/api/
   - Admin Interface: http://localhost:8000/admin/
   - API Documentation: http://localhost:8000/api/schema/swagger-ui/

### Quick Setup with Test Data

For development and testing purposes:

```bash
# Populate database with sample companies and products
curl -X POST http://localhost:8000/api/populate_db/

# Login credentials:
# Email: admin@example.com
# Password: 1234567890
```

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/api/schema/swagger-ui/
- **ReDoc**: http://localhost:8000/api/schema/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

### Key API Endpoints

#### Authentication
```
POST /api/login/                    # Obtain JWT tokens
POST /api/token/refresh/            # Refresh access token
POST /api/register/                 # Register new user
```

#### Companies
```
GET    /api/companies/              # List all companies
POST   /api/companies/              # Create company
GET    /api/companies/my/           # List user's companies
GET    /api/companies/{id}/         # Company details
```

#### Products
```
GET    /api/companies/{id}/products/                    # List products
POST   /api/companies/{id}/products/                    # Create product
GET    /api/companies/{id}/products/{id}/               # Product details
GET    /api/companies/{id}/products/{id}/emission_traces/ # Get PCF data
```

#### Emissions
```
GET    /api/companies/{id}/products/{id}/emissions/transport/     # Transport emissions
GET    /api/companies/{id}/products/{id}/emissions/material/      # Material emissions
GET    /api/companies/{id}/products/{id}/emissions/production_energy/ # Production energy
GET    /api/companies/{id}/products/{id}/emissions/user_energy/   # User energy
```

#### Export/Import
```
GET    /api/companies/{id}/products/{id}/export/aas_aasx/   # Export as AASX
GET    /api/companies/{id}/products/{id}/export/aas_json/   # Export as JSON
POST   /api/companies/{id}/products/import/aas_aasx/       # Import from AASX
```

## 🧪 Testing

### Run All Tests
```bash
cd CarbonInsight
python manage.py test
```

### Run Specific Test Modules
```bash
python manage.py test core.tests.test_companies
python manage.py test core.tests.test_products
python manage.py test core.tests.test_dpp_api
```

### Test Coverage
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

### PyCharm Integration
This project includes PyCharm run configurations:
- **CarbonInsight**: Django development server
- **CarbonInsight Tests**: Test runner with coverage

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (for production)
DATABASE_URL=postgresql://user:password@localhost:5432/carboninsight

# OpenAI Integration (optional)
OPENAI_API_KEY=your-openai-api-key

# Security Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# External URLs
BASE_URL=https://carboninsight.win.tue.nl
```

### Production Deployment

For production deployment:

1. **Update database settings** in `settings.py`
2. **Set `DEBUG=False`** and configure `ALLOWED_HOSTS`
3. **Configure static files** serving
4. **Set up SSL/HTTPS** for secure communication
5. **Configure environment variables** for secrets

## 📊 Data Model

### Core Entities
- **User**: Authentication and user management
- **Company**: Multi-tenant company structure
- **Product**: Central product entity with metadata
- **Emission**: Polymorphic emission types (Material, Transport, Energy)
- **ProductBoMLineItem**: Bill of Materials relationships
- **ProductSharingRequest**: Supplier data sharing workflow

### Emission Types
- **MaterialEmission**: Raw material emissions with weight-based calculations
- **TransportEmission**: Transportation emissions (distance × weight × factor)
- **ProductionEnergyEmission**: Manufacturing energy consumption
- **UserEnergyEmission**: Product usage phase energy consumption

### Reference Data
- **EmissionReference**: Lookup tables for emission factors
- **LifecycleStage**: LCA stages (A1-A5, B1-B7, C1-C4, D)
- **ReferenceImpactUnit**: Units for emission calculations (kg, piece, kWh, etc.)

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the coding standards
4. Add or update tests as needed
5. Run the test suite (`python manage.py test`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Coding Standards
- Follow PEP 8 for Python code style
- Use type hints where applicable
- Write comprehensive docstrings for classes and methods
- Maintain test coverage above 80%
- Use meaningful commit messages

### Code Structure
```
CarbonInsight/
├── core/                    # Main application
│   ├── models/             # Data models
│   ├── serializers/        # DRF serializers
│   ├── views/              # API views and viewsets
│   ├── permissions.py      # Access control
│   ├── exporters/          # File export functionality
│   ├── importers/          # File import functionality
│   └── tests/              # Test suites
├── CarbonInsight/          # Django project settings
└── requirements.txt        # Python dependencies
```

## 📋 Project Status

This project is part of a Software Engineering Project (SEP) at TU/e, developed by Group 13 for the period April-June 2025. The application targets manufacturing SMEs needing to comply with upcoming EU regulations for carbon footprint reporting and digital product passports.

### Roadmap
- ✅ Core PCF calculation engine
- ✅ Digital Product Passport generation
- ✅ Multi-format import/export
- ✅ Supply chain data sharing
- ✅ AI recommendations integration
- 🔄 Advanced analytics dashboard
- 🔄 Mobile application support
- 🔄 Enterprise integrations (ERP/PLM)

## 📄 License

This project is part of an academic assignment at TU/e. Please refer to the project guidelines for usage and distribution terms.

## 🆘 Support

For questions and support:
- Check the [API Documentation](http://localhost:8000/api/schema/swagger-ui/)
- Review existing [Issues](https://github.com/your-repo/issues)
- Contact the development team

---

**Developed by**: TU/e Group 13  
**Supervisor**: Felipe de Azeredo Coutinho Xavier  
**Client**: Sara Manders, EU Project Manager at Brainport Industries