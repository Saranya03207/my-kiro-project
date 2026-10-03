# Steering Documents - Smart Canteen Manager

This directory contains comprehensive guidelines for implementing the Smart Canteen Manager application. These documents establish standards, conventions, and best practices for consistent, high-quality development.

## 📚 Available Documents

### 1. [Architecture and Technology Standards](architecture-standards.md)
**When to use**: Beginning of project setup, architectural decisions

**Key topics**:
- Technology stack (FastAPI, SQLite, Vanilla JavaScript)
- Project structure and file organization
- Architectural principles and patterns
- API design standards
- Dependencies and development workflow

### 2. [Coding Conventions](coding-conventions.md)
**When to use**: Writing any code (Python, JavaScript, HTML, CSS)

**Key topics**:
- Python/FastAPI style guide (PEP 8, type hints, async/await)
- JavaScript/ES6+ conventions (modules, classes, async/await)
- HTML semantic markup and accessibility
- CSS organization (BEM-inspired, responsive design)
- Naming conventions across all languages
- Error handling patterns
- Git commit message format

### 3. [UI/UX Guidelines](ui-ux-guidelines.md)
**When to use**: Designing or implementing any UI component

**Key topics**:
- Design principles (simplicity, accessibility, responsiveness)
- Color palette and typography
- Component patterns (buttons, cards, forms, alerts)
- Page layouts (student and admin interfaces)
- Responsive breakpoints and mobile-first approach
- Accessibility checklist (WCAG 2.1 Level AA)
- Loading states and empty states

### 4. [Security and Data Handling Guidelines](security-guidelines.md)
**When to use**: Any time handling user input, authentication, or sensitive data

**Key topics**:
- Input validation (Pydantic schemas)
- SQL injection prevention (ORM usage)
- Authentication and session management
- Authorization middleware patterns
- Secure configuration (environment variables)
- Never expose secrets
- Rate limiting
- Security checklist

### 5. [Testing Guidelines](testing-guidelines.md)
**When to use**: Writing tests for any new functionality

**Key topics**:
- Property-based testing (Hypothesis, fast-check)
- Unit testing patterns (pytest, Jest)
- Integration testing (API endpoints, database)
- Test organization and naming conventions
- Coverage goals (80% backend, 75% frontend)
- Mocking and fixtures
- Test tag format for property tests

### 6. [AI Assistant Guidelines](ai-assistant-guidelines.md)
**When to use**: Implementing or working with the AI assistant feature

**Key topics**:
- Data-driven responses (NEVER invent data)
- Context building from current database state
- Graceful degradation when service unavailable
- Input sanitization (prevent injection attacks)
- Response guidelines and examples
- Testing AI responses
- Security considerations

## 🚀 Quick Start

### For New Developers

1. **Start here**: Read [Architecture Standards](architecture-standards.md) to understand the overall system
2. **Before coding**: Review [Coding Conventions](coding-conventions.md) for your language
3. **When building UI**: Reference [UI/UX Guidelines](ui-ux-guidelines.md) for design patterns
4. **Handling data**: Follow [Security Guidelines](security-guidelines.md) for safe practices
5. **Writing tests**: Use [Testing Guidelines](testing-guidelines.md) for comprehensive testing

### For Specific Tasks

| Task | Documents to Review |
|------|-------------------|
| Setting up project | Architecture Standards |
| Creating API endpoint | Architecture Standards, Coding Conventions, Security Guidelines |
| Building frontend component | Coding Conventions, UI/UX Guidelines |
| Implementing authentication | Security Guidelines, Coding Conventions |
| Writing property tests | Testing Guidelines |
| Adding AI features | AI Assistant Guidelines, Security Guidelines |
| Responsive design | UI/UX Guidelines, Coding Conventions (CSS) |

## 🎯 Key Principles

### Always Follow

1. **Security First**: Validate all input, never expose secrets, always use ORM
2. **Accessibility**: WCAG 2.1 Level AA compliance, keyboard navigation, screen reader support
3. **Testing**: Property tests for business logic, unit tests for specific cases, integration tests for APIs
4. **Documentation**: Type hints, docstrings, clear comments explaining WHY not WHAT
5. **Consistency**: Follow established patterns and conventions throughout the codebase

### Never Do

1. ❌ Write raw SQL queries (use ORM)
2. ❌ Hardcode secrets or configuration values
3. ❌ Skip input validation
4. ❌ Invent data in AI responses
5. ❌ Ignore accessibility requirements
6. ❌ Ship code without tests
7. ❌ Use console.log or print statements (use logging)

## 📋 Checklists

### Before Committing Code

- [ ] Code follows naming conventions
- [ ] All inputs are validated
- [ ] No hardcoded values (use config)
- [ ] Tests written and passing
- [ ] Documentation updated (if needed)
- [ ] No console.log or print statements
- [ ] Accessibility considered (for UI)
- [ ] Security reviewed (for data handling)

### Before Deployment

- [ ] All tests passing
- [ ] Security checklist completed
- [ ] Environment variables configured
- [ ] README documentation updated
- [ ] No secrets in code or git history
- [ ] CORS configured correctly
- [ ] Rate limiting enabled
- [ ] Error handling comprehensive

## 🔄 Workflow Integration

These steering documents are automatically loaded by Kiro when you work in this workspace. They provide context-aware guidance during development. You can:

- **Reference explicitly**: "Follow the security guidelines for input validation"
- **Trust automatic loading**: Kiro loads relevant documents based on what you're working on
- **Update as needed**: These are living documents - improve them as the project evolves

## 📝 Document Maintenance

### When to Update

- New patterns emerge that should be standardized
- Security vulnerabilities discovered that need guidelines
- UI/UX patterns refined based on user feedback
- Testing approaches improved
- Technology stack changes

### How to Update

1. Edit the relevant markdown file
2. Ensure examples are clear and practical
3. Update cross-references if needed
4. Commit with descriptive message: `docs: Update security guidelines for session management`

## 💡 Tips for Success

1. **Read before you code**: 5 minutes reviewing guidelines saves hours of refactoring
2. **Refer during code review**: Use these as objective standards for feedback
3. **Share with team**: Ensure everyone follows the same conventions
4. **Keep practical**: Guidelines should help, not hinder - update if something doesn't work
5. **Lead by example**: Follow these guidelines in all code contributions

## 🆘 Getting Help

- **Unclear guideline?** Ask for clarification and suggest improvements
- **Missing pattern?** Propose additions to relevant documents
- **Conflicts?** Security and architecture guidelines take precedence
- **Exceptions?** Document why deviation is necessary

## 📊 Document Status

| Document | Version | Last Updated | Status |
|----------|---------|--------------|--------|
| Architecture Standards | 1.0 | 2026-10-02 | ✅ Complete |
| Coding Conventions | 1.0 | 2026-10-02 | ✅ Complete |
| UI/UX Guidelines | 1.0 | 2026-10-02 | ✅ Complete |
| Security Guidelines | 1.0 | 2026-10-02 | ✅ Complete |
| Testing Guidelines | 1.0 | 2026-10-02 | ✅ Complete |
| AI Assistant Guidelines | 1.0 | 2026-10-02 | ✅ Complete |

---

**Remember**: These guidelines exist to ensure consistency, quality, and maintainability. They represent collective wisdom and best practices for this project. Follow them, improve them, and use them to build great software! 🚀
