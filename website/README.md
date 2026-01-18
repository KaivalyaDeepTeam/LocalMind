# LocalMind Website

Official website for **LocalMind** - AI transcription that's free, private, and runs entirely on your device.

🌐 **Live Site:** [https://svetozar-technologies.github.io/localmind.github.io/](https://svetozar-technologies.github.io/localmind.github.io/)

## Features

✅ **Multi-Language Support** - 8 languages with 100% translation coverage:
- 🇬🇧 English
- 🇪🇸 Spanish (Español)
- 🇯🇵 Japanese (日本語)
- 🇦🇪 Arabic (العربية) with RTL support
- 🇮🇳 Hindi (हिन्दी)
- 🇷🇺 Russian (Русский)
- 🇫🇷 French (Français)
- 🇨🇳 Chinese Simplified (中文)

✅ **Email Capture Modal** - Pre-download email collection for product updates

✅ **Privacy-Focused Analytics** - Plausible Analytics (GDPR compliant, no cookies)

✅ **Responsive Design** - Mobile-first, works on all devices

✅ **Static Site** - Fast, secure, hosted on GitHub Pages

## Project Structure

```
website/
├── index.html              # Main landing page
├── privacy.html            # Privacy policy page
├── css/
│   └── style.css          # All styles
├── js/
│   ├── i18n.js            # Internationalization system
│   └── main.js            # Main JavaScript logic
├── translations/          # Language files
│   ├── en.json           # English
│   ├── es.json           # Spanish
│   ├── ja.json           # Japanese
│   ├── ar.json           # Arabic
│   ├── hi.json           # Hindi
│   ├── ru.json           # Russian
│   ├── fr.json           # French
│   └── zh.json           # Chinese
└── assets/               # Images, logos, etc.
```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Svetozar-Technologies/localmind.github.io.git
cd localmind.github.io
```

### 2. Configure Email Capture (Optional)

The email capture modal uses [Formspree](https://formspree.io) for form handling.

**To enable it:**

1. Create a free Formspree account at https://formspree.io
2. Create a new form and get your form endpoint
3. Replace `YOUR_FORM_ID` in `index.html` line 786:

```html
<!-- Before -->
<form id="emailCaptureForm" action="https://formspree.io/f/YOUR_FORM_ID" method="POST">

<!-- After -->
<form id="emailCaptureForm" action="https://formspree.io/f/YOUR_ACTUAL_FORM_ID" method="POST">
```

**If you don't want email capture:**
- You can skip this step - the modal will still appear but submissions won't work
- Or remove the entire modal section from the HTML

### 3. Configure Analytics (Optional)

The site uses Plausible Analytics for privacy-friendly tracking.

**To configure:**

1. Sign up at https://plausible.io
2. Add your domain
3. Update line 33 in `index.html`:

```html
<!-- Before -->
<script defer data-domain="svetozar-technologies.github.io" src="https://plausible.io/js/script.js"></script>

<!-- After -->
<script defer data-domain="your-actual-domain.com" src="https://plausible.io/js/script.js"></script>
```

**If you don't want analytics:**
- Remove line 33 from `index.html`

### 4. Deploy to GitHub Pages

1. Push to your GitHub repository
2. Go to repository **Settings** → **Pages**
3. Select **Source:** Deploy from a branch
4. Select **Branch:** `main` / `(root)`
5. Click **Save**

Your site will be live at: `https://[username].github.io/[repository-name]/`

## Adding Translations

All translations are in the `translations/` folder as JSON files.

**To add a new language:**

1. Copy `translations/en.json` to `translations/[language-code].json`
2. Translate all values (keep the keys unchanged)
3. Add the language to `js/i18n.js` line 10-18:

```javascript
this.supportedLanguages = [
    // ... existing languages
    { code: 'de', name: 'Deutsch', flag: '🇩🇪' }  // Example: German
];
```

4. Test by selecting the language from the dropdown

**Translation Coverage:** All 8 languages currently have **100% coverage** (163/163 keys)

## Local Development

Simply open `index.html` in a browser. No build process required.

For live reloading during development, you can use:

```bash
# Using Python
python3 -m http.server 8000

# Using Node.js
npx serve
```

Then open http://localhost:8000

## Technology Stack

- **HTML5** - Semantic markup
- **CSS3** - Custom styles, no frameworks
- **Vanilla JavaScript** - No jQuery or heavy dependencies
- **Plausible Analytics** - Privacy-friendly analytics
- **Formspree** - Form backend (free tier)
- **GitHub Pages** - Static site hosting

## Privacy & Security

✅ **No tracking cookies** - Uses privacy-friendly Plausible Analytics

✅ **No personal data stored** - Email addresses only collected with explicit opt-in

✅ **GDPR compliant** - Privacy policy included

✅ **No third-party scripts** - Except Plausible and Google Fonts (optional)

✅ **Open source** - Audit the code yourself

## License

This website is part of the LocalMind project.

Website code: MIT License
Content: © 2025 Svetozar Technologies

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-translation`)
3. Commit your changes (`git commit -m 'Add German translation'`)
4. Push to the branch (`git push origin feature/new-translation`)
5. Open a Pull Request

## Support

- **Bug reports:** [GitHub Issues](https://github.com/Svetozar-Technologies/localmind.github.io/issues)
- **Feature requests:** [GitHub Discussions](https://github.com/Svetozar-Technologies/localmind.github.io/discussions)
- **Main project:** [LocalMind Repository](https://github.com/KaivalyaDeepTeam/localmind)

---

**Built with ❤️ by Svetozar Technologies**
