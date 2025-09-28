"""
Web server for C# Dependency Visualization
Run this after running analyze_csharp_standalone.py
"""

import os
import json
import webbrowser
import sys

def main():
    # Check if analysis file exists
    if not os.path.exists('csharp_dependencies.json'):
        print("Error: csharp_dependencies.json not found!")
        print("Please run 'python analyze_csharp_standalone.py' first")
        return
    
    try:
        # Try to import Flask
        from flask import Flask, render_template, jsonify
        from flask_cors import CORS
    except ImportError:
        print("Flask is not installed. Installing now...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "flask-cors"])
        print("Flask installed! Please run this script again.")
        return
    
    # Create Flask app
    app = Flask(__name__, template_folder='templates')
    CORS(app)
    
    # Load the analysis data
    with open('csharp_dependencies.json', 'r') as f:
        analysis_data = json.load(f)
    
    @app.route('/')
    def index():
        """Main visualization page"""
        return render_template('dependency_graph.html')
    
    @app.route('/api/data')
    def get_data():
        """API endpoint to get analysis data"""
        return jsonify(analysis_data)
    
    @app.route('/api/stats')
    def get_stats():
        """API endpoint to get statistics"""
        if 'statistics' in analysis_data:
            return jsonify(analysis_data['statistics'])
        return jsonify({"error": "No statistics available"}), 404
    
    @app.route('/api/class/<class_name>')
    def get_class_details(class_name):
        """API endpoint to get details for a specific class"""
        if 'classes' in analysis_data:
            if class_name in analysis_data['classes']:
                return jsonify(analysis_data['classes'][class_name])
        return jsonify({"error": "Class not found"}), 404
    
    print("\n" + "=" * 60)
    print("C# DEPENDENCY VISUALIZATION SERVER")
    print("=" * 60)
    
    # Print some stats
    stats = analysis_data.get('statistics', {})
    print(f"Loaded analysis with {stats.get('total_classes', 0)} classes")
    print(f"Total dependencies: {stats.get('total_dependencies', 0)}")
    
    print("\n🚀 Starting web server...")
    print(f"📊 Open http://localhost:5000 in your browser")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60 + "\n")
    
    # Open browser
    webbrowser.open('http://localhost:5000')
    
    # Start server
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    main()
