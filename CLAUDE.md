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

### Frontend Development
```bash
# Install dependencies
pnpm install

# Development server (runs on port 3100)
pnpm dev

# Build for production
pnpm build

# Preview production build
pnpm preview
```

### Backend Development
```bash
# Maven build
mvn clean install

# Run main application (port 8080)
mvn spring-boot:run -pl jeecg-module-system/jeecg-system-start

# API documentation available at: http://localhost:8080/doc.html
```

### Docker Deployment
```bash
# Full stack deployment
docker-compose up -d

# Microservices deployment
docker-compose -f docker-compose-cloud.yml up -d
```

## Architecture Overview

### Key Entry Points
- **Backend Main**: `/jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/java/org/jeecg/JeecgSystemApplication.java`
- **Frontend Main**: `/jeecgboot-vue3/src/main.ts`

### Module Structure
- **jeecg-boot-base-core**: Core framework and utilities
- **jeecg-module-system**: System management (users, roles, menus)
- **jeecg-boot-module**: Business modules including AI features
- **jeecg-server-cloud**: Microservices modules

### Core Features
1. **Low-Code Platform**: Online form builder, code generator, report designer
2. **AI Integration**: Support for ChatGPT, DeepSeek, Ollama with visual workflow designer
3. **Enterprise Features**: Multi-tenancy, workflow (Flowable), reporting (JimuReport)

### Database Support
Supports MySQL, PostgreSQL, Oracle, SQL Server, and Chinese databases (DM, KingBase, TiDB).

## Development Patterns

1. **Component-First**: Use existing JEECG components before creating new ones
2. **Low-Code First**: Build simple features with online tools, then enhance with code
3. **Modular Design**: Keep clear separation between core, system, and business modules
4. **AI Integration**: Leverage built-in AI capabilities for enhanced functionality

## Important Notes

- Frontend uses Ant Design Vue 4 as primary UI framework
- Backend follows Spring Boot best practices with MyBatis-Plus for ORM
- AI features are deeply integrated throughout the platform via `@jeecg/aiflow`
- The project implements intelligent upstream sync strategies to avoid conflicts