# run.py - Application Runner Script

"""
Flask Application Runner

This script initializes and runs the Flask blog application.
It's the entry point for starting the development server.

Usage:
    python run.py

Environment Variables:
    FLASK_ENV: Set to 'development' for debug mode
    FLASK_APP: Should point to this file (run.py)
"""

import os

# Create Flask application instance
from app import app

if __name__ == '__main__':
    """
    Run the Flask development server.
    
    Configuration:
    - debug=True: Enable debug mode for development
    - host='127.0.0.1': Listen on localhost only
    - port=5000: Default Flask port
    - threaded=True: Handle multiple requests simultaneously
    """
    
    # Get configuration from environment variables
    debug_mode = os.environ.get('FLASK_ENV') == 'development' or True  # Default to debug for learning
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 5000))
    
    print("=" * 60)
    print("🚀 Starting Flask Blog Application")
    print("=" * 60)
    print(f"📍 URL: http://{host}:{port}")
    print(f"🔧 Debug Mode: {'ON' if debug_mode else 'OFF'}")
    print(f"🗃️  Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print("=" * 60)
    print("📝 Available Routes:")
    print("   • / (Homepage)")
    print("   • /login (User Login)")
    print("   • /register (User Registration)")
    print("   • /create-post (Create New Post)")
    print("   • /post/<id> (View Post)")
    print("   • /api/posts (API: Get Posts)")
    print("   • /api/search (API: Search Posts)")
    print("=" * 60)
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        # Start the development server
        app.run(
            debug=debug_mode,
            host=host,
            port=port,
            threaded=True,
            use_reloader=debug_mode
        )
    except KeyboardInterrupt:
        print("\n👋 Flask Blog Application stopped!")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        
    print("🔧 For production deployment, use: gunicorn run:app")