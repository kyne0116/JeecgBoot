# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

JeecgBoot is an enterprise-level low-code platform with integrated AI capabilities (version 3.8.1). It combines traditional low-code development with modern AI application development, built on Vue 3 + Spring Boot architecture.

## Technology Stack

**Frontend (jeecgboot-vue3/)**
- Vue 3.5.13 + TypeScript + Vite 6 + Ant Design Vue 4.2.6
- Pinia for state management, VXE Table for advanced tables
- Custom JEECG components for business logic

**Backend (jeecg-boot/)**
- Spring Boot 2.7.18 + Java 17 (supports JDK 8, 17, 21)
- Spring Cloud Alibaba for microservices
- MyBatis-Plus 3.5.3.2 + Apache Shiro + JWT

## Common Development Commands

### Frontend Development (jeecgboot-vue3/)
```bash
# Install dependencies
pnpm install

# Development server (runs on port 3100 by default)
pnpm dev

# Build for production
pnpm build

# Build with bundle analyzer
pnpm build:report

# Preview production build
pnpm preview

# Clean cache and reinstall
pnpm reinstall

# Format code
pnpm batch:prettier
```

### Backend Development (jeecg-boot/)
```bash
# Maven build (all modules)
mvn clean install

# Run main application (single mode, port 8080)
mvn spring-boot:run -pl jeecg-module-system/jeecg-system-start

# Build with specific profile
mvn clean install -P dev

# Skip tests during build
mvn clean install -DskipTests

# API documentation available at: http://localhost:8080/doc.html
```

### Testing
```bash
# Frontend tests (Jest)
cd jeecgboot-vue3
npm run test

# Backend tests
cd jeecg-boot
mvn test
```

### Docker Deployment
```bash
# Full stack deployment (single mode)
docker-compose up -d

# Microservices deployment
docker-compose -f docker-compose-cloud.yml up -d

# Build and run specific service
docker-compose up jeecg-boot-system
```

## Architecture Overview

### Key Entry Points
- **Backend Main**: `/jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/java/org/jeecg/JeecgSystemApplication.java`
- **Frontend Main**: `/jeecgboot-vue3/src/main.ts`
- **Backend Config**: `/jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/application.yml`
- **Frontend Config**: `/jeecgboot-vue3/.env.development` (dev), `/jeecgboot-vue3/.env.production` (prod)

### Project Structure
```
JeecgBoot/
├── jeecg-boot/                     # Backend Spring Boot project
│   ├── jeecg-boot-base-core/       # Core framework and utilities
│   ├── jeecg-module-system/        # System management (users, roles, menus)
│   │   ├── jeecg-system-api/       # API definitions
│   │   ├── jeecg-system-biz/       # Business logic
│   │   └── jeecg-system-start/     # Startup module (main entry point)
│   ├── jeecg-boot-module/          # Business modules including AI features
│   │   └── jeecg-boot-module-airag/ # AI and RAG capabilities
│   └── jeecg-server-cloud/         # Microservices modules
│       ├── jeecg-cloud-gateway/    # API Gateway
│       ├── jeecg-cloud-nacos/      # Service discovery
│       └── jeecg-visual/           # Monitoring and management
├── jeecgboot-vue3/                 # Frontend Vue 3 project
│   ├── src/
│   │   ├── api/                    # API service layer
│   │   ├── components/             # Reusable components
│   │   ├── views/                  # Page components
│   │   ├── store/                  # Pinia state management
│   │   ├── router/                 # Vue Router configuration
│   │   └── utils/                  # Utility functions
│   ├── vite.config.ts              # Vite build configuration
│   └── package.json                # Frontend dependencies
└── docker-compose.yml              # Full stack deployment
```

### Core Features
1. **Low-Code Platform**: Online form builder, code generator, report designer
2. **AI Integration**: Support for ChatGPT, DeepSeek, Ollama with visual workflow designer (@jeecg/aiflow)
3. **Enterprise Features**: Multi-tenancy, workflow (Flowable), reporting (JimuReport)
4. **Microservices**: Spring Cloud Alibaba with Nacos, Gateway, Sentinel

### Database Support
Supports MySQL (default), PostgreSQL, Oracle, SQL Server, and Chinese databases (DM, KingBase, TiDB).

## Development Environment Setup

### Prerequisites
- **Node.js**: Version 20+ required
- **PNPM**: Version 9+ required for frontend dependency management
- **Java**: JDK 17 (supports JDK 8, 17, 21)
- **Maven**: 3.6+ for backend build
- **MySQL**: 5.7+ or compatible database

### Environment Configuration
- **Frontend proxy**: Development server proxies `/jeecgboot` to `http://localhost:8080/jeecg-boot`
- **Backend ports**: Main application runs on 8080, frontend dev server on 3100
- **Database**: Default connection expects MySQL on localhost:3306
- **Redis**: Optional but recommended for caching (localhost:6379)

### Single vs Microservices Mode
The platform supports both deployment modes:
- **Single Mode**: Use `docker-compose.yml` - all services in one container
- **Microservices Mode**: Use `docker-compose-cloud.yml` - separate services with Nacos

### Profiles and Environments
- **Maven profiles**: `dev` (default), `test`, `prod`, `SpringCloud`
- **Frontend environments**: `.env.development`, `.env.production`
- **Configuration**: Uses `@profile.name@` Maven property filtering

## Development Patterns

1. **Component-First**: Use existing JEECG components before creating new ones
2. **Low-Code First**: Build simple features with online tools, then enhance with code
3. **Modular Design**: Keep clear separation between core, system, and business modules
4. **AI Integration**: Leverage built-in AI capabilities for enhanced functionality

## Code Generation and Low-Code Features

### Online Development Tools
- **Online Forms**: Create forms without coding using the visual form designer
- **Code Generator**: Generate complete CRUD operations for entities
- **Report Designer**: Visual report and dashboard creation
- **Workflow Designer**: Visual process definition using Flowable

### AI-Powered Development
- **AI Chat Assistant**: Integrated ChatGPT/DeepSeek for development assistance
- **AI Code Generation**: Generate tables, forms, and reports using natural language
- **AI Knowledge Base**: RAG-powered documentation and Q&A system

## Important Technical Notes

- **Frontend**: Vue 3.5.13 + TypeScript + Vite 6 + Ant Design Vue 4 + Pinia
- **Backend**: Spring Boot 2.7.18 + MyBatis-Plus 3.5.3.2 + Apache Shiro + JWT
- **AI Integration**: `@jeecg/aiflow` package provides AI workflow capabilities
- **Testing**: Jest for frontend, JUnit for backend (use `mvn test` and `npm run test`)
- **Build**: Frontend uses Vite for fast development, backend uses Maven multi-module structure
- **Microservices**: Spring Cloud Alibaba with Nacos service discovery and Gateway routing
- **Security**: JWT tokens with Shiro for authentication/authorization
- **Database**: Supports multiple databases with MyBatis-Plus for cross-database compatibility