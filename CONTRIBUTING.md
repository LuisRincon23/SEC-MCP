# Contributing to Financial MCPs

We love your input! We want to make contributing to Financial MCPs as easy and transparent as possible.

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

## Pull Requests

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code follows the existing style.
6. Issue that pull request!

## Any contributions you make will be under the MIT Software License

When you submit code changes, your submissions are understood to be under the same [MIT License](LICENSE) that covers the project.

## Report bugs using GitHub's [issues](https://github.com/yourusername/financial-mcps/issues)

We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/yourusername/financial-mcps/issues/new).

## Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## Code Style

* 4 spaces for indentation rather than tabs
* 80 character line length (flexible for readability)
* Follow PEP 8 for Python code
* Use descriptive variable names
* Add comments for complex logic
* Write docstrings for all functions and classes

## Testing

* Write tests for new functionality
* Run the test suite before submitting PR:
  ```bash
  python test_phd_features.py
  ./test_single_mcp.sh MCP_NAME
  ```

## Adding a New MCP

If you want to add a new MCP:

1. Create a new directory under `FinancialMCPs/`
2. Follow the existing MCP structure:
   ```
   YOUR_MCP_NAME/
   ├── src/
   │   └── main.py
   ├── pyproject.toml
   ├── start-mcp.sh
   └── README.md
   ```
3. Inherit from shared modules where appropriate
4. Add comprehensive documentation
5. Include example usage

## License

By contributing, you agree that your contributions will be licensed under its MIT License.