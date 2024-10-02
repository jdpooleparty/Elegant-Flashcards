# Elegant-Flashcards

Elegant-Flashcards is a Python-based application for creating and studying flashcards. It provides an intuitive interface for managing decks of flashcards and offers various study modes to enhance learning.

## Features

- Create and manage multiple flashcard decks
- Import flashcards from CSV and JSON files
- Customizable study modes (random order, show/hide known cards)
- Dark mode support
- Sound effects for positive reinforcement
- Simple and elegant user interface

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/jdpooleparty/Elegant-Flashcards.git
   cd Elegant-Flashcards
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the application:
```
python src/main.py
```

## Building the Application

To create a standalone executable:

1. Ensure you have PyInstaller installed:
   ```
   pip install pyinstaller
   ```

2. Run the build script:
   ```
   python build_script.py
   ```

The executable will be created in the `dist` directory.

## Project Structure

- `src/`: Contains the main Python source files
- `Flashcards/`: Directory for storing flashcard deck files
- `resources/`: Contains additional resources like images or sounds
- `data/`: Stores application data
- `build_script.py`: Script for building the standalone executable
- `requirements.txt`: List of Python dependencies
- `config.ini`: Configuration file for application settings


## Contributing

We welcome contributions to Elegant-Flashcards! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.


## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all contributors who have helped shape Elegant-Flashcards
- Inspired by the need for a simple, yet powerful flashcard application