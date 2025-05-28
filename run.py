"""
Run script for the Phantom Words Dashboard.
This script serves as an entry point to run the Dash application.
"""
from src.app import app

def main():
    """Run the Dash application server."""
    app.run_server(debug=True, host="0.0.0.0", port=8050)

if __name__ == "__main__":
    main()
