"""
Standalone C# Dependency Analyzer (No Flask Required)
This version just analyzes the dependencies and exports to JSON.
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import Dict, Set, List
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class ClassInfo:
    """Information about a C# class"""
    name: str
    filepath: str
    namespace: str
    base_classes: List[str]
    interfaces: List[str]
    dependencies: Set[str]
    dependents: Set[str]
    fields: List[str]
    methods: List[str]
    properties: List[str]
    
    def to_dict(self):
        return {
            "name": self.name,
            "filepath": self.filepath,
            "namespace": self.namespace,
            "base_classes": self.base_classes,
            "interfaces": self.interfaces,
            "dependencies": list(self.dependencies),
            "dependents": list(self.dependents),
            "fields": self.fields,
            "methods": self.methods,
            "properties": self.properties
        }

class CSharpDependencyAnalyzer:
    """Analyzes C# source files for dependencies"""
    
    def __init__(self, root_path: str, exclude_patterns: List[str] = None):
        self.root_path = Path(root_path)
        self.exclude_patterns = exclude_patterns or ["TextMesh Pro", "Packages", "Library", "Temp", "obj", "bin"]
        self.classes: Dict[str, ClassInfo] = {}
        self.namespaces: Dict[str, List[str]] = defaultdict(list)
        self.using_statements: Dict[str, Set[str]] = defaultdict(set)
        
    def should_exclude_file(self, filepath: Path) -> bool:
        """Check if file should be excluded based on patterns"""
        filepath_str = str(filepath)
        for pattern in self.exclude_patterns:
            if pattern in filepath_str:
                return True
        return False
    
    def find_csharp_files(self) -> List[Path]:
        """Find all C# files in the root directory"""
        cs_files = []
        for filepath in self.root_path.rglob("*.cs"):
            if not self.should_exclude_file(filepath):
                cs_files.append(filepath)
        return cs_files
    
    def extract_using_statements(self, content: str) -> List[str]:
        """Extract using statements from C# file"""
        using_pattern = r'using\s+([^;]+);'
        return re.findall(using_pattern, content)
    
    def extract_namespace(self, content: str) -> str:
        """Extract namespace from C# file"""
        namespace_pattern = r'namespace\s+([^\s{]+)'
        match = re.search(namespace_pattern, content)
        return match.group(1) if match else ""
    
    def extract_classes(self, content: str, filepath: Path) -> List[ClassInfo]:
        """Extract class information from C# file"""
        classes = []
        
        # Pattern to match class declarations with inheritance
        class_pattern = r'(?:public\s+|private\s+|protected\s+|internal\s+)?(?:abstract\s+|sealed\s+|static\s+)?(?:partial\s+)?class\s+(\w+)(?:\s*:\s*([^{]+))?'
        
        namespace = self.extract_namespace(content)
        
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            inheritance = match.group(2) or ""
            
            # Parse base classes and interfaces
            base_classes = []
            interfaces = []
            if inheritance:
                inherited = [item.strip() for item in inheritance.split(',')]
                for item in inherited:
                    # Simple heuristic: interfaces often start with 'I'
                    if item.startswith('I') and len(item) > 1 and item[1].isupper():
                        interfaces.append(item)
                    else:
                        base_classes.append(item)
            
            # Extract fields
            fields = self.extract_fields(content, class_name)
            
            # Extract methods
            methods = self.extract_methods(content, class_name)
            
            # Extract properties
            properties = self.extract_properties(content, class_name)
            
            class_info = ClassInfo(
                name=class_name,
                filepath=str(filepath.relative_to(self.root_path)).replace('\\', '/'),
                namespace=namespace,
                base_classes=base_classes,
                interfaces=interfaces,
                dependencies=set(),
                dependents=set(),
                fields=fields,
                methods=methods,
                properties=properties
            )
            
            classes.append(class_info)
        
        return classes
    
    def extract_fields(self, content: str, class_name: str) -> List[str]:
        """Extract field declarations from a class"""
        # Simplified pattern for field declarations
        field_pattern = r'(?:public|private|protected|internal)?\s*(?:static\s+)?(?:readonly\s+)?(\w+(?:<[^>]+>)?)\s+(\w+)\s*[;=]'
        fields = []
        for match in re.finditer(field_pattern, content):
            field_type = match.group(1)
            field_name = match.group(2)
            fields.append(f"{field_type} {field_name}")
        return fields[:20]  # Limit to first 20 fields
    
    def extract_methods(self, content: str, class_name: str) -> List[str]:
        """Extract method signatures from a class"""
        # Pattern for method declarations
        method_pattern = r'(?:public|private|protected|internal)?\s*(?:static\s+)?(?:virtual\s+|override\s+|abstract\s+)?(?:async\s+)?(\w+(?:<[^>]+>)?)\s+(\w+)\s*\([^)]*\)'
        methods = []
        for match in re.finditer(method_pattern, content):
            return_type = match.group(1)
            method_name = match.group(2)
            # Skip constructors
            if method_name != class_name:
                methods.append(f"{return_type} {method_name}()")
        return methods[:20]  # Limit to first 20 methods
    
    def extract_properties(self, content: str, class_name: str) -> List[str]:
        """Extract properties from a class"""
        # Pattern for property declarations
        property_pattern = r'(?:public|private|protected|internal)?\s*(?:static\s+)?(\w+(?:<[^>]+>)?)\s+(\w+)\s*{\s*get'
        properties = []
        for match in re.finditer(property_pattern, content):
            prop_type = match.group(1)
            prop_name = match.group(2)
            properties.append(f"{prop_type} {prop_name}")
        return properties[:20]  # Limit to first 20 properties
    
    def find_type_references(self, content: str, class_info: ClassInfo) -> Set[str]:
        """Find all type references in the content"""
        references = set()
        
        # Look for type references in various contexts
        type_patterns = [
            r'(?:public|private|protected|internal)?\s*(?:static\s+)?(?:readonly\s+)?(\w+)(?:<[^>]+>)?\s+\w+\s*[;=]',  # Fields
            r'(?:public|private|protected|internal)?\s*(?:static\s+)?(?:virtual\s+|override\s+|abstract\s+)?(?:async\s+)?(\w+)(?:<[^>]+>)?\s+\w+\s*\(',  # Method returns
            r'\(\s*(\w+)(?:<[^>]+>)?\s+\w+',  # Method parameters
            r'new\s+(\w+)',  # Object instantiation
            r':\s*(\w+)',  # Inheritance
            r'typeof\((\w+)\)',  # typeof expressions
            r'is\s+(\w+)',  # Type checking
            r'as\s+(\w+)',  # Type casting
            r'<(\w+)>',  # Generic types
        ]
        
        for pattern in type_patterns:
            for match in re.finditer(pattern, content):
                type_name = match.group(1)
                # Filter out common C# keywords and primitive types
                if not self.is_primitive_or_keyword(type_name):
                    references.add(type_name)
        
        return references
    
    def is_primitive_or_keyword(self, type_name: str) -> bool:
        """Check if a type name is a primitive type or C# keyword"""
        primitives_and_keywords = {
            'void', 'int', 'float', 'double', 'string', 'bool', 'byte', 'char', 
            'decimal', 'long', 'short', 'uint', 'ulong', 'ushort', 'object',
            'var', 'dynamic', 'class', 'struct', 'enum', 'interface', 'delegate',
            'public', 'private', 'protected', 'internal', 'static', 'virtual',
            'override', 'abstract', 'sealed', 'readonly', 'const', 'new',
            'return', 'if', 'else', 'while', 'for', 'foreach', 'switch', 'case',
            'break', 'continue', 'goto', 'throw', 'try', 'catch', 'finally',
            'using', 'namespace', 'this', 'base', 'null', 'true', 'false',
            'typeof', 'sizeof', 'is', 'as', 'ref', 'out', 'in', 'params'
        }
        return type_name.lower() in primitives_and_keywords
    
    def analyze(self):
        """Perform the dependency analysis"""
        print("Finding C# files...")
        cs_files = self.find_csharp_files()
        print(f"Found {len(cs_files)} C# files to analyze")
        
        # First pass: extract all classes
        for filepath in cs_files:
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Extract using statements
                using_stmts = self.extract_using_statements(content)
                self.using_statements[str(filepath)] = set(using_stmts)
                
                # Extract classes
                classes = self.extract_classes(content, filepath)
                for class_info in classes:
                    self.classes[class_info.name] = class_info
                    if class_info.namespace:
                        self.namespaces[class_info.namespace].append(class_info.name)
                    
                    # Find type references
                    references = self.find_type_references(content, class_info)
                    class_info.dependencies = references
                    
            except Exception as e:
                print(f"Error processing {filepath}: {e}")
        
        # Second pass: resolve dependencies and build dependents
        for class_name, class_info in self.classes.items():
            resolved_deps = set()
            for dep in class_info.dependencies:
                if dep in self.classes:
                    resolved_deps.add(dep)
                    # Add this class as a dependent of the dependency
                    self.classes[dep].dependents.add(class_name)
            class_info.dependencies = resolved_deps
        
        print(f"Analysis complete. Found {len(self.classes)} classes")
    
    def get_statistics(self) -> Dict:
        """Get statistics about the analyzed codebase"""
        total_classes = len(self.classes)
        total_dependencies = sum(len(c.dependencies) for c in self.classes.values())
        
        # Find most dependent classes
        most_dependent = sorted(
            self.classes.items(),
            key=lambda x: len(x[1].dependencies),
            reverse=True
        )[:10]
        
        # Find most depended upon classes
        most_depended = sorted(
            self.classes.items(),
            key=lambda x: len(x[1].dependents),
            reverse=True
        )[:10]
        
        return {
            "total_classes": total_classes,
            "total_dependencies": total_dependencies,
            "total_namespaces": len(self.namespaces),
            "most_dependent": [(name, len(info.dependencies)) for name, info in most_dependent],
            "most_depended": [(name, len(info.dependents)) for name, info in most_depended],
            "average_dependencies": total_dependencies / total_classes if total_classes > 0 else 0
        }
    
    def export_to_json(self, output_file: str):
        """Export analysis results to JSON"""
        data = {
            "classes": {name: info.to_dict() for name, info in self.classes.items()},
            "namespaces": dict(self.namespaces),
            "statistics": self.get_statistics()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"Exported analysis to {output_file}")
        return data

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Analyze C# dependencies')
    parser.add_argument('--root', type=str, default='..\\EoAT_EndofAllThings',
                      help='Root directory to analyze')
    parser.add_argument('--output', type=str, default='csharp_dependencies.json',
                      help='Output JSON file')
    
    args = parser.parse_args()
    
    # Get absolute path
    root_path = os.path.abspath(args.root)
    
    if not os.path.exists(root_path):
        print(f"Error: Path {root_path} does not exist")
        return
    
    print(f"\nAnalyzing C# dependencies in: {root_path}")
    print("=" * 60)
    
    # Create analyzer and perform analysis
    analyzer = CSharpDependencyAnalyzer(root_path)
    analyzer.analyze()
    
    # Export to JSON
    analyzer.export_to_json(args.output)
    
    # Print statistics
    stats = analyzer.get_statistics()
    print("\n" + "=" * 60)
    print("DEPENDENCY ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"Total Classes: {stats['total_classes']}")
    print(f"Total Dependencies: {stats['total_dependencies']}")
    print(f"Total Namespaces: {stats['total_namespaces']}")
    print(f"Average Dependencies per Class: {stats['average_dependencies']:.2f}")
    
    print("\n📊 Most Dependent Classes (complexity indicators):")
    for i, (name, count) in enumerate(stats['most_dependent'][:5], 1):
        print(f"  {i}. {name}: {count} dependencies")
    
    print("\n🎯 Core Classes (most used by others):")
    for i, (name, count) in enumerate(stats['most_depended'][:5], 1):
        print(f"  {i}. {name}: {count} dependents")
    
    print("\n" + "=" * 60)
    print(f"✅ Results saved to: {args.output}")
    print("\nTo visualize the dependencies:")
    print("  1. Install Flask: pip install flask flask-cors")
    print("  2. Run: python csharp_dependency_visualizer.py")
    print("  3. Open: http://localhost:5000")

if __name__ == '__main__':
    main()
