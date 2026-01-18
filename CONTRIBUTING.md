# Contributing to LocalMind

Thank you for your interest in contributing to LocalMind! We welcome contributions from everyone.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue on GitHub with:
- A clear description of the problem
- Steps to reproduce the issue
- Expected vs actual behavior
- Your system information (OS, Python version, hardware)
- Relevant logs or error messages

### Suggesting Features

We welcome feature suggestions! Please open an issue with:
- A clear description of the feature
- Why this feature would be useful
- Examples of how it would work
- Any relevant mockups or diagrams

### Code Contributions

1. **Fork the repository**
   ```bash
   git clone https://github.com/KaivalyaDeepTeam/localmind.git
   cd localmind
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set up development environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Make your changes**
   - Write clean, readable code
   - Follow existing code style
   - Add comments where necessary
   - Update documentation if needed

5. **Test your changes**
   ```bash
   # Run tests
   pytest tests/

   # Test the application
   python -m localmind
   ```

6. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

   Use conventional commit messages:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `style:` - Code style changes (formatting, etc.)
   - `refactor:` - Code refactoring
   - `test:` - Adding or updating tests
   - `chore:` - Maintenance tasks

7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Open a Pull Request**
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your fork and branch
   - Provide a clear description of your changes
   - Link any related issues

## Code Guidelines

### Python Style
- Follow PEP 8 style guide
- Use type hints where appropriate
- Keep functions focused and small
- Write docstrings for public functions

### Testing
- Add tests for new features
- Ensure all tests pass before submitting PR
- Test on your target platform (macOS, Windows, or Linux)

### Documentation
- Update README.md if you add user-facing features
- Update docstrings for code changes
- Add comments for complex logic

## Translation Contributions

We welcome translations for the UI! To add a new language:

1. Check if your language is supported by creating an issue
2. Add translations to the appropriate locale files
3. Test the UI in your language
4. Submit a PR with screenshots

## Project Structure

```
localmind/
├── localmind/           # Main application code
│   ├── ui/             # UI components
│   ├── core/           # Core functionality
│   └── utils/          # Utility functions
├── tests/              # Test suite
├── docs/               # Documentation
├── packaging/          # Build scripts
└── website/            # Website (separate repo)
```

## Development Tips

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_export.py

# Run with coverage
pytest --cov=localmind tests/
```

### Building Locally
```bash
# Build application
pyinstaller LocalMind.spec

# Build DMG (macOS)
./build_dmg_local.sh
```

### Debugging
- Use Python debugger: `import pdb; pdb.set_trace()`
- Check logs in the application directory
- Test with different audio files and formats

## Getting Help

- **Questions**: Open a [Discussion](https://github.com/KaivalyaDeepTeam/localmind/discussions)
- **Bugs**: Open an [Issue](https://github.com/KaivalyaDeepTeam/localmind/issues)
- **Security**: Email kaivalyaanandpandey666@gmail.com

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discriminatory language
- Trolling or insulting comments
- Personal or political attacks
- Publishing others' private information
- Other unprofessional conduct

## License

By contributing to LocalMind, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be acknowledged in:
- The project README
- Release notes for significant contributions
- GitHub's contributor graph

Thank you for helping make LocalMind better! 🎉
