# Municipal Permit Tracking System

[![License: ISC](https://img.shields.io/badge/License-ISC-blue.svg)](https://opensource.org/licenses/ISC)
[![Next.js](https://img.shields.io/badge/Next.js-15.4.6-black)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9.2-blue)](https://www.typescriptlang.org/)
[![Supabase](https://img.shields.io/badge/Supabase-Latest-green)](https://supabase.com/)

A comprehensive permit scraping and mapping solution for construction industry professionals. Track permits across 35-40 Southern California municipalities with real-time updates, route optimization, and professional quote generation.

## ✨ Features

- 🗺️ **Interactive Mapping** - Visualize permits on Leaflet maps with clustering
- 🔍 **Multi-Municipal Scraping** - Automated data collection from 35+ portals
- 📊 **Real-time Dashboard** - Live permit status tracking and analytics
- 🚛 **Route Optimization** - Calculate optimal trucking routes and pricing
- 💰 **Quote Generation** - Professional LDP quote sheets with distance calculations
- 🔐 **Secure Architecture** - Supabase backend with Row Level Security

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+ (for scraping scripts)
- Supabase account

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ramos333oz/Municipal-Permit-Scraper.git
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

5. **Open your browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 15 (App Router)
- **Styling**: Tailwind CSS v4 + Emotion
- **Language**: TypeScript
- **Maps**: Leaflet + React Leaflet
- **Icons**: Lucide React
- **State Management**: React Server Components

### Backend
- **Database**: Supabase (PostgreSQL + PostGIS)
- **Authentication**: Supabase Auth
- **API**: Next.js API Routes
- **Geocoding**: Multi-tier (Geocodio, Google, OpenCage)

### Scraping & Automation
- **Language**: Python 3.8+
- **Browser Automation**: Selenium WebDriver
- **Data Processing**: Pandas, NumPy
- **Scheduling**: GitHub Actions

## 📁 Project Structure

```
├── src/
│   ├── app/                    # Next.js App Router pages
│   ├── components/            # Reusable React components
│   ├── lib/                   # Utility functions & configurations
│   └── types/                 # TypeScript type definitions
├── scripts/                   # Python scraping scripts
│   ├── san-diego-script/      # San Diego County scraper
│   └── script-configs/        # Configuration files
├── UI-design-plans/           # Design system & documentation
├── data-example/              # Sample data files
└── Docs/                      # Project documentation
```

## 🚦 Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run type-check   # TypeScript validation
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the ISC License - see the [LICENSE](LICENSE) file for details.

## 📚 Documentation

- [Setup Guide](SETUP_GUIDE.md) - Detailed installation instructions
- [UI Design Plans](UI-design-plans/README.md) - Design system documentation
- [API Documentation](Docs/) - Backend API reference

## 🐛 Issues & Support

Found a bug or need help? Please [open an issue](https://github.com/ramos333oz/Municipal-Permit-Scraper/issues) on GitHub.
