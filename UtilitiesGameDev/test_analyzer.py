"""Quick test of the C# dependency analyzer"""
import os
import sys
from csharp_dependency_visualizer import CSharpDependencyAnalyzer

def test_analyzer():
    # Test on the Scripts folder
    root_path = os.path.abspath("..\\EoAT_EndofAllThings\\Assets\\Scripts")
    
    if not os.path.exists(root_path):
        print(f"Error: Path {root_path} does not exist")
        return
    
    print(f"Analyzing C# files in: {root_path}")
    print("-" * 50)
    
    # Create analyzer
    analyzer = CSharpDependencyAnalyzer(root_path)
    
    # Run analysis
    analyzer.analyze()
    
    # Get statistics
    stats = analyzer.get_statistics()
    
    print(f"\n✓ Analysis Complete!")
    print(f"  Total Classes: {stats['total_classes']}")
    print(f"  Total Dependencies: {stats['total_dependencies']}")
    print(f"  Average Dependencies: {stats['average_dependencies']:.2f}")
    
    if stats['most_dependent']:
        print(f"\nMost Complex Classes (most dependencies):")
        for name, count in stats['most_dependent'][:3]:
            print(f"  • {name}: {count} dependencies")
    
    if stats['most_depended']:
        print(f"\nCore Classes (most used by others):")
        for name, count in stats['most_depended'][:3]:
            print(f"  • {name}: {count} dependents")
    
    # Export to JSON
    analyzer.export_to_json("csharp_dependencies.json")
    print(f"\n✓ Exported to csharp_dependencies.json")
    
    print("\n" + "=" * 50)
    print("To visualize, run:")
    print("  python csharp_dependency_visualizer.py")
    print("\nThen open http://localhost:5000 in your browser")

if __name__ == "__main__":
    test_analyzer()
