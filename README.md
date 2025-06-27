# Pokémon Go Max Mechanics

![Python Version](https://img.shields.io/badge/python-3.13-blue.svg)
![Poetry](https://img.shields.io/badge/poetry-dependency%20management-blue.svg)
![Tkinter](https://img.shields.io/badge/tkinter-GUI-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Code Quality](https://img.shields.io/badge/code%20quality-mypy%20%7C%20ruff%20%7C%20isort-brightgreen.svg)

A Python GUI application built with tkinter for exploring and analyzing Pokémon Go Max mechanics. This project provides an intuitive interface for understanding the complex mechanics behind Max moves, Dynamax/Gigantamax transformations, and related battle mechanics.

## 🚀 Features

- **Clean GUI Interface**: Built with tkinter for cross-platform compatibility
- **Extensible Architecture**: Modular design ready for additional features
- **Type Safety**: Full type hints with mypy compliance
- **Code Quality**: Enforced with ruff, isort, and comprehensive linting

## 📋 Requirements

- Python 3.13+
- Poetry (for dependency management)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd pokemon-go-max-mechanics
   ```

2. **Install dependencies using Poetry**:
   ```bash
   poetry install
   ```

3. **Install development dependencies** (optional, for contributing):
   ```bash
   poetry install --with code-quality,test
   ```

## 🎮 Usage

Run the application with:

```bash
# Using Poetry
poetry run python main.py

# Or activate the virtual environment first
poetry shell
python main.py
```

The application will open a GUI window with the main interface for exploring Max mechanics.

## 🏗️ Project Structure

```
pokemon-go-max-mechanics/
├── main.py                           # Application entry point
├── src/
│   └── application/
│       ├── app.py                   # Main application class
│       └── gui/
│           └── widgets/             # Custom GUI widgets
├── pyproject.toml                   # Poetry configuration and tool settings
└── README.md                       # Project documentation
```

## 🧪 Development

### Code Quality Checks

Run all code quality checks in a single command:

```bash
# Full code quality check suite
poetry run mypy src/ && poetry run isort --check-only . && poetry run ruff check .
```

### Individual Tools

```bash
# Type checking with mypy
poetry run mypy src/

# Import sorting with isort
poetry run isort .
poetry run isort --check-only .  # Check without modifying

# Linting and formatting with ruff
poetry run ruff check .           # Check for issues
poetry run ruff format .          # Format code
poetry run ruff check --fix .     # Auto-fix issues
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=src
```

### Development Workflow

1. **Make your changes**
2. **Run code quality checks**:
   ```bash
   poetry run mypy src/ && poetry run isort --check-only . && poetry run ruff check .
   ```
3. **Fix any issues** reported by the tools
4. **Run tests** to ensure functionality
5. **Commit your changes**

## 📝 Configuration

The project uses several configuration files:

- **`pyproject.toml`**: Poetry dependencies, mypy, ruff, and isort configuration
- **Tool Settings**:
  - **mypy**: Strict type checking with Python 3.13 target
  - **ruff**: Line length 119, comprehensive linting rules
  - **isort**: Black-compatible profile for import sorting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run the code quality checks (see Development section)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## 🎯 Roadmap

- [ ] Max move damage calculator
- [ ] Dynamax/Gigantamax form analyzer
- [ ] Battle mechanic simulations
- [ ] Data visualization for Max mechanics
- [ ] Import/export functionality for battle data

---

**Built with ❤️ for the Pokémon Go community**
