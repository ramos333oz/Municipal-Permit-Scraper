# Contributing to Municipal Permit Tracking System

Thank you for your interest in contributing to the Municipal Permit Tracking System! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+ (for scraping scripts)
- Git
- Supabase account

### Setup Development Environment

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/Municipal-Permit-Scraper.git
   cd Municipal-Permit-Scraper
   ```

2. **Install dependencies**
   ```bash
   npm install
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your actual values
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

## 📝 Development Guidelines

### Code Style
- Use TypeScript for all new code
- Follow ESLint configuration
- Use Prettier for code formatting
- Write meaningful commit messages

### Commit Message Format
```
type(scope): description

Examples:
feat(scraper): add San Diego County permit scraper
fix(ui): resolve map rendering issue
docs(readme): update installation instructions
```

### Branch Naming
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

## 🧪 Testing

Before submitting a PR:
```bash
npm run lint          # Check code style
npm run type-check     # TypeScript validation
npm run build          # Ensure build works
```

## 📋 Pull Request Process

1. Create a feature branch from `main`
2. Make your changes
3. Test thoroughly
4. Update documentation if needed
5. Submit a pull request with clear description

## 🐛 Reporting Issues

When reporting issues, please include:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Node version, etc.)

## 📚 Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [Project Architecture](./UI-design-plans/README.md)

## 📞 Questions?

Feel free to open an issue for questions or reach out to the maintainers.
