# Fantasy RPG Text Adventure Game - Documentation

This document provides a detailed explanation of each file in the project.

## Core Files

### `app.py`
Main Streamlit application entry point.
- Implements the web-based user interface using Streamlit
- Handles game screens (main menu, character creation, game screen, etc.)
- Provides a stylish UI with custom CSS
- Manages session state and game flow
- Checks for required environment variables

### `main.py`
Console version of the game.
- Provides a command-line interface for the game
- Handles user input and game flow
- Includes menu system for character management
- Offers text-based game interface

### `test_connections.py`
Test script for verifying external service connections.
- Tests MongoDB connection and database setup
- Tests Google Gemini API connection
- Provides diagnostic information about the game's data state

### `init_mongodb.py`
Database initialization script.
- Sets up initial MongoDB collections
- Populates the database with game data:
  - Items
  - World locations
  - Quests
  - NPCs
  - Enemies

## Game Module (`game/`)

### `game_engine.py`
Core game logic implementation.
- Manages game state and player actions
- Handles character creation and management
- Processes game commands
- Manages combat, inventory, and quest systems
- Integrates with MongoDB and AI systems

### `database.py`
MongoDB database operations.
- Handles all database interactions
- Manages collections for players, items, quests, etc.
- Provides CRUD operations for game data
- Initializes game data if needed

### `ai_generator.py`
Google Gemini AI integration.
- Generates dynamic game content
- Creates rich location descriptions
- Handles NPC dialogue
- Generates combat narratives
- Provides contextual responses to player actions

### `ai_utils.py`
AI utility functions.
- Provides wrapper around AIGenerator
- Simplifies AI response generation
- Manages AI context

## Game Data (`game/data/`)

### `enemies.py`
Enemy definitions and configurations.
- Defines enemy types and properties
- Specifies combat stats
- Sets up loot tables
- Configures XP and gold rewards

### `npcs.py`
NPC (Non-Player Character) definitions.
- Defines NPCs and their properties
- Specifies dialogue options
- Sets up quest relationships
- Configures shop inventories

### `__init__.py`
Package initialization files for Python modules.

## Streamlit Components (`streamlit_app/`)

### (Empty/Planned Files)
The following files are currently empty but planned for future development:
- `app.py` & `app_modular.py`: Alternative Streamlit implementations
- `custom.css`: Additional styling
- Components:
  - `character.py`: Character management UI
  - `combat.py`: Combat system UI
  - `inventory.py`: Inventory management UI
  - `quests.py`: Quest tracking UI
- Utils:
  - `ai_helper.py`: AI integration utilities
  - `database.py`: Database utilities
  - `session.py`: Session management

## Configuration Files

### `.env`
Environment variables configuration.
- MongoDB connection string
- Google Gemini API key
- (Note: This file should not be committed to version control)

### `requirements.txt`
Project dependencies.
- pymongo: MongoDB driver
- google-generativeai: Google Gemini API
- python-dotenv: Environment variable management
- streamlit: Web interface framework

## Documentation Files

### `README.md`
Project overview and setup instructions.
- Features and capabilities
- Installation instructions
- Usage guide
- Project structure
- License information

### `overview.md`
Detailed project documentation.
- Project architecture
- Technology stack
- Database schema
- AI integration details
- Future enhancements

### `srs.md`
Software Requirements Specification.
- Detailed requirements documentation
- System architecture
- Data models
- Functional requirements
- Non-functional requirements

## VS Code Configuration

### `.vscode/settings.json`
Editor-specific settings.
- Workspace configuration
- Extension settings

## Additional Files

### `.gitattributes`
Git configuration file.
- File handling rules
- Text file normalization
