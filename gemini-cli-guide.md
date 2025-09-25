# Gemini CLI Command Guide

## Overview
Gemini CLI is a command-line interface that allows interaction with Google's Gemini AI model. This guide helps AI agents effectively use Gemini CLI.

## Basic Usage

### Basic Commands
```bash
gemini [promptWords...]  # Launch interactive CLI
```

### Main Options

#### Model Related
- `-m, --model <string>`: Specify the model to use
- `-p, --prompt <string>`: Direct prompt input (non-interactive mode)
- `-i, --prompt-interactive <string>`: Execute prompt then switch to interactive mode

#### Execution Environment
- `-s, --sandbox`: Run in sandbox mode
- `-d, --debug`: Enable debug mode
- `-y, --yolo`: Automatically accept all actions (YOLO mode)

#### Approval Mode
- `--approval-mode <mode>`: Set approval mode
  - `default`: Default (prompt for approval)
  - `auto_edit`: Auto-approve edit tools
  - `yolo`: Auto-approve all tools

#### Files and Context
- `-a, --all-files`: Include all files in context (deprecated)
- `--include-directories <array>`: Additional directories to include in workspace

#### Extensions and Tools
- `-e, --extensions <array>`: List of extensions to use
- `-l, --list-extensions`: Show available extensions list
- `--allowed-tools <array>`: Tools that can run without confirmation
- `--allowed-mcp-server-names <array>`: Allowed MCP server names

#### Accessibility and Output
- `--screen-reader`: Enable screen reader mode
- `--session-summary <string>`: File to write session summary to

#### Others
- `-v, --version`: Show version number
- `-h, --help`: Show help

## MCP Server Management

### Commands
```bash
gemini mcp add <name> <commandOrUrl> [args...]  # Add server
gemini mcp remove <name>                        # Remove server
gemini mcp list                                 # List configured MCP servers
```

### Usage Examples
```bash
# Add MCP server
gemini mcp add my-server "npx @modelcontextprotocol/server-filesystem"

# Check MCP server list
gemini mcp list

# Remove MCP server
gemini mcp remove my-server
```

## Extension Management

### Commands
```bash
gemini extensions install [source]          # Install extension
gemini extensions uninstall <name>          # Uninstall extension
gemini extensions list                      # List installed extensions
gemini extensions update [--all] [name]     # Update extensions
gemini extensions disable [--scope] <name>  # Disable extension
gemini extensions enable [--scope] <name>   # Enable extension
gemini extensions link <path>               # Link extension from local path
gemini extensions new <path> <template>     # Create new extension
```

### Usage Examples
```bash
# Install extension
gemini extensions install https://github.com/user/extension-repo

# Update all extensions
gemini extensions update --all

# Check extension list
gemini extensions list
```

## Repository Management

### Commands
```bash
python src/cli/main.py repo create <name>              # Create a new knowledge repository
python src/cli/main.py repo list                      # List all knowledge repositories
python src/cli/main.py repo browse <name> [path]      # Browse a knowledge repository
python src/cli/main.py repo search <name> -q <query>  # Search a knowledge repository
python src/cli/main.py repo export <name> -o <output> # Export a knowledge repository
python src/cli/main.py repo import <source> <name>    # Import a knowledge repository
python src/cli/main.py repo stats <name>              # Display statistics for a repository
python src/cli/main.py repo validate <name>           # Validate a knowledge repository
```

### Usage Examples
```bash
# Create a new repository named 'my-repo'
python src/cli/main.py repo create my-repo

# List all repositories
python src/cli/main.py repo list

# Browse the root of 'my-repo'
python src/cli/main.py repo browse my-repo

# Search for 'python' in 'my-repo'
python src/cli/main.py repo search my-repo -q python

# Export 'my-repo' to a file named 'my-repo.md'
python src/cli/main.py repo export my-repo -o my-repo.md

# Import a repository from 'my-repo.md' and name it 'new-repo'
python src/cli/main.py repo import my-repo.md new-repo

# Display statistics for 'my-repo'
python src/cli/main.py repo stats my-repo

# Validate 'my-repo'
python src/cli/main.py repo validate my-repo
```

## AI Agent Usage Guide

### 1. Basic Interactive Usage
```bash
gemini
```
- Enter interactive mode
- Enable continuous conversation
- Maintain context

### 2. Single Prompt Execution
```bash
gemini "Please review the code"
```

### 3. Debug Mode Usage
```bash
gemini -d "Please diagnose the issue"
```

### 4. Run in Sandbox Environment
```bash
gemini -s "Please test in a safe environment"
```

### 5. Use Specific Model
```bash
gemini -m "gemini-pro" "Please perform advanced analysis"
```

### 6. Auto-approval Mode
```bash
gemini --approval-mode yolo "Please perform tasks automatically"
```

### 7. Allow Specific Tools Only
```bash
gemini --allowed-tools "read_file,write_file" "Please perform file operations"
```

## Best Practices

### 1. Security
- Avoid using `--yolo` option in production environments
- Use `--allowed-tools` to restrict tools to only allowed ones
- Utilize sandbox mode

### 2. Performance
- Activate only necessary extensions (`-e` option)
- Avoid including unnecessary files
- Use debug mode only for troubleshooting

### 3. Maintenance
- Regular extension updates
- Monitor MCP server status
- Utilize session summaries

## Troubleshooting

### Common Issues
1. **Permission Error**: Check `--approval-mode` settings
2. **Memory Shortage**: Monitor with `--show-memory-usage`
3. **Extension Conflicts**: Use `-e` option to use only specific extensions

### Logging and Debugging
```bash
# Run in debug mode
gemini -d "Please analyze the problem situation"

# Check memory usage
gemini --show-memory-usage "Please perform the task"
```

## Configuration Files

Most options can be configured in the `settings.json` file:
- `tools.sandbox`: Sandbox settings
- `ui.showMemoryUsage`: Memory usage display
- `telemetry.*`: Telemetry settings
- `general.checkpointing.*`: Checkpointing settings

Through this guide, AI agents can effectively utilize Gemini CLI.
