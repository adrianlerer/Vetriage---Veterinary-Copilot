# Contributing to VetrIAge

Thank you for your interest in contributing to VetrIAge! 🐾

## 📋 Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## 🚀 Getting Started

1. **Fork** the repository
2. **Clone** your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Vetriage---Veterinary-Copilot.git
   cd Vetriage---Veterinary-Copilot
   ```

3. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Set up development environment**:
   ```bash
   cd rag_api
   pip install -r requirements.txt
   cp .env.example .env
   # Add your API keys to .env
   ```

## 💻 Development Guidelines

### Commit Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation only
- `test:` Test additions/changes
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `chore:` Build process or auxiliary tool changes

Example:
```bash
git commit -m "feat(rag): add caching layer for embeddings"
git commit -m "fix(api): resolve port conflict detection"
git commit -m "docs: update installation guide"
```

### Code Style

- **Python**: Follow PEP 8
- **Line length**: 100 characters max
- **Formatting**: Use `black` for formatting
- **Type hints**: Use type annotations where possible

```bash
# Format code
black rag_api/
```

### Testing

All code changes must include tests:

```bash
# Run tests
cd rag_api
python test_rag_system.py

# Or with pytest
pytest test_rag_system.py -v
```

### Port Configuration

**⚡ CRITICAL**: Never hardcode ports!

```python
# ✅ CORRECT
port = int(os.getenv("PORT", "8000"))

# ❌ WRONG
port = 8000  # Never do this!
```

See [docs/FLEXIBLE_PORT_STANDARD.md](docs/FLEXIBLE_PORT_STANDARD.md) for details.

## 📝 Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new features
3. **Run test suite** and ensure all tests pass
4. **Update README.md** with relevant changes
5. **Create Pull Request** with clear description

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] All tests pass
- [ ] New tests added (if applicable)

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No hardcoded ports
```

## 🐛 Bug Reports

Use GitHub Issues with:
- Clear title
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Python version, OS, etc.)

## 💡 Feature Requests

Open a GitHub Discussion with:
- Use case description
- Proposed solution
- Potential alternatives

## 📚 Documentation

- Keep README.md up to date
- Add docstrings to functions
- Update API documentation
- Include examples for new features

## ✅ Review Process

- All PRs require review before merge
- Address reviewer feedback
- Maintain clean commit history
- Squash commits if requested

## 🙏 Thank You!

Your contributions make VetrIAge better for veterinarians worldwide! 🐾
