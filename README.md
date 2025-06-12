# CarbonInsight Backend

> **Automated Carbon Footprint Calculator with Digital Product Passport (DPP) generation for manufacturing SMEs**

CarbonInsight is a comprehensive full-stack web application developed as a Bachelor's End Project for Brainport Industries. This repository contains the **Django REST API backend** that powers the system, working in conjunction with a Next.js frontend to enable manufacturing Small and Medium-sized Enterprises (SMEs) to calculate their Product Carbon Footprint (PCF), manage supply chain emissions data, and generate standards-compliant Digital Product Passports for regulatory compliance and ESG reporting.

## Full-Stack Architecture

**Frontend**: Next.js web application (separate repository)  
**Backend**: Django REST API (this repository)  
**Database**: PostgreSQL (production) / SQLite (development)  
**Integration**: RESTful API communication between frontend and backend

## Key Features Relevant to Environmental & Cost Analytics

### **Environmental Footprint Calculation Engine**
- **Multi-dimensional PCF calculation** across complete product lifecycles following **EN 15804** and **EN 15978** standards:
  - **A1-A5**: Product and Construction stages (raw materials, transport, manufacturing, installation)
  - **B1-B7**: Use stage (maintenance, repair, replacement, operational energy/water)
  - **C1-C4**: End-of-life stage (demolition, transport, waste processing, disposal)
  - **D**: Benefits beyond system boundary (reuse, recycling potential)
- **Polymorphic emission tracking** for materials, transport, production energy, and user energy
- **Real-time aggregation** of emissions data across complex supply chains
- **Standards compliance** with ISO 14067, ISO 14040/14044, EN 15804, EN 15978, and IDTA specifications

### **Data Modeling & Analytics Infrastructure**
- **Hierarchical data structures** for multi-tenant company and product relationships
- **Audit trail system** with comprehensive change tracking and compliance logging
- **RESTful API architecture** designed for dashboard integration and real-time monitoring
- **Flexible data export** in multiple formats (JSON, XML, CSV, XLSX) for analytics pipelines

### **Cost & Resource Visibility Features**
- **Bill of Materials (BoM) tracking** with quantity-based cost modeling potential
- **Resource consumption mapping** (energy, materials, transport) across product lifecycles
- **Multi-company data segregation** enabling cost allocation and cross-tenant analytics
- **Supplier relationship management** with data sharing approval workflows

## Technical Architecture

### **Backend Technology Stack**
```python
# Core Framework
Django 5.2 + Django REST Framework 3.16
PostgreSQL/SQLite with polymorphic model inheritance
JWT-based authentication with role-based access control

# Standards Integration
basyx-python-sdk (Asset Administration Shell compliance)
AAS test engines for validation
ISO 14067/14040 methodology implementation
EN 15804/15978 lifecycle stage definitions
ECLASS 15 with IRDI classification codes

# Analytics & Integration
OpenAI GPT-4 integration for sustainability recommendations
Import/Export engine with fuzzy matching for data ingestion
Multi-format file processing (AASX, XML, JSON, CSV, XLSX)

# Additional Libraries
django-polymorphic (inheritance patterns)
django-import-export (data pipeline)
drf-spectacular (OpenAPI documentation)
django-axes (security)
django-countries (internationalization)
```

### **Data Model Architecture**
```
Companies (Multi-tenant)
├── Products (Hierarchical BoM)
│   ├── MaterialEmissions (kg-based calculations)
│   ├── TransportEmissions (tkm-based calculations)
│   ├── ProductionEnergyEmissions (kWh-based calculations)
│   └── UserEnergyEmissions (lifecycle energy consumption)
├── Users (Role-based access)
└── AuditLogs (Compliance tracking)
```

## Quick Start

### Prerequisites
- Python 3.12+
- Git
- Virtual environment support

### Installation & Setup
```bash
# Clone and setup environment
git clone <repository-url>
cd CarbonInsight
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies and setup database
pip install -r requirements.txt
cd CarbonInsight
python manage.py migrate

# Start development server
python manage.py runserver

# Access points:
# API Root: http://localhost:8000/api/
# Interactive Documentation: http://localhost:8000/api/schema/swagger-ui/
# Admin Interface: http://localhost:8000/admin/
```

### Quick Demo Setup
```bash
# Populate with sample data for testing
curl -X POST http://localhost:8000/api/populate_db/

# Login credentials for testing:
# Email: admin@example.com
# Password: 1234567890
```

## API Endpoints for Analytics Integration

### **Environmental Metrics APIs**
```bash
# Product-level emissions data
GET /api/companies/{id}/products/{id}/emission_traces/
# Returns comprehensive carbon footprint with lifecycle breakdown

# Company-level aggregation
GET /api/companies/{id}/products/
# Filterable list with emission totals for portfolio analysis

# Audit trail for compliance
GET /api/companies/{id}/audit/
GET /api/companies/{id}/products/{id}/audit/
```

### **Data Export for Dashboard Integration**
```bash
# Structured data exports
GET /api/companies/{id}/products/export/csv/
GET /api/companies/{id}/products/export/xlsx/
GET /api/companies/{id}/products/{id}/emissions/transport/export/csv/

# Standards-compliant formats
GET /api/companies/{id}/products/{id}/export/aas_json/
GET /api/companies/{id}/products/{id}/export/scsn_full_xml/
```

### **Multi-format Import Pipeline**
```bash
# Automated data ingestion
POST /api/companies/{id}/products/import/tabular/
POST /api/companies/{id}/products/import/aas_aasx/
POST /api/companies/{id}/products/{id}/emissions/transport/import/tabular/
```

## Key Technical Implementations

### **Environmental Calculation Engine**
```python
# Polymorphic emission calculation with lifecycle tracking
class Emission(PolymorphicModel):
    def get_emission_trace(self) -> EmissionTrace:
        # Real-time calculation with override support
        # Aggregates biogenic/non-biogenic emissions
        # Provides audit trail and data lineage

# Hierarchical product emissions with BoM support
class Product(models.Model):
    def get_emission_trace(self) -> EmissionTrace:
        # Recursive calculation across supply chain
        # Handles data sharing permissions
        # Aggregates component-level emissions
```

### **Multi-tenant Data Architecture**
```python
# Company-based data segregation
class ProductPermission(BasePermission):
    def has_permission(self, request, view):
        # Role-based access control
        # Cross-company data sharing workflows
        # Audit logging for compliance

# Flexible reference data management
class EmissionReference(models.Model):
    # Standardized emission factors
    # Lifecycle stage mapping
    # Multi-company reference sharing
```

### **Analytics-Ready Data Structures**
```python
# Comprehensive emission tracing
@dataclass
class EmissionTrace:
    emissions_subtotal: Dict[LifecycleStage, EmissionSplit]
    children: Set[EmissionTraceChild]
    mentions: List[EmissionTraceMention]
    
    @property
    def total_biogenic(self) -> float
    def total_non_biogenic(self) -> float
    def total(self) -> float
```

## Relevance to Cloud Cost & Environmental Footprint Analysis

### **Direct Applications**
- **Environmental Metrics Modeling**: Proven experience building complex environmental calculation engines
- **Multi-tenant Cost Allocation**: Architecture supporting cost segregation across business units
- **Real-time Data Aggregation**: APIs designed for dashboard consumption and monitoring
- **Compliance & Audit Systems**: Built-in audit trails for ESG reporting requirements

### **Transferable Technical Skills**
- **Data Pipeline Architecture**: Import/export systems handling multiple file formats
- **Standards Integration**: Experience with industry standards (ISO, IDTA) applicable to cloud cost standards
- **API Design for Analytics**: RESTful endpoints optimized for dashboard and reporting consumption
- **Resource Consumption Tracking**: Emission calculations translatable to cloud resource usage patterns

### **ESG & Sustainability Experience**
- **Carbon Footprint Calculation**: Deep understanding of environmental impact measurement
- **Supply Chain Analytics**: Multi-company data relationships similar to cloud service dependencies
- **Regulatory Compliance**: ISO 14067/14040 compliance experience applicable to ESG reporting
- **AI-Powered Optimization**: Integration of AI recommendations for resource optimization

## Project Structure

```
CarbonInsight/
├── core/                    # Main application
│   ├── models/             # Data models (polymorphic emissions, products, companies)
│   ├── serializers/        # DRF serializers for API responses
│   ├── views/              # API views and viewsets
│   ├── permissions.py      # Role-based access control
│   ├── exporters/          # AAS, SCSN, ZIP export functionality
│   ├── importers/          # AAS file validation and parsing
│   ├── resources/          # Import/export resource definitions
│   └── tests/              # Comprehensive test suites
├── CarbonInsight/          # Django project settings
│   ├── settings.py         # Configuration and environment variables
│   ├── urls.py            # URL routing
│   └── wsgi.py            # WSGI application
├── requirements.txt        # Python dependencies
└── manage.py              # Django management commands
```

## Testing & Quality Assurance

```bash
# Comprehensive test suite
python manage.py test

# Coverage reporting
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

**Test Coverage**: Comprehensive unit tests covering emission calculations, API endpoints, and data validation

## Documentation & Standards Compliance

- **Interactive API Documentation**: OpenAPI 3.0 specification with Swagger UI
- **Standards Compliance**: 
  - **ISO 14067**: Carbon footprint of products
  - **ISO 14040/14044**: Life Cycle Assessment principles and framework
  - **EN 15804**: Environmental Product Declarations for construction products
  - **EN 15978**: Assessment of environmental performance of buildings
  - **Asset Administration Shell (AAS)**: Digital representation standards
- **LCA Lifecycle Stages**: Following EN 15804/15978 framework:
  - **A1-A3** (Product): Raw materials, transport to factory, manufacturing ("cradle-to-gate")
  - **A4-A5** (Construction): Transport to site, installation
  - **B1-B7** (Use): Operation, maintenance, repair, replacement, energy/water use
  - **C1-C4** (End-of-life): Demolition, transport, waste processing, disposal
  - **D** (Beyond boundary): Reuse, recycling, recovery benefits
- **Code Documentation**: Comprehensive docstrings and type hints throughout codebase
- **Architecture Documentation**: PlantUML class diagrams and relationship mapping

## Configuration

### Environment Variables
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

## Production Deployment

For production deployment:

1. **Update database settings** in `settings.py`
2. **Set `DEBUG=False`** and configure `ALLOWED_HOSTS`
3. **Configure static files** serving
4. **Set up SSL/HTTPS** for secure communication
5. **Configure environment variables** for secrets

## Core Features

### **Product Carbon Footprint Calculation**
- Calculate PCF using IDTA-supported methodologies (ISO 14040/14044, ISO 14067, etc.)
- Support for all lifecycle stages (A1-A5, B1-B7, C1-C4, D)
- Real-time aggregation across complex supply chains

### **Digital Product Passport Generation**
- Generate standards-compliant DPPs in AASX, XML, and JSON formats
- Asset Administration Shell (AAS) compliance
- SCSN-compatible payload generation

### **Supply Chain Data Management**
- Multi-company architecture with secure data sharing
- Product sharing request workflows with approval mechanisms
- Role-based access control and audit logging

### **Advanced Analytics**
- AI-powered sustainability recommendations using OpenAI GPT-4
- Comprehensive emission tracing with data lineage
- Multi-format data export for external analytics tools

### **Standards Integration**
- **ISO 14067** (Carbon footprint of products)
- **ISO 14040/14044** (Life Cycle Assessment principles and framework)
- **EN 15804** (Environmental Product Declarations for construction products)
- **EN 15978** (Assessment of environmental performance of buildings)
- **Asset Administration Shell (AAS)** specifications
- **SCSN (Smart Connected Supplier Network)** compatibility
- **ECLASS 15** classification system with IRDI codes

## Project Context

**Developed for**: Brainport Industries (Bachelor's End Project)  
**Client**: Sara Manders, EU Project Manager  
**Supervisor**: Felipe de Azeredo Coutinho Xavier  
**Institution**: Eindhoven University of Technology (TU/e)  
**Period**: April-June 2025  

**Industry Impact**: Supports EU regulatory compliance for carbon footprint reporting and digital product passports in manufacturing supply chains.

## Key Achievements & Learning Outcomes

### **Technical Accomplishments**
- Built production-ready Django REST API backend with 80%+ test coverage
- Implemented complex polymorphic data models for multi-type emission calculations
- Created standards-compliant export pipeline for Asset Administration Shell (AAS) format
- Designed multi-tenant architecture supporting secure cross-company data sharing

### **Sustainability & Analytics Experience**
- Deep understanding of carbon footprint calculation methodologies (ISO standards)
- Experience with environmental data modeling and lifecycle assessment
- Real-world application of sustainability metrics in industrial context
- Integration of AI/ML for environmental optimization recommendations

### **Relevant to Cloud Infrastructure Role**
- **Cost Modeling Experience**: Built resource consumption tracking systems
- **Multi-tenant Architecture**: Designed secure data segregation for enterprise use
- **Analytics Pipeline Development**: Created APIs optimized for dashboard consumption
- **Compliance & Audit Systems**: Implemented comprehensive logging for regulatory requirements

## Contributing

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

## License

This project is part of an academic assignment at TU/e. Please refer to the project guidelines for usage and distribution terms.

---

This project demonstrates practical experience in environmental metrics calculation, multi-tenant data architecture, and analytics pipeline development - all directly applicable to cloud cost and environmental footprint analysis roles in enterprise environments.