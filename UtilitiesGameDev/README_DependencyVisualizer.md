# C# Dependency Visualizer

A powerful utility for analyzing and visualizing dependencies between C# scripts in your Unity or C# projects. This tool creates an interactive web-based graph showing how your classes are interconnected.

## Features

- **Interactive Graph Visualization**: Explore your codebase with a force-directed graph
- **Dependency Analysis**: Automatically detects:
  - Class inheritance relationships
  - Interface implementations
  - Field type references
  - Method parameter and return types
  - Object instantiations
- **Multiple Layout Options**: Force-directed, circular, and hierarchical layouts
- **Search and Filter**: Quickly find specific classes
- **Detailed Class Information**: View dependencies, dependents, fields, methods, and properties
- **Color-coded Nodes**: Visual indication of dependency complexity
- **Export Capability**: Save the graph as SVG

## Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

## Installation

### Option 1: Using Batch File (Windows Command Prompt)
Simply double-click `run_dependency_visualizer.bat` or run it from the command line:
```batch
run_dependency_visualizer.bat
```
The batch file will automatically install required dependencies on first run.

### Option 2: Using PowerShell
```powershell
.\run_dependency_visualizer.ps1
```

### Option 3: Manual Installation
```bash
# Install dependencies
pip install -r requirements_dependency_viz.txt

# Run the visualizer
python csharp_dependency_visualizer.py
```

## Usage

### Basic Usage
By default, the tool analyzes the `EoAT_EndofAllThings` folder:
```bash
python csharp_dependency_visualizer.py
```

### Custom Directory
Analyze a different directory:
```bash
python csharp_dependency_visualizer.py --root "C:\Path\To\Your\CSharpProject"
```

### Custom Port
Run on a different port:
```bash
python csharp_dependency_visualizer.py --port 8080
```

### Without Auto-opening Browser
```bash
python csharp_dependency_visualizer.py --no-browser
```

## Web Interface Controls

### Graph Interactions
- **Click** on a node to see detailed information
- **Drag** nodes to reposition them
- **Scroll** to zoom in/out
- **Drag background** to pan

### Control Panel Features

#### Search
- Type in the search box to highlight matching classes
- Search is case-insensitive

#### Layout Types
1. **Force Directed**: Natural clustering based on connections
2. **Circular**: All nodes arranged in a circle
3. **Hierarchical**: Arranged by dependency depth

#### Visual Options
- **Link Strength**: Adjust the attraction between connected nodes
- **Node Size**: Uniform, or based on dependency/dependent count
- **Show Labels**: Toggle class name labels
- **Show Arrows**: Toggle directional arrows on connections

#### Actions
- **Reset View**: Return to default zoom and position
- **Export SVG**: Save the current graph as an SVG file

### Node Color Legend
- 🟢 **Green**: No dependencies (independent classes)
- 🔵 **Blue**: 1-3 dependencies (low complexity)
- 🟠 **Orange**: 4-7 dependencies (moderate complexity)
- 🔴 **Red**: 8+ dependencies (high complexity)

## Understanding the Visualization

### Nodes
Each node represents a C# class found in your project. The node properties include:
- Class name
- File path
- Namespace
- Base classes and interfaces
- Dependencies (classes this class uses)
- Dependents (classes that use this class)

### Links
Arrows between nodes show dependency direction:
- An arrow from A to B means "A depends on B"
- Thicker lines indicate stronger relationships

### Class Details Panel
When you click on a node, the sidebar shows:
- Full file path
- List of dependencies (what this class uses)
- List of dependents (what uses this class)
- Base classes and interfaces

## Excluded Directories

By default, the following are excluded from analysis:
- TextMesh Pro
- Packages
- Library
- Temp
- obj
- bin

## Troubleshooting

### "Python is not installed"
Download and install Python 3.x from [python.org](https://python.org)

### "Module not found" errors
Run: `pip install -r requirements_dependency_viz.txt`

### Port already in use
Specify a different port: `python csharp_dependency_visualizer.py --port 8080`

### Graph is too cluttered
1. Use the search to focus on specific classes
2. Click on a node to highlight only its connections
3. Adjust the link strength slider
4. Try different layout types

## Output Files

The tool generates:
- `csharp_dependencies.json`: Raw dependency data
- Web visualization on `http://localhost:5000`

## Tips for Better Analysis

1. **Start with Overview**: Use force-directed layout to see natural clusters
2. **Identify Problem Areas**: Look for red nodes (many dependencies)
3. **Find Core Classes**: Check "Most Depended Upon" in statistics
4. **Trace Dependencies**: Click nodes to see immediate connections
5. **Export for Documentation**: Save SVG for architecture documentation

## Technical Details

The analyzer uses regex patterns to identify:
- Using statements
- Namespace declarations
- Class declarations with inheritance
- Field declarations
- Method signatures
- Property declarations
- Type references in code

## Limitations

- Static analysis only (no runtime dependency detection)
- May miss some dynamic or reflection-based dependencies
- Generic type parameters may not be fully resolved
- Focuses on direct class dependencies

## License

This utility is provided as-is for development use.

---

For issues or suggestions, please check the code in `csharp_dependency_visualizer.py`
