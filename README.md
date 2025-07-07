# Pokémon Go Max Mechanics (MCP? soon)

![Python Version](https://img.shields.io/badge/python-3.13-blue.svg)
![uv](https://img.shields.io/badge/uv-dependency%20management-blue.svg)
![Tkinter](https://img.shields.io/badge/tkinter-GUI-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Code Quality](https://img.shields.io/badge/code%20quality-mypy%20%7C%20ruff%20%7C%20isort-brightgreen.svg)

A Python GUI application for Pokémon Go Max mechanics that calculates optimal attackers and tanks, with additional informational views. This project is designed to eventually become an MCP (Model Context Protocol) server, providing tools and context for AI agents to answer Max mechanics queries.

This is a passion project that combines Pokémon Go strategy optimization with tinkering around MCP server development - exploring how to make complex game mechanics accessible to AI assistants.

## 📋 Requirements

- Python 3.13+
- uv (for dependency management)

## 🛠️ Installation

1. **Install uv** (if not already installed).

2. **Clone the repository**:
   ```bash
   git clone https://github.com/ddelcastillo/pokemon-go-max-mechanics-mcp.git
   cd pokemon-go-max-mechanics-mcp
   ```

3. **Install dependencies**:
   ```bash
   # Install project dependencies
   uv sync
   
   # Install development dependencies
   uv sync --group code-quality --group test
   ```

## 🎮 Usage

Run the application with:

```bash
# Run the GUI application
uv run python main.py
```

The application will open a GUI window with the main interface for exploring Max mechanics and calculating optimal strategies.

## 🏗️ Project Structure

This project employs **hexagonal architecture** with clear separation of concerns:

```
pokemon-go-max-mechanics-mcp/
├── main.py                           # Application entry point
├── src/
│   ├── application/                  # Application layer (use cases, services)
│   ├── domain/                       # Domain layer (entities, ports)
│   │   └── ports/                    # Abstract ports (inbound/outbound)
│   └── infrastructure/               # Infrastructure layer (adapters, DI)
│       ├── adapters/                 # Concrete adapters (inbound/outbound)
│       └── dependency_injection/     # DI modules and setup
├── tests/                            # Test mirror structure
└── pyproject.toml                    # uv configuration and tool settings
```

The architecture follows ports & adapters pattern with dependency injection for clean, testable code.

## 🧪 Development

### Code Quality Checks

```bash
# Full code quality check suite
uv run ruff check . && uv run isort --check-only . && uv run mypy src/

# Auto-fix formatting
uv run ruff format . && uv run isort .
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and run quality checks
4. Commit using conventional commits with emojis (`git commit -m "✨ feat: add amazing feature"`)
5. Reference the GitHub issue you're solving (e.g., "Closes #123")
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## 🎯 Roadmap

- [ ] **General Pokémon domain mapping** - Core entities and value objects
- [ ] **Max-related domain mapping** - CPM calculations, HP mechanics, known bosses
- [ ] **First max services** - Damage calculations for tanks & defenders
- [ ] **Composed services** - Querying optimal tanks & defenders
- [ ] **Database normalization** - Persist analysis views in relational database
- [ ] **MCP support** - Adapt services for Model Context Protocol
- [ ] **MCP documentation** - Server setup and optimization guides
- [ ] **Max Simulator** - Battle simulation with initial known strategies

Made by Maskarayde for Team Virrey.