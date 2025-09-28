# C# Dependency Visualizer - Quick Start Guide

## 🚀 Fastest Way to Start

**Just double-click:** `run_complete_analysis.bat`

This will:
1. Analyze all C# scripts in your EoAT project
2. Generate a dependency graph
3. Open an interactive visualization in your browser

## 📁 Files Created

- **analyze_csharp_standalone.py** - The core analyzer (works without Flask)
- **serve_visualization.py** - Web server for visualization
- **csharp_dependency_visualizer.py** - All-in-one version (analyzer + server)
- **templates/dependency_graph.html** - Interactive web interface
- **run_complete_analysis.bat** - One-click runner

## 🎯 What You Can Do

### In the Web Interface:
- **Click and drag** nodes to rearrange
- **Click a node** to see its dependencies and dependents
- **Search** for specific classes
- **Change layouts** (Force, Circular, Hierarchical)
- **Export** the graph as SVG

### Understanding the Graph:
- **Node Size** = Importance (more connections = bigger)
- **Node Color**:
  - 🟢 Green = No dependencies (independent)
  - 🔵 Blue = 1-3 dependencies (simple)
  - 🟠 Orange = 4-7 dependencies (moderate)
  - 🔴 Red = 8+ dependencies (complex)
- **Arrows** = Dependency direction (A→B means A depends on B)

## 📊 Analysis Results

From your project analysis:
- **24 classes** found
- **90 total dependencies**
- **Most Complex Classes:**
  1. AIController (7 dependencies)
  2. AIDifficultySettings (7 dependencies)
  3. TurnManager (7 dependencies)

- **Core Classes** (most used):
  1. Unit (16 other classes depend on it)
  2. GameState (12 dependents)
  3. Player (9 dependents)

## 🔧 Manual Usage

### Analyze a different folder:
```bash
python analyze_csharp_standalone.py --root "C:\Path\To\Your\CSharp\Project"
```

### Just run the visualization:
```bash
python serve_visualization.py
```

### Analyze + Visualize in one command:
```bash
python csharp_dependency_visualizer.py --root "..\EoAT_EndofAllThings"
```

## 🐛 Troubleshooting

### "Flask not found"
Run: `pip install flask flask-cors`

### "Python not found"
Install Python 3.x from python.org

### Port 5000 already in use
Edit serve_visualization.py and change the port number in the last line

## 💡 Tips

1. **Reduce Complexity**: Classes with many dependencies (red nodes) might need refactoring
2. **Find Central Classes**: Classes with many dependents are core to your architecture
3. **Identify Clusters**: Groups of interconnected classes might belong in the same module
4. **Check for Circular Dependencies**: Look for bidirectional arrows between nodes

## 📈 Use Cases

- **Code Review**: Identify overly complex classes
- **Refactoring**: Find classes that need simplification
- **Documentation**: Export graphs for architecture docs
- **Onboarding**: Help new developers understand the codebase
- **Planning**: Identify impact of changes before making them

---

Enjoy exploring your code architecture! 🎉
