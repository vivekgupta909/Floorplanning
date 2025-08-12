#!/usr/bin/env python3
"""
Floorplanning Tool - Version 2.0
Enhanced desktop application with improved handles and non-rectilinear shapes
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.patches as patches

class FloorplanToolV2:
    def __init__(self, root):
        self.root = root
        self.root.title("Floorplanning Tool - Version 3.0")
        self.root.geometry("1400x900")
        
        # Data storage
        self.blocks = []
        self.connections = []
        self.hardmacro_names = []
        
        # Interactive state
        self.selected_block = None
        self.dragging = False
        self.resize_mode = None
        self.selected_port = None
        self.port_dragging = False  # 'move', 'width', 'height', 'corner'
        self.panning = False  # For canvas panning
        self.last_mouse_pos = None
        self.hover_handle = None
        
        # Port configuration
        self.PORT_RADIUS = 15  # Larger radius for port bubbles
        
        # View management
        
        # Handle configuration
        self.handle_config = {
            'corner_size': 25,      # Larger corner handles
            'edge_width': 15,       # Edge handle width
            'edge_height': 25,      # Edge handle height
            'colors': {
                'corner': '#FF6B6B',    # Red for corners
                'edge': '#4ECDC4',      # Teal for edges
                'hover': '#FFE66D',     # Yellow for hover
                'selected': '#FF8E8E'   # Light red for selected
            }
        }
        
        # Create GUI
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top controls
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Upload button
        self.upload_btn = ttk.Button(control_frame, text="Upload CSV", command=self.upload_csv)
        self.upload_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Interactive controls
        self.interactive_var = tk.BooleanVar(value=True)
        self.interactive_cb = ttk.Checkbutton(control_frame, text="Interactive Mode", 
                                            variable=self.interactive_var)
        self.interactive_cb.pack(side=tk.LEFT, padx=(0, 10))
        
        # Shape mode controls
        self.shape_mode_var = tk.StringVar(value="rectangle")
        shape_frame = ttk.LabelFrame(control_frame, text="Shape Mode")
        shape_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Radiobutton(shape_frame, text="Rectangle", variable=self.shape_mode_var, 
                       value="rectangle").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(shape_frame, text="L-Shape", variable=self.shape_mode_var, 
                       value="lshape").pack(side=tk.LEFT, padx=5)
        
        # Connection mode controls
        conn_frame = ttk.LabelFrame(control_frame, text="Connection Mode")
        conn_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        self.connection_mode_var = tk.StringVar(value="straight")
        ttk.Radiobutton(conn_frame, text="Straight", variable=self.connection_mode_var, 
                       value="straight").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(conn_frame, text="Manhattan", variable=self.connection_mode_var, 
                       value="manhattan").pack(side=tk.LEFT, padx=5)
        
        # Reset view button
        self.reset_btn = ttk.Button(control_frame, text="Reset View", command=self.reset_view)
        self.reset_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Zoom controls
        zoom_frame = ttk.Frame(control_frame)
        zoom_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(zoom_frame, text="Zoom:").pack(side=tk.LEFT)
        
        self.zoom_in_btn = ttk.Button(zoom_frame, text="+", width=3, command=self.zoom_in)
        self.zoom_in_btn.pack(side=tk.LEFT, padx=2)
        
        self.zoom_out_btn = ttk.Button(zoom_frame, text="-", width=3, command=self.zoom_out)
        self.zoom_out_btn.pack(side=tk.LEFT, padx=2)
        
        self.fit_btn = ttk.Button(zoom_frame, text="Fit", width=5, command=self.fit_to_screen)
        self.fit_btn.pack(side=tk.LEFT, padx=2)
        
        # Pan mode toggle
        self.pan_var = tk.BooleanVar(value=False)
        self.pan_btn = ttk.Checkbutton(zoom_frame, text="Pan Mode", variable=self.pan_var)
        self.pan_btn.pack(side=tk.LEFT, padx=(10, 2))
        
        # Info labels
        self.info_label = ttk.Label(control_frame, text="No data loaded")
        self.info_label.pack(side=tk.LEFT)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Floorplan view tab
        self.floorplan_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.floorplan_frame, text="Interactive Floorplan")
        
        # Create matplotlib figure for floorplan with full-screen canvas
        self.fig = Figure(figsize=(12, 8))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, self.floorplan_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Set up dynamic canvas sizing
        self.auto_resize_view = True  # Control when to auto-resize view
        self.ax.set_xlim(0, 1000)
        self.ax.set_ylim(0, 1000)
        
        # Connect mouse events
        self.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        self.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        
        # Properties tab
        self.properties_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.properties_frame, text="Block Properties")
        
        # Create properties widgets
        self.create_properties_widgets()
        
        # Connections tab
        self.connections_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.connections_frame, text="Connections")
        
        # Create connections list
        self.create_connections_widgets()
        
        # Instructions
        self.create_instructions()
        
        # Initial plot
        self.update_plot()
        
    def create_instructions(self):
        """Create instruction panel"""
        instruction_frame = ttk.LabelFrame(self.floorplan_frame, text="Instructions")
        instruction_frame.pack(fill=tk.X, pady=(0, 10))
        
        instructions = """
        Interactive Controls (Version 2.0):
        • Click and drag blocks to move them
        • Drag RED corner handles to reshape aspect ratio (area stays constant)
        • Drag TEAL edge handles to change width/height (area stays constant)
        • Hover over handles for visual feedback
        • Use Shape Mode to switch between rectangle and L-shape
        • Use Properties tab for precise editing
        """
        
        ttk.Label(instruction_frame, text=instructions, justify=tk.LEFT).pack(padx=5, pady=5)
        
    def create_properties_widgets(self):
        # Scrollable frame for properties
        canvas = tk.Canvas(self.properties_frame)
        scrollbar = ttk.Scrollbar(self.properties_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.properties_container = scrollable_frame
        
    def create_connections_widgets(self):
        # Scrollable frame for connections
        canvas = tk.Canvas(self.connections_frame)
        scrollbar = ttk.Scrollbar(self.connections_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.connections_container = scrollable_frame
        
    def get_handle_at_position(self, x, y, block):
        """Get handle type at given position with improved detection"""
        corner_size = self.handle_config['corner_size']
        edge_width = self.handle_config['edge_width']
        edge_height = self.handle_config['edge_height']
        
        # Corner handles (all four corners)
        corners = [
            (block['x'] + block['width'] - corner_size, block['y'] + block['height'] - corner_size),  # Top-right
            (block['x'] + block['width'] - corner_size, block['y']),                                  # Bottom-right
            (block['x'], block['y'] + block['height'] - corner_size),                                 # Top-left
            (block['x'], block['y'])                                                                   # Bottom-left
        ]
        
        for i, (cx, cy) in enumerate(corners):
            if (x >= cx and x <= cx + corner_size and 
                y >= cy and y <= cy + corner_size):
                return f'corner_{i}'
        
        # Edge handles (right and bottom edges)
        if (x >= block['x'] + block['width'] - edge_width and 
            block['y'] < y < block['y'] + block['height']):
            return 'edge_right'
        
        if (y >= block['y'] + block['height'] - edge_height and 
            block['x'] < x < block['x'] + block['width']):
            return 'edge_bottom'
        
        return None
        
    def on_mouse_press(self, event):
        """Handle mouse press events with improved handle detection"""
        if not self.interactive_var.get() or not self.blocks:
            return
            
        if event.inaxes != self.ax:
            return
        
        # Check if pan mode is enabled
        if self.pan_var.get():
            self.panning = True
            self.last_mouse_pos = (event.xdata, event.ydata)
            return
        
        # First check if clicking on a port
        port_conn_index, port_type = self.get_port_at_position(event.xdata, event.ydata)
        if port_conn_index is not None:
            self.selected_port = (port_conn_index, port_type)
            self.port_dragging = True
            self.last_mouse_pos = (event.xdata, event.ydata)
            self.update_plot()
            return
            
        # Find clicked block
        clicked_block = self.get_block_at_position(event.xdata, event.ydata)
        
        if clicked_block:
            self.selected_block = clicked_block
            self.dragging = True
            self.last_mouse_pos = (event.xdata, event.ydata)
            
            # Check if clicking on resize handle
            handle_type = self.get_handle_at_position(event.xdata, event.ydata, clicked_block)
            
            if handle_type:
                if handle_type.startswith('corner'):
                    self.resize_mode = 'corner'
                elif handle_type.startswith('edge'):
                    if 'right' in handle_type:
                        self.resize_mode = 'width'
                    else:
                        self.resize_mode = 'height'
                else:
                    self.resize_mode = 'move'
            else:
                self.resize_mode = 'move'
                
            self.update_plot()
        else:
            self.selected_block = None
            self.dragging = False
            self.resize_mode = None
            self.selected_port = None
            self.port_dragging = False
            self.update_plot()
            
    def on_mouse_move(self, event):
        """Handle mouse move events with improved feedback"""
        if not self.interactive_var.get():
            return
            
        if event.inaxes != self.ax:
            return
            
        # Update hover state
        if self.selected_block:
            handle_type = self.get_handle_at_position(event.xdata, event.ydata, self.selected_block)
            if handle_type != self.hover_handle:
                self.hover_handle = handle_type
                self.update_plot()
        
        # Handle panning
        if self.panning:
            if self.last_mouse_pos is not None:
                dx = event.xdata - self.last_mouse_pos[0]
                dy = event.ydata - self.last_mouse_pos[1]
                
                # Get current view limits
                x_min, x_max = self.ax.get_xlim()
                y_min, y_max = self.ax.get_ylim()
                
                # Update view limits
                self.ax.set_xlim(x_min - dx, x_max - dx)
                self.ax.set_ylim(y_min - dy, y_max - dy)
                
                self.last_mouse_pos = (event.xdata, event.ydata)
                self.canvas.draw()
            return
        
        # Handle port dragging
        if self.port_dragging and self.selected_port:
            conn_index, port_type = self.selected_port
            self.move_port_along_edge(conn_index, port_type, event.xdata, event.ydata)
            self.last_mouse_pos = (event.xdata, event.ydata)
            self.update_plot()
            return
            
        if not self.dragging or not self.selected_block:
            return
            
        if self.last_mouse_pos is None:
            return
            
        dx = event.xdata - self.last_mouse_pos[0]
        dy = event.ydata - self.last_mouse_pos[1]
        
        if self.resize_mode == 'move':
            # Move block
            self.selected_block['x'] += dx
            self.selected_block['y'] += dy
            
            # Update port positions for connections involving this block
            self.update_ports_for_block_movement(self.selected_block, dx, dy)
        elif self.resize_mode == 'width':
            # Resize width (maintain area)
            new_width = self.selected_block['width'] + dx
            if new_width > 10:  # Minimum size
                old_area = self.selected_block['area']
                old_width = self.selected_block['width']
                self.selected_block['width'] = new_width
                self.selected_block['height'] = old_area / new_width
                
                # Update port positions for width resize
                self.update_ports_for_block_resize(self.selected_block, 'width', old_width, new_width)
                print(f"Width resize: {new_width:.1f} × {self.selected_block['height']:.1f} = {old_area:.1f}")
        elif self.resize_mode == 'height':
            # Resize height (maintain area)
            new_height = self.selected_block['height'] + dy
            if new_height > 10:  # Minimum size
                old_area = self.selected_block['area']
                old_height = self.selected_block['height']
                self.selected_block['height'] = new_height
                self.selected_block['width'] = old_area / new_height
                
                # Update port positions for height resize
                self.update_ports_for_block_resize(self.selected_block, 'height', old_height, new_height)
                print(f"Height resize: {self.selected_block['width']:.1f} × {new_height:.1f} = {old_area:.1f}")
        elif self.resize_mode == 'corner':
            # Reshape by changing aspect ratio while maintaining area
            new_width = self.selected_block['width'] + dx
            new_height = self.selected_block['height'] + dy
            if new_width > 10 and new_height > 10:
                old_area = self.selected_block['area']
                old_width = self.selected_block['width']
                old_height = self.selected_block['height']
                self.selected_block['width'] = new_width
                self.selected_block['height'] = old_area / new_width
                
                # Update port positions for corner resize
                self.update_ports_for_block_resize(self.selected_block, 'corner', old_width, new_width, old_height, new_height)
                print(f"Corner reshape: {new_width:.1f} × {self.selected_block['height']:.1f} = {old_area:.1f}")
        
        self.last_mouse_pos = (event.xdata, event.ydata)
        self.update_plot()
        
    def on_mouse_release(self, event):
        """Handle mouse release events"""
        self.dragging = False
        self.port_dragging = False
        self.panning = False
        self.resize_mode = None
        self.last_mouse_pos = None
        self.hover_handle = None
        
    def get_block_at_position(self, x, y):
        """Find block at given position"""
        for block in self.blocks:
            if (x >= block['x'] and x <= block['x'] + block['width'] and
                y >= block['y'] and y <= block['y'] + block['height']):
                return block
        return None
        
    def reset_view(self):
        """Reset the plot view to fit all blocks"""
        self.auto_resize_view = True
        self.update_plot()
        
    def upload_csv(self):
        """Upload and process CSV file"""
        try:
            filename = filedialog.askopenfilename(
                title="Select CSV file",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if not filename:
                return
                
            # Read CSV with header
            df = pd.read_csv(filename, index_col=0)
            
            # Get hardmacro names
            self.hardmacro_names = df.index.tolist()
            
            # Validate
            if len(self.hardmacro_names) != len(df.columns):
                messagebox.showerror("Error", "Number of row names must match number of column names")
                return
                
            adjacency_matrix = df.values
            
            if adjacency_matrix.shape[0] != adjacency_matrix.shape[1]:
                messagebox.showerror("Error", "Matrix must be square")
                return
                
            # Process data
            self.process_adjacency_matrix(adjacency_matrix)
            
            # Update UI
            self.update_info()
            self.update_plot()
            self.update_properties()
            self.update_connections()
            
            messagebox.showinfo("Success", f"Loaded {len(self.blocks)} hardmacros with {len(self.connections)} connections")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV: {str(e)}")
            
    def process_adjacency_matrix(self, matrix):
        """Process adjacency matrix into blocks and connections"""
        self.blocks = []
        self.connections = []
        
        for i in range(len(matrix)):
            # Create block
            area = matrix[i][i]
            side_length = np.sqrt(area)
            
            block = {
                'id': i,
                'name': self.hardmacro_names[i],
                'area': area,
                'width': side_length,
                'height': side_length,
                'x': 100 + (i % 3) * 800,  # Spread blocks across canvas
                'y': 100 + (i // 3) * 400,
                'shape_type': 'rectangle'  # Default shape type
            }
            self.blocks.append(block)
            
        # Find connections
        for i in range(len(matrix)):
            for j in range(i+1, len(matrix)):
                if matrix[i][j] > 0:
                    connection = {
                        'from': i,
                        'to': j,
                        'from_name': self.hardmacro_names[i],
                        'to_name': self.hardmacro_names[j],
                        'connections': matrix[i][j]
                    }
                    self.connections.append(connection)
                    
    def update_info(self):
        """Update info label"""
        if self.blocks:
            self.info_label.config(text=f"Blocks: {len(self.blocks)} | Connections: {len(self.connections)}")
        else:
            self.info_label.config(text="No data loaded")
            
    def find_edge_connection_points(self, from_block, to_block, connection_index=0):
        """Find the best edge points for connecting two blocks with spread positioning"""
        # Calculate block centers
        from_center_x = from_block['x'] + from_block['width'] / 2
        from_center_y = from_block['y'] + from_block['height'] / 2
        to_center_x = to_block['x'] + to_block['width'] / 2
        to_center_y = to_block['y'] + to_block['height'] / 2
        
        # Determine relative positions
        dx = to_center_x - from_center_x
        dy = to_center_y - from_center_y
        
        # Calculate spread offset based on connection index
        spread_offset = connection_index * 30  # 30 units spacing between connections
        
        # Find start point on from_block edge with spread
        if abs(dx) > abs(dy):
            # More horizontal connection
            if dx > 0:
                # To block is to the right - use right edge of from_block
                start_x = from_block['x'] + from_block['width']
                # Spread along the right edge
                start_y = from_center_y + spread_offset
                # Ensure it stays within block bounds
                start_y = max(from_block['y'] + 20, min(from_block['y'] + from_block['height'] - 20, start_y))
            else:
                # To block is to the left - use left edge of from_block
                start_x = from_block['x']
                # Spread along the left edge
                start_y = from_center_y + spread_offset
                # Ensure it stays within block bounds
                start_y = max(from_block['y'] + 20, min(from_block['y'] + from_block['height'] - 20, start_y))
        else:
            # More vertical connection
            if dy > 0:
                # To block is above - use top edge of from_block
                start_x = from_center_x + spread_offset
                start_y = from_block['y'] + from_block['height']
                # Ensure it stays within block bounds
                start_x = max(from_block['x'] + 20, min(from_block['x'] + from_block['width'] - 20, start_x))
            else:
                # To block is below - use bottom edge of from_block
                start_x = from_center_x + spread_offset
                start_y = from_block['y']
                # Ensure it stays within block bounds
                start_x = max(from_block['x'] + 20, min(from_block['x'] + from_block['width'] - 20, start_x))
        
        # Find end point on to_block edge with spread
        if abs(dx) > abs(dy):
            # More horizontal connection
            if dx > 0:
                # From block is to the left - use left edge of to_block
                end_x = to_block['x']
                # Spread along the left edge
                end_y = to_center_y + spread_offset
                # Ensure it stays within block bounds
                end_y = max(to_block['y'] + 20, min(to_block['y'] + to_block['height'] - 20, end_y))
            else:
                # From block is to the right - use right edge of to_block
                end_x = to_block['x'] + to_block['width']
                # Spread along the right edge
                end_y = to_center_y + spread_offset
                # Ensure it stays within block bounds
                end_y = max(to_block['y'] + 20, min(to_block['y'] + to_block['height'] - 20, end_y))
        else:
            # More vertical connection
            if dy > 0:
                # From block is below - use bottom edge of to_block
                end_x = to_center_x + spread_offset
                end_y = to_block['y']
                # Ensure it stays within block bounds
                end_x = max(to_block['x'] + 20, min(to_block['x'] + to_block['width'] - 20, end_x))
            else:
                # From block is above - use top edge of to_block
                end_x = to_center_x + spread_offset
                end_y = to_block['y'] + to_block['height']
                # Ensure it stays within block bounds
                end_x = max(to_block['x'] + 20, min(to_block['x'] + to_block['width'] - 20, end_x))
        
        return (start_x, start_y), (end_x, end_y)
    
    def get_edge_type(self, point, block):
        """Determine which edge of a block a point is on"""
        x, y = point
        block_x, block_y = block['x'], block['y']
        block_w, block_h = block['width'], block['height']
        
        # Check if point is on the right edge
        if abs(x - (block_x + block_w)) < 5:
            return 'right'
        # Check if point is on the left edge
        elif abs(x - block_x) < 5:
            return 'left'
        # Check if point is on the top edge
        elif abs(y - (block_y + block_h)) < 5:
            return 'top'
        # Check if point is on the bottom edge
        elif abs(y - block_y) < 5:
            return 'bottom'
        else:
            return 'unknown'
    
    def get_port_at_position(self, x, y):
        """Find if a port bubble is at the given position"""
        port_radius = self.PORT_RADIUS
        
        for i, conn in enumerate(self.connections):
            if 'port_positions' in conn:
                start_port = conn['port_positions']['start']
                end_port = conn['port_positions']['end']
                
                # Check start port
                if ((x - start_port['x'])**2 + (y - start_port['y'])**2) <= port_radius**2:
                    return i, 'start'
                
                # Check end port
                if ((x - end_port['x'])**2 + (y - end_port['y'])**2) <= port_radius**2:
                    return i, 'end'
        
        return None, None
    
    def move_port_along_edge(self, conn_index, port_type, new_x, new_y):
        """Move a port along the full perimeter of its block"""
        conn = self.connections[conn_index]
        port = conn['port_positions'][port_type]
        
        # Determine which block this port belongs to
        if port_type == 'start':
            block = self.blocks[conn['from']]
        else:
            block = self.blocks[conn['to']]
        
        block_x, block_y = block['x'], block['y']
        block_w, block_h = block['width'], block['height']
        
        # Find the closest point on the block's perimeter to the new position
        # Calculate distances to each edge
        dist_to_left = abs(new_x - block_x)
        dist_to_right = abs(new_x - (block_x + block_w))
        dist_to_bottom = abs(new_y - block_y)
        dist_to_top = abs(new_y - (block_y + block_h))
        
        # Find the minimum distance to determine which edge to snap to
        min_dist = min(dist_to_left, dist_to_right, dist_to_bottom, dist_to_top)
        
        if min_dist == dist_to_left:
            # Snap to left edge
            port['x'] = block_x
            port['y'] = max(block_y, min(block_y + block_h, new_y))
            port['edge'] = 'left'
        elif min_dist == dist_to_right:
            # Snap to right edge
            port['x'] = block_x + block_w
            port['y'] = max(block_y, min(block_y + block_h, new_y))
            port['edge'] = 'right'
        elif min_dist == dist_to_bottom:
            # Snap to bottom edge
            port['x'] = max(block_x, min(block_x + block_w, new_x))
            port['y'] = block_y
            port['edge'] = 'bottom'
        else:  # dist_to_top
            # Snap to top edge
            port['x'] = max(block_x, min(block_x + block_w, new_x))
            port['y'] = block_y + block_h
            port['edge'] = 'top'
    
    def update_ports_for_block_movement(self, block, dx, dy):
        """Update port positions when a block is moved"""
        block_id = block['id']
        
        for conn in self.connections:
            if 'port_positions' in conn:
                # Update start port if it belongs to this block
                if conn['from'] == block_id:
                    start_port = conn['port_positions']['start']
                    start_port['x'] += dx
                    start_port['y'] += dy
                
                # Update end port if it belongs to this block
                if conn['to'] == block_id:
                    end_port = conn['port_positions']['end']
                    end_port['x'] += dx
                    end_port['y'] += dy
    
    def update_ports_for_block_resize(self, block, resize_type, old_width, new_width, old_height=None, new_height=None):
        """Update port positions when a block is resized"""
        block_id = block['id']
        
        for conn in self.connections:
            if 'port_positions' in conn:
                # Update start port if it belongs to this block
                if conn['from'] == block_id:
                    self.update_port_for_resize(conn['port_positions']['start'], block, resize_type, old_width, new_width, old_height, new_height)
                
                # Update end port if it belongs to this block
                if conn['to'] == block_id:
                    self.update_port_for_resize(conn['port_positions']['end'], block, resize_type, old_width, new_width, old_height, new_height)
    
    def get_connection_offset(self, conn, start_port, end_port, base_offset):
        """Calculate offset for a connection to avoid overlap with other connections"""
        # Count how many connections use the same edge as this connection
        start_edge = start_port['edge']
        end_edge = end_port['edge']
        
        # Find all connections that use the same start edge
        same_start_edge_count = 0
        same_end_edge_count = 0
        
        for other_conn in self.connections:
            if 'port_positions' in other_conn:
                other_start = other_conn['port_positions']['start']
                other_end = other_conn['port_positions']['end']
                
                # Count connections using same start edge
                if (other_start['edge'] == start_edge and 
                    abs(other_start['x'] - start_port['x']) < 5 and 
                    abs(other_start['y'] - start_port['y']) < 5):
                    same_start_edge_count += 1
                
                # Count connections using same end edge
                if (other_end['edge'] == end_edge and 
                    abs(other_end['x'] - end_port['x']) < 5 and 
                    abs(other_end['y'] - end_port['y']) < 5):
                    same_end_edge_count += 1
        
        # Increase offset based on number of overlapping connections
        offset_multiplier = max(same_start_edge_count, same_end_edge_count)
        return base_offset + (offset_multiplier * 20)  # Add 20 units per overlapping connection
    
    def update_port_for_resize(self, port, block, resize_type, old_width, new_width, old_height=None, new_height=None):
        """Update a single port position during block resize"""
        edge = port['edge']
        block_x, block_y = block['x'], block['y']
        block_w, block_h = block['width'], block['height']
        
        if resize_type == 'width':
            if edge == 'right':
                # Port stays on right edge, update x position
                port['x'] = block_x + block_w
            elif edge == 'left':
                # Port stays on left edge, no change needed
                port['x'] = block_x
            elif edge == 'top':
                # Port on top edge - adjust x position proportionally
                if old_width > 0:
                    old_relative_x = (port['x'] - block_x) / old_width
                    port['x'] = block_x + (old_relative_x * new_width)
                # Ensure port stays on top edge
                port['y'] = block_y + block_h
            elif edge == 'bottom':
                # Port on bottom edge - adjust x position proportionally
                if old_width > 0:
                    old_relative_x = (port['x'] - block_x) / old_width
                    port['x'] = block_x + (old_relative_x * new_width)
                # Ensure port stays on bottom edge
                port['y'] = block_y
        
        elif resize_type == 'height':
            if edge == 'top':
                # Port stays on top edge, update y position
                port['y'] = block_y + block_h
            elif edge == 'bottom':
                # Port stays on bottom edge, no change needed
                port['y'] = block_y
            elif edge == 'right':
                # Port on right edge - adjust y position proportionally
                if old_height and old_height > 0:
                    old_relative_y = (port['y'] - block_y) / old_height
                    port['y'] = block_y + (old_relative_y * new_height)
                # Ensure port stays on right edge
                port['x'] = block_x + block_w
            elif edge == 'left':
                # Port on left edge - adjust y position proportionally
                if old_height and old_height > 0:
                    old_relative_y = (port['y'] - block_y) / old_height
                    port['y'] = block_y + (old_relative_y * new_height)
                # Ensure port stays on left edge
                port['x'] = block_x
        
        elif resize_type == 'corner':
            # Handle both width and height changes
            if edge == 'right':
                # Port on right edge - adjust y position proportionally
                if old_height and old_height > 0:
                    old_relative_y = (port['y'] - block_y) / old_height
                    port['y'] = block_y + (old_relative_y * new_height)
                # Ensure port stays on right edge
                port['x'] = block_x + block_w
            elif edge == 'left':
                # Port on left edge - adjust y position proportionally
                if old_height and old_height > 0:
                    old_relative_y = (port['y'] - block_y) / old_height
                    port['y'] = block_y + (old_relative_y * new_height)
                # Ensure port stays on left edge
                port['x'] = block_x
            elif edge == 'top':
                # Port on top edge - adjust x position proportionally
                if old_width > 0:
                    old_relative_x = (port['x'] - block_x) / old_width
                    port['x'] = block_x + (old_relative_x * new_width)
                # Ensure port stays on top edge
                port['y'] = block_y + block_h
            elif edge == 'bottom':
                # Port on bottom edge - adjust x position proportionally
                if old_width > 0:
                    old_relative_x = (port['x'] - block_x) / old_width
                    port['x'] = block_x + (old_relative_x * new_width)
                # Ensure port stays on bottom edge
                port['y'] = block_y
    
    def update_plot(self):
        """Update the floorplan visualization with improved handles"""
        self.ax.clear()
        
        # Auto-resize view to fit all blocks if enabled
        if self.auto_resize_view and self.blocks:
            x_coords = []
            y_coords = []
            
            for block in self.blocks:
                x_coords.extend([block['x'], block['x'] + block['width']])
                y_coords.extend([block['y'], block['y'] + block['height']])
            
            # Add some padding
            padding = 100
            x_min, x_max = min(x_coords) - padding, max(x_coords) + padding
            y_min, y_max = min(y_coords) - padding, max(y_coords) + padding
            
            # Set view limits
            self.ax.set_xlim(x_min, x_max)
            self.ax.set_ylim(y_min, y_max)
        
        if not self.blocks:
            self.ax.text(0.5, 0.5, 'Upload CSV to see floorplan', 
                        ha='center', va='center', transform=self.ax.transAxes)
            self.canvas.draw()
            return
            
        # Draw blocks with improved handles
        for i, block in enumerate(self.blocks):
            # Determine color based on selection
            if block == self.selected_block:
                facecolor = 'lightcoral'
                edgecolor = 'red'
                linewidth = 3
            else:
                facecolor = 'lightblue'
                edgecolor = 'blue'
                linewidth = 2
                
            # Draw main rectangle
            rect = plt.Rectangle((block['x'], block['y']), 
                               block['width'], block['height'],
                               linewidth=linewidth, edgecolor=edgecolor, 
                               facecolor=facecolor, alpha=0.7)
            self.ax.add_patch(rect)
            
            # Draw improved handles for selected block
            if block == self.selected_block and self.interactive_var.get():
                self.draw_improved_handles(block)
            
            # Add label with area info
            calculated_area = int(block['width'] * block['height'])
            area_text = f"{block['name']}\n{int(block['area'])} μm²\n{int(block['width'])}×{int(block['height'])}"
            self.ax.text(block['x'] + block['width']/2, 
                        block['y'] + block['height']/2,
                        area_text,
                        ha='center', va='center', fontsize=8, weight='bold')
                        
        # Draw Manhattan connections with draggable port bubbles
        for i, conn in enumerate(self.connections):
            from_block = self.blocks[conn['from']]
            to_block = self.blocks[conn['to']]
            
            # Initialize port positions if not set
            if 'port_positions' not in conn:
                start_point, end_point = self.find_edge_connection_points(from_block, to_block, i)
                conn['port_positions'] = {
                    'start': {'x': start_point[0], 'y': start_point[1], 'edge': self.get_edge_type(start_point, from_block)},
                    'end': {'x': end_point[0], 'y': end_point[1], 'edge': self.get_edge_type(end_point, to_block)}
                }
            
            start_port = conn['port_positions']['start']
            end_port = conn['port_positions']['end']
            
            # Draw Z-shaped connection (perpendicular to edge, then bend)
            # Calculate perpendicular offset from edge
            offset = 50  # Increased distance to move perpendicular to edge for better separation
            
            # Determine connection direction based on edge types
            start_edge = start_port['edge']
            end_edge = end_port['edge']
            
            # Calculate double Z-path points (Z at source, Z at destination, connected by straight line)
            # First, determine the offset for this specific connection to avoid overlap
            connection_offset = self.get_connection_offset(conn, start_port, end_port, offset)
            
            # Source Z-connector points
            if start_edge in ['left', 'right']:
                # Start port is on left or right edge
                if start_edge == 'left':
                    # First perpendicular line going left from port
                    s1_x = start_port['x'] - connection_offset
                    s1_y = start_port['y']
                    # Second perpendicular line going up/down
                    s2_x = s1_x
                    s2_y = start_port['y'] + (connection_offset if start_port['y'] < end_port['y'] else -connection_offset)
                else:  # right
                    # First perpendicular line going right from port
                    s1_x = start_port['x'] + connection_offset
                    s1_y = start_port['y']
                    # Second perpendicular line going up/down
                    s2_x = s1_x
                    s2_y = start_port['y'] + (connection_offset if start_port['y'] < end_port['y'] else -connection_offset)
            else:  # start_edge is 'top' or 'bottom'
                # Start port is on top or bottom edge
                if start_edge == 'bottom':
                    # First perpendicular line going down from port
                    s1_x = start_port['x']
                    s1_y = start_port['y'] - connection_offset
                    # Second perpendicular line going left/right
                    s2_x = start_port['x'] + (connection_offset if start_port['x'] < end_port['x'] else -connection_offset)
                    s2_y = s1_y
                else:  # top
                    # First perpendicular line going up from port
                    s1_x = start_port['x']
                    s1_y = start_port['y'] + connection_offset
                    # Second perpendicular line going left/right
                    s2_x = start_port['x'] + (connection_offset if start_port['x'] < end_port['x'] else -connection_offset)
                    s2_y = s1_y
            
            # Destination Z-connector points
            if end_edge in ['left', 'right']:
                # End port is on left or right edge
                if end_edge == 'left':
                    # First perpendicular line going left from port
                    d1_x = end_port['x'] - connection_offset
                    d1_y = end_port['y']
                    # Second perpendicular line going up/down
                    d2_x = d1_x
                    d2_y = end_port['y'] + (connection_offset if end_port['y'] < start_port['y'] else -connection_offset)
                else:  # right
                    # First perpendicular line going right from port
                    d1_x = end_port['x'] + connection_offset
                    d1_y = end_port['y']
                    # Second perpendicular line going up/down
                    d2_x = d1_x
                    d2_y = end_port['y'] + (connection_offset if end_port['y'] < start_port['y'] else -connection_offset)
            else:  # end_edge is 'top' or 'bottom'
                # End port is on top or bottom edge
                if end_edge == 'bottom':
                    # First perpendicular line going down from port
                    d1_x = end_port['x']
                    d1_y = end_port['y'] - connection_offset
                    # Second perpendicular line going left/right
                    d2_x = end_port['x'] + (connection_offset if end_port['x'] < start_port['x'] else -connection_offset)
                    d2_y = d1_y
                else:  # top
                    # First perpendicular line going up from port
                    d1_x = end_port['x']
                    d1_y = end_port['y'] + connection_offset
                    # Second perpendicular line going left/right
                    d2_x = end_port['x'] + (connection_offset if end_port['x'] < start_port['x'] else -connection_offset)
                    d2_y = d1_y
            
            # Draw double Z-shaped connection
            # Source Z: from port to first perpendicular point
            self.ax.plot([start_port['x'], s1_x], [start_port['y'], s1_y], 'r--', linewidth=1, alpha=0.7)
            # Source Z: from first to second perpendicular point
            self.ax.plot([s1_x, s2_x], [s1_y, s2_y], 'r--', linewidth=1, alpha=0.7)
            
            # Middle connection between the two Z's (straight or Manhattan)
            if self.connection_mode_var.get() == "straight":
                # Straight line connecting the two Z's
                self.ax.plot([s2_x, d2_x], [s2_y, d2_y], 'r--', linewidth=1, alpha=0.7)
            else:  # manhattan
                # Manhattan connection between the two Z's
                # First go horizontal, then vertical
                mid_x = s2_x
                mid_y = d2_y
                self.ax.plot([s2_x, mid_x], [s2_y, mid_y], 'r--', linewidth=1, alpha=0.7)
                self.ax.plot([mid_x, d2_x], [mid_y, d2_y], 'r--', linewidth=1, alpha=0.7)
            
            # Destination Z: from second perpendicular point to first perpendicular point
            self.ax.plot([d2_x, d1_x], [d2_y, d1_y], 'r--', linewidth=1, alpha=0.7)
            # Destination Z: from first perpendicular point to end port
            self.ax.plot([d1_x, end_port['x']], [d1_y, end_port['y']], 'r--', linewidth=1, alpha=0.7)
            
            # Draw port bubbles (bigger for easier selection)
            start_bubble = plt.Circle((start_port['x'], start_port['y']), self.PORT_RADIUS, 
                                    facecolor='blue', edgecolor='black', linewidth=1, alpha=0.8)
            end_bubble = plt.Circle((end_port['x'], end_port['y']), self.PORT_RADIUS, 
                                  facecolor='red', edgecolor='black', linewidth=1, alpha=0.8)
            self.ax.add_patch(start_bubble)
            self.ax.add_patch(end_bubble)
            
            # Calculate the middle point of the entire connection path
            # Total path length = source Z + middle connection + destination Z
            source_z_length = abs(s1_x - start_port['x']) + abs(s1_y - start_port['y']) + abs(s2_x - s1_x) + abs(s2_y - s1_y)
            
            if self.connection_mode_var.get() == "straight":
                middle_line_length = abs(d2_x - s2_x) + abs(d2_y - s2_y)
            else:  # manhattan
                # Manhattan middle connection has two segments
                mid_x = s2_x
                mid_y = d2_y
                middle_line_length = abs(mid_x - s2_x) + abs(mid_y - s2_y) + abs(d2_x - mid_x) + abs(d2_y - mid_y)
            
            dest_z_length = abs(d1_x - d2_x) + abs(d1_y - d2_y) + abs(end_port['x'] - d1_x) + abs(end_port['y'] - d1_y)
            total_length = source_z_length + middle_line_length + dest_z_length
            
            # Find the middle point along the path
            target_length = total_length / 2
            current_length = 0
            
            # Check each segment to find where the middle point falls
            if current_length + source_z_length >= target_length:
                # Middle point is in source Z
                ratio = (target_length - current_length) / source_z_length
                if ratio < 0.5:
                    # In first segment of source Z
                    seg_ratio = ratio * 2
                    mid_x = start_port['x'] + seg_ratio * (s1_x - start_port['x'])
                    mid_y = start_port['y'] + seg_ratio * (s1_y - start_port['y'])
                else:
                    # In second segment of source Z
                    seg_ratio = (ratio - 0.5) * 2
                    mid_x = s1_x + seg_ratio * (s2_x - s1_x)
                    mid_y = s1_y + seg_ratio * (s2_y - s1_y)
            else:
                current_length += source_z_length
                if current_length + middle_line_length >= target_length:
                    # Middle point is in middle connection
                    ratio = (target_length - current_length) / middle_line_length
                    if self.connection_mode_var.get() == "straight":
                        # Straight line
                        mid_x = s2_x + ratio * (d2_x - s2_x)
                        mid_y = s2_y + ratio * (d2_y - s2_y)
                    else:  # manhattan
                        # Manhattan connection - check which segment
                        manhattan_mid_x = s2_x
                        manhattan_mid_y = d2_y
                        first_segment_length = abs(manhattan_mid_x - s2_x) + abs(manhattan_mid_y - s2_y)
                        if ratio * middle_line_length <= first_segment_length:
                            # In first segment (horizontal)
                            seg_ratio = (ratio * middle_line_length) / first_segment_length
                            mid_x = s2_x + seg_ratio * (manhattan_mid_x - s2_x)
                            mid_y = s2_y + seg_ratio * (manhattan_mid_y - s2_y)
                        else:
                            # In second segment (vertical)
                            seg_ratio = (ratio * middle_line_length - first_segment_length) / (abs(d2_x - manhattan_mid_x) + abs(d2_y - manhattan_mid_y))
                            mid_x = manhattan_mid_x + seg_ratio * (d2_x - manhattan_mid_x)
                            mid_y = manhattan_mid_y + seg_ratio * (d2_y - manhattan_mid_y)
                else:
                    # Middle point is in destination Z
                    current_length += middle_line_length
                    ratio = (target_length - current_length) / dest_z_length
                    if ratio < 0.5:
                        # In first segment of dest Z
                        seg_ratio = ratio * 2
                        mid_x = d2_x + seg_ratio * (d1_x - d2_x)
                        mid_y = d2_y + seg_ratio * (d1_y - d2_y)
                    else:
                        # In second segment of dest Z
                        seg_ratio = (ratio - 0.5) * 2
                        mid_x = d1_x + seg_ratio * (end_port['x'] - d1_x)
                        mid_y = d1_y + seg_ratio * (end_port['y'] - d1_y)
            
            # Add connection count at the middle of the entire connection path
            self.ax.text(mid_x, mid_y, str(conn['connections']), 
                        ha='center', va='center', fontsize=8,
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
                        
        self.ax.set_xlabel('X Position (μm)')
        self.ax.set_ylabel('Y Position (μm)')
        self.ax.set_title('Interactive Floorplan Visualization - Version 3.0')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_aspect('equal')
        
        # Disable auto-resize during interaction
        if self.dragging or self.port_dragging:
            self.auto_resize_view = False
        
        self.canvas.draw()
    

        
    def draw_improved_handles(self, block):
        """Draw improved resize handles with better visibility"""
        corner_size = self.handle_config['corner_size']
        edge_width = self.handle_config['edge_width']
        edge_height = self.handle_config['edge_height']
        colors = self.handle_config['colors']
        
        # Corner handles (all four corners)
        corners = [
            (block['x'] + block['width'] - corner_size, block['y'] + block['height'] - corner_size),  # Top-right
            (block['x'] + block['width'] - corner_size, block['y']),                                  # Bottom-right
            (block['x'], block['y'] + block['height'] - corner_size),                                 # Top-left
            (block['x'], block['y'])                                                                   # Bottom-left
        ]
        
        for i, (cx, cy) in enumerate(corners):
            # Determine color based on hover state
            handle_id = f'corner_{i}'
            if self.hover_handle == handle_id:
                color = colors['hover']
            else:
                color = colors['corner']
                
            handle = plt.Rectangle((cx, cy), corner_size, corner_size,
                                 linewidth=2, edgecolor='black',
                                 facecolor=color, alpha=0.9)
            self.ax.add_patch(handle)
        
        # Edge handles (right and bottom edges)
        edge_handles = [
            # Right edge
            (block['x'] + block['width'] - edge_width, block['y'] + (block['height'] - edge_height)/2, edge_width, edge_height),
            # Bottom edge
            (block['x'] + (block['width'] - edge_width)/2, block['y'] + block['height'] - edge_height, edge_width, edge_height)
        ]
        
        edge_ids = ['edge_right', 'edge_bottom']
        
        for i, (ex, ey, ew, eh) in enumerate(edge_handles):
            # Determine color based on hover state
            handle_id = edge_ids[i]
            if self.hover_handle == handle_id:
                color = colors['hover']
            else:
                color = colors['edge']
                
            handle = plt.Rectangle((ex, ey), ew, eh,
                                 linewidth=2, edgecolor='black',
                                 facecolor=color, alpha=0.9)
            self.ax.add_patch(handle)
        
    def update_properties(self):
        """Update properties tab"""
        # Clear existing widgets
        for widget in self.properties_container.winfo_children():
            widget.destroy()
            
        if not self.blocks:
            ttk.Label(self.properties_container, text="No blocks loaded").pack(pady=20)
            return
            
        # Create property editors for each block
        for i, block in enumerate(self.blocks):
            frame = ttk.LabelFrame(self.properties_container, text=f"Block {i+1}: {block['name']}")
            frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Area
            ttk.Label(frame, text="Area (μm²):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
            area_var = tk.StringVar(value=str(int(block['area'])))
            area_entry = ttk.Entry(frame, textvariable=area_var, width=15)
            area_entry.grid(row=0, column=1, padx=5, pady=2)
            
            # Width
            ttk.Label(frame, text="Width (μm):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
            width_var = tk.StringVar(value=str(int(block['width'])))
            width_entry = ttk.Entry(frame, textvariable=width_var, width=15)
            width_entry.grid(row=1, column=1, padx=5, pady=2)
            
            # Height
            ttk.Label(frame, text="Height (μm):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
            height_var = tk.StringVar(value=str(int(block['height'])))
            height_entry = ttk.Entry(frame, textvariable=height_var, width=15)
            height_entry.grid(row=2, column=1, padx=5, pady=2)
            
            # Position
            ttk.Label(frame, text="X Position:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
            x_var = tk.StringVar(value=str(int(block['x'])))
            x_entry = ttk.Entry(frame, textvariable=x_var, width=15)
            x_entry.grid(row=3, column=1, padx=5, pady=2)
            
            ttk.Label(frame, text="Y Position:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
            y_var = tk.StringVar(value=str(int(block['y'])))
            y_entry = ttk.Entry(frame, textvariable=y_var, width=15)
            y_entry.grid(row=4, column=1, padx=5, pady=2)
            
            # Update button
            def update_block(block_id=block['id'], area_var=area_var, width_var=width_var, 
                           height_var=height_var, x_var=x_var, y_var=y_var):
                try:
                    block['area'] = float(area_var.get())
                    block['width'] = float(width_var.get())
                    block['height'] = float(height_var.get())
                    block['x'] = float(x_var.get())
                    block['y'] = float(y_var.get())
                    self.update_plot()
                except ValueError:
                    messagebox.showerror("Error", "Please enter valid numbers")
                    
            ttk.Button(frame, text="Update", command=update_block).grid(row=5, column=0, columnspan=2, pady=5)
            
    def update_connections(self):
        """Update connections tab"""
        # Clear existing widgets
        for widget in self.connections_container.winfo_children():
            widget.destroy()
            
        if not self.connections:
            ttk.Label(self.connections_container, text="No connections loaded").pack(pady=20)
            return
            
        # Create connection list
        for i, conn in enumerate(self.connections):
            frame = ttk.Frame(self.connections_container)
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(frame, text=f"{conn['from_name']} ↔ {conn['to_name']}", 
                     font=('Arial', 10, 'bold')).pack(anchor=tk.W)
            ttk.Label(frame, text=f"Connections: {conn['connections']}", 
                     font=('Arial', 9)).pack(anchor=tk.W)
            
            ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, pady=2)
    
    def zoom_in(self):
        """Zoom in on the current view"""
        if self.blocks:
            # Disable auto-resize during zoom
            self.auto_resize_view = False
            
            # Get current view limits
            x_min, x_max = self.ax.get_xlim()
            y_min, y_max = self.ax.get_ylim()
            
            # Calculate center
            x_center = (x_min + x_max) / 2
            y_center = (y_min + y_max) / 2
            
            # Calculate new limits (zoom in by 20%)
            x_range = (x_max - x_min) * 0.8
            y_range = (y_max - y_min) * 0.8
            
            # Set new limits
            self.ax.set_xlim(x_center - x_range/2, x_center + x_range/2)
            self.ax.set_ylim(y_center - y_range/2, y_center + y_range/2)
            
            self.canvas.draw()
    
    def zoom_out(self):
        """Zoom out from the current view"""
        if self.blocks:
            # Disable auto-resize during zoom
            self.auto_resize_view = False
            
            # Get current view limits
            x_min, x_max = self.ax.get_xlim()
            y_min, y_max = self.ax.get_ylim()
            
            # Calculate center
            x_center = (x_min + x_max) / 2
            y_center = (y_min + y_max) / 2
            
            # Calculate new limits (zoom out by 20%)
            x_range = (x_max - x_min) * 1.2
            y_range = (y_max - y_min) * 1.2
            
            # Set new limits
            self.ax.set_xlim(x_center - x_range/2, x_center + x_range/2)
            self.ax.set_ylim(y_center - y_range/2, y_center + y_range/2)
            
            self.canvas.draw()
    
    def fit_to_screen(self):
        """Fit all blocks to the current view"""
        if self.blocks:
            # Disable auto-resize during fit
            self.auto_resize_view = False
            
            # Calculate bounds of all blocks
            x_coords = []
            y_coords = []
            
            for block in self.blocks:
                x_coords.extend([block['x'], block['x'] + block['width']])
                y_coords.extend([block['y'], block['y'] + block['height']])
            
            # Add some padding
            padding = 50
            x_min, x_max = min(x_coords) - padding, max(x_coords) + padding
            y_min, y_max = min(y_coords) - padding, max(y_coords) + padding
            
            # Set view limits
            self.ax.set_xlim(x_min, x_max)
            self.ax.set_ylim(y_min, y_max)
            
            self.canvas.draw()

def main():
    root = tk.Tk()
    app = FloorplanToolV2(root)
    root.mainloop()

if __name__ == "__main__":
    main()
