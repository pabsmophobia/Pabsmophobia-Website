# 👻 Pabsmophobia-Website

Official website, event hub, and evidence vault for **Pabsmophobia** — your central hub for paranormal investigation, supernatural events, and collected evidence.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Getting Started](#getting-started)
- [Site Structure](#site-structure)
- [Evidence Submission](#evidence-submission)
- [Contributing](#contributing)
- [Local Development](#local-development)
- [Deployment](#deployment)

---

## 🌐 Overview

This website serves as the official platform for Pabsmophobia, combining:

- **Event Hub** — Track and discover paranormal events in real-time
- **Evidence Vault** — A curated, organized collection of paranormal evidence and documentation
- **Community Portal** — Connect with investigators and enthusiasts
- **Investigation Log** — Historical records of investigations and findings

---

## ✨ Features

- 🔍 **Evidence Classification System** — Organized by category, location, and date
- 📍 **Interactive Event Tracking** — Real-time event updates and locations
- 📚 **Research Archive** — Comprehensive documentation and case studies
- 🎯 **Submission Portal** — Submit evidence for review and publication
- 📱 **Responsive Design** — Works seamlessly on desktop, tablet, and mobile

---

## 🚀 Getting Started

### Prerequisites

- Node.js v24 or higher
- npm or yarn package manager
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/pabsmophobia/Pabsmophobia-Website.git
   cd Pabsmophobia-Website
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Run the development server**
   ```bash
   npm start
   ```

4. **Build for production**
   ```bash
   npm run build
   ```

---

## 📁 Site Structure

```
Pabsmophobia-Website/
├── index.html                 # Homepage
├── events/                    # Event hub pages
├── evidence/                  # Evidence vault
│   ├── apparitions/
│   ├── poltergeists/
│   ├── hauntings/
│   └── unexplained/
├── research/                  # Research and documentation
├── submit/                    # Evidence submission portal
├── assets/                    # Images, styles, scripts
│   ├── css/
│   ├── js/
│   └── images/
├── .github/
│   └── workflows/             # GitHub Actions automation
│       └── uniform-format.yml # HTML/CSS formatting
└── README.md                  # This file
```

---

## 🕵️ Evidence Submission

### How to Submit Evidence

1. Navigate to the **[Submit Evidence](./submit/)** section
2. Fill out the submission form with:
   - **Type** — Apparition, Poltergeist, Haunting, or Other
   - **Location** — Where the incident occurred
   - **Date** — When it was reported/discovered
   - **Description** — Detailed account of the experience
   - **Attachments** — Photos, videos, or documentation (optional)
   - **Contact Info** — For follow-up investigations

3. Submit for review
4. Our team will verify and classify the evidence
5. Approved submissions appear in the Evidence Vault

### Evidence Guidelines

- Be as detailed and accurate as possible
- Include corroborating evidence when available
- Respect privacy — redact names if necessary
- No hoaxes or fabricated claims
- Evidence must be submitted in good faith

---

## 🤝 Contributing

We welcome contributions from paranormal researchers, enthusiasts, and developers!

### Types of Contributions

- 📝 **Evidence & Reports** — Submit findings and investigations
- 🐛 **Bug Reports** — Found an issue? Let us know
- 💡 **Feature Requests** — Suggest improvements
- 💻 **Code Contributions** — Help improve the website

### Development Contribution Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Commit with clear messages (`git commit -m "feat: your feature"`)
5. Push to your fork and submit a Pull Request

---

## 💻 Local Development

### Build Process

The site uses automated HTML/CSS formatting via GitHub Actions:

```bash
# Manual formatting (runs on every push to main)
node .github/scripts/format-html.js
```

### Watch Mode

Monitor your files during development:

```bash
npm run watch
```

### Testing

```bash
npm run test
```

---

## 🌍 Deployment

This site is deployed via **GitHub Pages** and automatically updates when changes are pushed to the `main` branch.

### Deployment Status

- **Hosting** — GitHub Pages
- **Branch** — `main`
- **URL** — `https://pabsmophobia.github.io/Pabsmophobia-Website/`

### Automated Workflows

1. **Normalize HTML Formatting** — Auto-formats HTML/CSS on every push
2. **Pages Build & Deployment** — Automatically builds and deploys the site

Check the [Actions tab](https://github.com/pabsmophobia/Pabsmophobia-Website/actions) for deployment status.

---

## 📞 Contact & Support

- **Issues** — Report bugs via [GitHub Issues](https://github.com/pabsmophobia/Pabsmophobia-Website/issues)
- **Discussions** — Join the community at [GitHub Discussions](https://github.com/pabsmophobia/Pabsmophobia-Website/discussions)
- **Email** — [Contact us directly]

---

## 📄 License

This project is licensed under the MIT License — see LICENSE.md for details.

---

## 🙏 Acknowledgments

Thank you to all contributors, researchers, and the paranormal investigation community for their dedication to uncovering the unknown.

**Last Updated:** August 9, 2026
