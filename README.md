# VLSI Floorplanning Tool - Version 3.0

A sophisticated desktop application for interactive VLSI floorplan visualization and manipulation with advanced connection management and dynamic canvas controls.

## 🚀 Key Features

### **Enhanced Connection System**
- **Double Z-Connectors**: Each connection features Z-shaped connectors at both source and destination ends
- **Perpendicular Edge Connections**: Connections start perpendicular to hardmacro edges to avoid overlap
- **Dynamic Offset Adjustment**: Connection offsets automatically adjust based on overlapping connections
- **Connection Mode Selector**: Toggle between straight lines and Manhattan connections for middle sections

### **Advanced Port Management**
- **Larger Port Bubbles**: 15-unit radius for easier selection and manipulation
- **Full Perimeter Movement**: Ports can slide along the entire perimeter of hardmacros
- **Spread Positioning**: Ports are automatically distributed along edges to prevent overlapping
- **Edge Attachment**: Ports remain attached to hardmacro edges during movement and resizing

### **Interactive Canvas Controls**
- **Dynamic Canvas Sizing**: Canvas automatically adjusts to fit all hardmacros
- **Zoom Controls**: Zoom in (+), zoom out (-), and fit to screen functionality
- **Pan Mode**: Navigate across the canvas when zoomed in/out
- **Auto-Resize**: View automatically adjusts when blocks move outside current view

### **Hardmacro Manipulation**
- **Drag & Drop**: Click and drag hardmacros to move them
- **Resize Handles**: 
  - **Red corner handles**: Reshape aspect ratio while maintaining area
  - **Teal edge handles**: Change width/height while maintaining area
- **Hover Effects**: Visual feedback when hovering over handles
- **Area Preservation**: All reshaping operations maintain the original hardmacro area

## 📋 Requirements

- Python 3.7+
- Tkinter (usually included with Python)
- Matplotlib
- NumPy
- Pandas

## 🛠️ Installation

1. Navigate to the version3 directory:
   ```bash
   cd version3
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements_desktop.txt
   ```

## 🚀 Usage

### Starting the Application
```bash
python floorplan_desktop_v3.py
```

### Loading Data
1. Click "Upload CSV" to select your adjacency matrix file
2. The application will load hardmacros and connections automatically
3. Status bar shows: "Blocks: X | Connections: Y"

### Interactive Controls

#### **Mode Selection**
- **Interactive Mode**: Enable/disable interactive features
- **Shape Mode**: Switch between Rectangle and L-Shape (legacy feature)
- **Connection Mode**: 
  - **Straight**: Middle connections use straight lines
  - **Manhattan**: Middle connections use L-shaped Manhattan routing

#### **Canvas Navigation**
- **Zoom In (+)**: Increase zoom level
- **Zoom Out (-)**: Decrease zoom level
- **Fit**: Fit all blocks to current view
- **Pan Mode**: Enable mouse panning when checked
- **Reset View**: Reset to default view

#### **Hardmacro Manipulation**
- **Move**: Click and drag hardmacros to move them
- **Resize**: 
  - Drag red corner handles to reshape aspect ratio
  - Drag teal edge handles to change width/height
- **Port Movement**: Click and drag port bubbles to move them along hardmacro edges

#### **Connection Management**
- **Port Positioning**: Ports automatically spread along edges to avoid overlap
- **Connection Offsets**: Automatically adjust based on overlapping connections
- **Z-Connectors**: Each connection has Z-shaped connectors at both ends
- **Connection Counts**: Displayed at the middle of each connection path

## 📁 File Structure

```
version3/
├── floorplan_desktop_v3.py      # Main application
├── requirements_desktop.txt     # Python dependencies
├── sample_adjacency_matrix.csv  # Sample data
└── README.md                   # This file
```

## 📊 Data Format

### Adjacency Matrix CSV
The application expects a CSV file with:
- **Row/Column headers**: Hardmacro names
- **Diagonal values**: Hardmacro areas (in µm²)
- **Off-diagonal values**: Connection counts between hardmacros

Example:
```csv
,CPU_Core,Memory_Controller,GPU_Unit
CPU_Core,1000000,50,30
Memory_Controller,50,800000,40
GPU_Unit,30,40,1200000
```

## 🔧 Technical Details

### **Connection Algorithm**
1. **Port Positioning**: Ports are placed along hardmacro edges with spread distribution
2. **Z-Connector Generation**: 
   - First perpendicular line from port
   - Second perpendicular line for direction change
   - Middle connection (straight or Manhattan)
   - Reverse Z at destination
3. **Overlap Prevention**: Dynamic offset calculation based on connection density

### **Canvas Management**
- **Dynamic Sizing**: View automatically adjusts to fit all hardmacros
- **Auto-Resize**: Disabled during interaction, re-enabled on release
- **Zoom Constraints**: Maintains aspect ratio and prevents excessive zoom

### **Port System**
- **Edge Detection**: Automatic detection of which edge a port is on
- **Perimeter Movement**: Constrained movement along hardmacro edges
- **Position Updates**: Automatic updates during hardmacro movement and resizing

## 🎯 Use Cases

### **VLSI Design**
- Interactive floorplan visualization
- Connection routing analysis
- Hardmacro placement optimization
- Design space exploration

### **Educational**
- VLSI design principles demonstration
- Connection routing concepts
- Interactive learning tool

### **Research**
- Floorplanning algorithm development
- Connection optimization studies
- Design methodology evaluation

## 🔄 Version History

### Version 3.0 Features
- ✅ Double Z-connectors for all connections
- ✅ Larger port bubbles (15-unit radius)
- ✅ Full perimeter port movement
- ✅ Spread port positioning
- ✅ Dynamic connection offset adjustment
- ✅ Connection mode selector (Straight/Manhattan)
- ✅ Improved canvas management
- ✅ Enhanced port attachment system
- ✅ Better visual feedback and hover effects

### Previous Versions
- **Version 2.0**: Basic interactive floorplanning with Manhattan connections
- **Version 1.0**: Simple visualization tool

## 🐛 Troubleshooting

### Common Issues

1. **Ports not moving properly**
   - Ensure Interactive Mode is enabled
   - Check that ports are within hardmacro bounds

2. **Connections not visible**
   - Verify CSV file format is correct
   - Check that connection counts are > 0

3. **Canvas not responding**
   - Try Reset View button
   - Ensure Pan Mode is disabled for normal interaction

4. **Performance issues**
   - Reduce number of hardmacros
   - Close other applications to free memory

### Error Messages
- **"Matrix must be square"**: Ensure CSV has equal rows and columns
- **"Number of row names must match number of column names"**: Check CSV header format
- **"Failed to load CSV"**: Verify file format and permissions

## 🔮 Future Enhancements

### Planned Features
- [ ] Multi-layer support
- [ ] Advanced routing algorithms
- [ ] Performance optimization
- [ ] Export functionality
- [ ] Custom connection styles
- [ ] Network analysis tools

### Potential Improvements
- [ ] 3D visualization
- [ ] Real-time collaboration
- [ ] Integration with EDA tools
- [ ] Machine learning optimization
- [ ] Advanced constraint handling

## 📞 Support

For issues, questions, or feature requests:
1. Check the troubleshooting section above
2. Review the technical documentation
3. Test with the provided sample data
4. Ensure all dependencies are properly installed

## 📄 License

This tool is provided as-is for educational and research purposes. Please ensure compliance with any applicable licenses for included libraries and dependencies.

---

**Version 3.0** - Enhanced with advanced connection management and dynamic canvas controls
