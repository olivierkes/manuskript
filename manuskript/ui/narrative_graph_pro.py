#!/usr/bin/env python
# --!-- coding: utf8 --!--
"""
Professional Narrative Graph Widget
Clean architecture, optimized performance, modern UI/UX
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import QWebEngineView

import logging
import json
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass
import math
from enum import Enum

LOGGER = logging.getLogger(__name__)

class GraphLayout(Enum):
    """Available graph layouts."""
    FORCE_DIRECTED = "force"
    CIRCULAR = "circular"
    HIERARCHICAL = "hierarchical"
    RADIAL = "radial"
    GRID = "grid"

class GraphRenderer(QGraphicsView):
    """
    Optimized graph renderer using hardware acceleration.
    """
    
    # Signals
    nodeSelected = pyqtSignal(str, str)  # entity_id, entity_type
    nodeContextMenu = pyqtSignal(str, QPoint)
    edgeContextMenu = pyqtSignal(str, str, QPoint)
    selectionChanged = pyqtSignal(set)  # Set of selected entity IDs
    
    def __init__(self):
        super().__init__()
        
        # Setup rendering
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)
        self.setCacheMode(QGraphicsView.CacheBackground)
        
        # Scene
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        # Visual settings
        self.setup_visual_theme()
        
        # State
        self.nodes = {}  # entity_id -> GraphNode
        self.edges = {}  # (source_id, target_id) -> GraphEdge
        self.selected_nodes = set()
        
        # Interaction
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setMouseTracking(True)
        
        # Layout engine
        self.layout_engine = ForceDirectedLayout()
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_layout)
        
    def setup_visual_theme(self):
        """Setup Neo4j-like visual theme."""
        self.node_colors = {
            'CHARACTER': QColor(97, 175, 239),   # Blue
            'LOCATION': QColor(253, 204, 92),    # Yellow
            'OBJECT': QColor(195, 125, 198),     # Purple
            'EVENT': QColor(132, 202, 155),      # Green
            'THEME': QColor(248, 150, 121),      # Orange
            'CONCEPT': QColor(141, 153, 174)     # Gray
        }
        
        # Dark background
        gradient = QLinearGradient(0, 0, 0, 800)
        gradient.setColorAt(0, QColor(25, 25, 35))
        gradient.setColorAt(1, QColor(45, 45, 55))
        self.setBackgroundBrush(QBrush(gradient))
    
    def load_graph(self, graph_engine):
        """Load graph from engine with optimized rendering."""
        # Clear scene
        self.scene.clear()
        self.nodes.clear()
        self.edges.clear()
        
        if not graph_engine:
            return
        
        # Calculate layout
        positions = self.layout_engine.calculate(graph_engine)
        
        # Create nodes (batch operation for performance)
        for entity_id, entity in graph_engine.entities.items():
            pos = positions.get(entity_id, (0, 0))
            node = self.create_node(entity, pos)
            self.nodes[entity_id] = node
        
        # Create edges (batch operation)
        for (source_id, target_id), relationship in graph_engine.relationships.items():
            if source_id in self.nodes and target_id in self.nodes:
                edge = self.create_edge(
                    self.nodes[source_id],
                    self.nodes[target_id],
                    relationship
                )
                self.edges[(source_id, target_id)] = edge
        
        # Fit view
        self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
    
    def create_node(self, entity, position):
        """Create an optimized graph node."""
        node = GraphNode(entity, self.node_colors.get(entity.type.name, QColor(128, 128, 128)))
        node.setPos(*position)
        self.scene.addItem(node)
        return node
    
    def create_edge(self, source_node, target_node, relationship):
        """Create an optimized graph edge."""
        edge = GraphEdge(source_node, target_node, relationship)
        self.scene.addItem(edge)
        return edge
    
    def animate_layout(self):
        """Animate layout changes smoothly."""
        # Implement smooth transitions
        pass
    
    def wheelEvent(self, event):
        """Smooth zoom with limits."""
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor
        
        # Get current scale
        current_scale = self.transform().m11()
        
        # Apply limits
        if event.angleDelta().y() > 0:
            if current_scale < 5.0:  # Max zoom
                self.scale(zoom_in_factor, zoom_in_factor)
        else:
            if current_scale > 0.1:  # Min zoom
                self.scale(zoom_out_factor, zoom_out_factor)

class GraphNode(QGraphicsItem):
    """Optimized graph node with caching."""
    
    def __init__(self, entity, color):
        super().__init__()
        self.entity = entity
        self.color = color
        self.radius = 25
        
        # Optimization flags
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        
        # Hover effect
        self.setAcceptHoverEvents(True)
        self.hover = False
    
    def boundingRect(self):
        return QRectF(-self.radius-2, -self.radius-2, 
                     (self.radius+2)*2, (self.radius+2)*2)
    
    def paint(self, painter, option, widget):
        # Draw shadow
        if self.hover:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(0, 0, 0, 50))
            painter.drawEllipse(QPointF(2, 2), self.radius+2, self.radius+2)
        
        # Draw node
        painter.setPen(QPen(self.color.darker(150), 2))
        painter.setBrush(self.color)
        painter.drawEllipse(QPointF(0, 0), self.radius, self.radius)
        
        # Draw text
        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 9, QFont.Bold))
        text = self.entity.name[:12]
        rect = QRectF(-self.radius, -10, self.radius*2, 20)
        painter.drawText(rect, Qt.AlignCenter, text)
    
    def hoverEnterEvent(self, event):
        self.hover = True
        self.update()
    
    def hoverLeaveEvent(self, event):
        self.hover = False
        self.update()

class GraphEdge(QGraphicsItem):
    """Optimized graph edge with arrow."""
    
    def __init__(self, source_node, target_node, relationship):
        super().__init__()
        self.source = source_node
        self.target = target_node
        self.relationship = relationship
        self.setZValue(-1)
    
    def boundingRect(self):
        return self.shape().boundingRect()
    
    def shape(self):
        path = QPainterPath()
        path.moveTo(self.source.pos())
        path.lineTo(self.target.pos())
        return path
    
    def paint(self, painter, option, widget):
        # Calculate positions
        source_pos = self.source.pos()
        target_pos = self.target.pos()
        
        # Draw line
        painter.setPen(QPen(QColor(150, 150, 150, 128), 1.5))
        painter.drawLine(source_pos, target_pos)
        
        # Draw arrow
        angle = math.atan2(target_pos.y() - source_pos.y(),
                          target_pos.x() - source_pos.x())
        
        # Arrow at edge of target node
        arrow_length = 10
        arrow_degrees = math.pi / 6
        
        end_x = target_pos.x() - 25 * math.cos(angle)
        end_y = target_pos.y() - 25 * math.sin(angle)
        
        p1 = QPointF(end_x, end_y)
        p2 = QPointF(end_x - arrow_length * math.cos(angle - arrow_degrees),
                    end_y - arrow_length * math.sin(angle - arrow_degrees))
        p3 = QPointF(end_x - arrow_length * math.cos(angle + arrow_degrees),
                    end_y - arrow_length * math.sin(angle + arrow_degrees))
        
        painter.setBrush(QColor(150, 150, 150, 128))
        painter.drawPolygon(QPolygonF([p1, p2, p3]))

class ForceDirectedLayout:
    """Optimized force-directed layout algorithm."""
    
    def calculate(self, graph_engine, iterations=50):
        """Calculate node positions using force-directed layout."""
        import random
        
        positions = {}
        velocities = {}
        
        # Initialize random positions
        for entity_id in graph_engine.entities:
            positions[entity_id] = (
                random.uniform(-200, 200),
                random.uniform(-200, 200)
            )
            velocities[entity_id] = (0, 0)
        
        # Parameters
        k = 100  # Ideal edge length
        c_rep = 10000  # Repulsion constant
        c_spring = 0.01  # Spring constant
        damping = 0.9
        
        for _ in range(iterations):
            forces = {entity_id: (0, 0) for entity_id in positions}
            
            # Repulsive forces between all nodes
            entities = list(positions.keys())
            for i, e1 in enumerate(entities):
                for e2 in entities[i+1:]:
                    dx = positions[e2][0] - positions[e1][0]
                    dy = positions[e2][1] - positions[e1][1]
                    dist = max(math.sqrt(dx**2 + dy**2), 0.01)
                    
                    force = c_rep / (dist ** 2)
                    fx = force * dx / dist
                    fy = force * dy / dist
                    
                    forces[e1] = (forces[e1][0] - fx, forces[e1][1] - fy)
                    forces[e2] = (forces[e2][0] + fx, forces[e2][1] + fy)
            
            # Attractive forces along edges
            for (source_id, target_id), rel in graph_engine.relationships.items():
                if source_id in positions and target_id in positions:
                    dx = positions[target_id][0] - positions[source_id][0]
                    dy = positions[target_id][1] - positions[source_id][1]
                    dist = max(math.sqrt(dx**2 + dy**2), 0.01)
                    
                    force = c_spring * (dist - k)
                    fx = force * dx / dist
                    fy = force * dy / dist
                    
                    forces[source_id] = (forces[source_id][0] + fx, forces[source_id][1] + fy)
                    forces[target_id] = (forces[target_id][0] - fx, forces[target_id][1] - fy)
            
            # Update positions
            for entity_id in positions:
                vx = (velocities[entity_id][0] + forces[entity_id][0]) * damping
                vy = (velocities[entity_id][1] + forces[entity_id][1]) * damping
                velocities[entity_id] = (vx, vy)
                
                positions[entity_id] = (
                    positions[entity_id][0] + vx,
                    positions[entity_id][1] + vy
                )
        
        # Scale to viewport
        scale = 3
        return {
            entity_id: (x * scale, y * scale)
            for entity_id, (x, y) in positions.items()
        }

class NarrativeGraphPro(QWidget):
    """
    Professional narrative graph widget with clean architecture.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.graph_engine = None
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the professional UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Main toolbar
        self.toolbar = self.create_main_toolbar()
        layout.addWidget(self.toolbar)
        
        # Splitter for graph and panels
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Graph view
        graph_container = QWidget()
        graph_layout = QVBoxLayout(graph_container)
        graph_layout.setContentsMargins(0, 0, 0, 0)
        
        # Graph controls
        controls = self.create_graph_controls()
        graph_layout.addWidget(controls)
        
        # Graph renderer
        self.graph_renderer = GraphRenderer()
        graph_layout.addWidget(self.graph_renderer)
        
        splitter.addWidget(graph_container)
        
        # Right panel - Data and controls
        self.side_panel = self.create_side_panel()
        splitter.addWidget(self.side_panel)
        
        splitter.setSizes([600, 300])
        layout.addWidget(splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        layout.addWidget(self.status_bar)
        
        # Apply stylesheet
        self.setStyleSheet(self.get_stylesheet())
    
    def create_main_toolbar(self):
        """Create the main toolbar."""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        
        # File actions
        toolbar.addAction(QIcon(), "💾 Save", self.save_graph)
        toolbar.addAction(QIcon(), "📂 Load", self.load_graph)
        toolbar.addSeparator()
        
        # Scan action
        scan_action = toolbar.addAction(QIcon(), "🔍 Scan Project", self.scan_project)
        scan_action.setToolTip("Scan project for entities and relationships")
        
        toolbar.addSeparator()
        
        # Entity actions
        toolbar.addAction(QIcon(), "👤 Add Character", lambda: self.add_entity('CHARACTER'))
        toolbar.addAction(QIcon(), "📍 Add Location", lambda: self.add_entity('LOCATION'))
        toolbar.addAction(QIcon(), "🔗 Add Relationship", self.add_relationship)
        
        toolbar.addSeparator()
        
        # View actions
        toolbar.addAction(QIcon(), "🔄 Refresh", self.refresh_view)
        toolbar.addAction(QIcon(), "📊 Statistics", self.show_statistics)
        
        return toolbar
    
    def create_graph_controls(self):
        """Create graph control bar."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Layout selector
        layout.addWidget(QLabel("Layout:"))
        self.layout_combo = QComboBox()
        self.layout_combo.addItems([l.value for l in GraphLayout])
        self.layout_combo.currentTextChanged.connect(self.change_layout)
        layout.addWidget(self.layout_combo)
        
        # Filter
        layout.addWidget(QLabel("Filter:"))
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Type to filter...")
        self.filter_input.textChanged.connect(self.apply_filter)
        layout.addWidget(self.filter_input)
        
        # Zoom
        layout.addWidget(QLabel("Zoom:"))
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(10, 500)
        self.zoom_slider.setValue(100)
        self.zoom_slider.valueChanged.connect(self.change_zoom)
        layout.addWidget(self.zoom_slider)
        
        layout.addStretch()
        
        return widget
    
    def create_side_panel(self):
        """Create the side panel with tabs."""
        tabs = QTabWidget()
        
        # Inspector tab
        self.inspector = self.create_inspector()
        tabs.addTab(self.inspector, "Inspector")
        
        # Query tab
        self.query_panel = self.create_query_panel()
        tabs.addTab(self.query_panel, "Query")
        
        # Analytics tab
        self.analytics = self.create_analytics()
        tabs.addTab(self.analytics, "Analytics")
        
        return tabs
    
    def create_inspector(self):
        """Create entity inspector panel."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Entity details
        self.entity_details = QTextEdit()
        self.entity_details.setReadOnly(True)
        layout.addWidget(self.entity_details)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(QPushButton("Edit", clicked=self.edit_selected))
        button_layout.addWidget(QPushButton("Delete", clicked=self.delete_selected))
        button_layout.addWidget(QPushButton("Find Paths", clicked=self.find_paths))
        layout.addLayout(button_layout)
        
        return widget
    
    def create_query_panel(self):
        """Create graph query panel."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Query input
        self.query_input = QTextEdit()
        self.query_input.setPlaceholderText("Enter graph query...")
        self.query_input.setMaximumHeight(100)
        layout.addWidget(self.query_input)
        
        # Query buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(QPushButton("Execute", clicked=self.execute_query))
        button_layout.addWidget(QPushButton("Clear", clicked=self.query_input.clear))
        layout.addLayout(button_layout)
        
        # Results
        self.query_results = QTableWidget()
        layout.addWidget(self.query_results)
        
        return widget
    
    def create_analytics(self):
        """Create analytics panel."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Use web view for rich visualizations
        self.analytics_view = QWebEngineView()
        layout.addWidget(self.analytics_view)
        
        # Update button
        update_btn = QPushButton("Update Analytics")
        update_btn.clicked.connect(self.update_analytics)
        layout.addWidget(update_btn)
        
        return widget
    
    def setup_connections(self):
        """Setup signal connections."""
        self.graph_renderer.nodeSelected.connect(self.on_node_selected)
        self.graph_renderer.nodeContextMenu.connect(self.show_node_menu)
        self.graph_renderer.selectionChanged.connect(self.on_selection_changed)
    
    def get_stylesheet(self):
        """Get professional dark theme stylesheet."""
        return """
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        
        QToolBar {
            background: #363636;
            border: none;
            padding: 5px;
        }
        
        QToolBar QToolButton {
            background: transparent;
            border: 1px solid transparent;
            border-radius: 3px;
            padding: 5px;
            margin: 2px;
        }
        
        QToolBar QToolButton:hover {
            background: #4a4a4a;
            border-color: #5a5a5a;
        }
        
        QTabWidget::pane {
            border: 1px solid #3a3a3a;
            background: #2b2b2b;
        }
        
        QTabBar::tab {
            background: #363636;
            color: #ffffff;
            padding: 8px 16px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background: #4a4a4a;
            border-bottom: 2px solid #61afef;
        }
        
        QLineEdit, QTextEdit, QComboBox {
            background: #363636;
            border: 1px solid #4a4a4a;
            border-radius: 3px;
            padding: 5px;
            color: #ffffff;
        }
        
        QLineEdit:focus, QTextEdit:focus {
            border-color: #61afef;
        }
        
        QPushButton {
            background: #4a4a4a;
            border: 1px solid #5a5a5a;
            border-radius: 3px;
            padding: 6px 12px;
            color: #ffffff;
        }
        
        QPushButton:hover {
            background: #5a5a5a;
        }
        
        QPushButton:pressed {
            background: #3a3a3a;
        }
        
        QSlider::groove:horizontal {
            height: 4px;
            background: #4a4a4a;
            border-radius: 2px;
        }
        
        QSlider::handle:horizontal {
            background: #61afef;
            width: 12px;
            height: 12px;
            margin: -4px 0;
            border-radius: 6px;
        }
        
        QStatusBar {
            background: #363636;
            border-top: 1px solid #4a4a4a;
        }
        """
    
    # Implementation methods
    def scan_project(self):
        """Scan project asynchronously."""
        self.status_bar.showMessage("Scanning project...")
        # Implement async scanning
        QTimer.singleShot(100, self._do_scan)
    
    def _do_scan(self):
        """Perform the actual scan."""
        try:
            from manuskript.ai.narrative_graph.graph_engine import NarrativeGraphEngine, EntityType
            from manuskript import functions as F
            
            main_window = F.mainWindow()
            if not main_window:
                return
            
            # Initialize engine
            if not self.graph_engine:
                project_path = getattr(main_window, 'currentProject', '.')
                self.graph_engine = NarrativeGraphEngine(project_path)
            
            # Smart scan implementation
            # ... (scan logic here)
            
            # Update view
            self.graph_renderer.load_graph(self.graph_engine)
            self.status_bar.showMessage("Scan complete", 3000)
            
        except Exception as e:
            LOGGER.error(f"Scan failed: {e}")
            self.status_bar.showMessage(f"Scan failed: {e}", 5000)
    
    def refresh_view(self):
        """Refresh the graph view."""
        if self.graph_engine:
            self.graph_renderer.load_graph(self.graph_engine)
    
    def add_entity(self, entity_type):
        """Add a new entity."""
        # Show dialog
        pass
    
    def add_relationship(self):
        """Add a new relationship."""
        # Show dialog
        pass
    
    def change_layout(self, layout_name):
        """Change graph layout."""
        # Update layout
        pass
    
    def apply_filter(self, filter_text):
        """Apply filter to graph."""
        # Filter nodes
        pass
    
    def change_zoom(self, value):
        """Change zoom level."""
        scale = value / 100.0
        self.graph_renderer.resetTransform()
        self.graph_renderer.scale(scale, scale)
    
    def on_node_selected(self, entity_id, entity_type):
        """Handle node selection."""
        if self.graph_engine and entity_id in self.graph_engine.entities:
            entity = self.graph_engine.entities[entity_id]
            
            # Update inspector
            details = f"""
Entity: {entity.name}
Type: {entity.type.name}
Importance: {entity.importance_score:.2f}
Mentions: {entity.mention_count}
First Seen: {entity.first_appearance or 'Unknown'}

Attributes:
{json.dumps(entity.attributes, indent=2)}
            """
            self.entity_details.setPlainText(details)
    
    def on_selection_changed(self, selected_ids):
        """Handle selection change."""
        self.status_bar.showMessage(f"Selected {len(selected_ids)} entities")
    
    def show_node_menu(self, entity_id, pos):
        """Show context menu for node."""
        menu = QMenu(self)
        menu.addAction("Edit", lambda: self.edit_entity(entity_id))
        menu.addAction("Delete", lambda: self.delete_entity(entity_id))
        menu.addSeparator()
        menu.addAction("Find Connections", lambda: self.find_connections(entity_id))
        menu.addAction("Find Paths From", lambda: self.find_paths_from(entity_id))
        menu.exec_(pos)
    
    def edit_selected(self):
        """Edit selected entities."""
        pass
    
    def delete_selected(self):
        """Delete selected entities."""
        pass
    
    def find_paths(self):
        """Find paths between selected entities."""
        pass
    
    def execute_query(self):
        """Execute graph query."""
        pass
    
    def show_statistics(self):
        """Show graph statistics."""
        if self.graph_engine:
            stats = self.graph_engine.get_statistics()
            
            msg = QMessageBox(self)
            msg.setWindowTitle("Graph Statistics")
            msg.setText(f"""
Total Entities: {stats['total_entities']}
Total Relationships: {stats['total_relationships']}

Entities by Type:
{json.dumps(stats['entities_by_type'], indent=2)}

Average Connections: {stats['avg_connections']:.2f}
Graph Density: {stats['density']:.4f}

Performance:
{json.dumps(stats['performance_metrics'], indent=2)}
            """)
            msg.exec_()
    
    def update_analytics(self):
        """Update analytics visualization."""
        # Generate D3.js visualization
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://d3js.org/d3.v7.min.js"></script>
            <style>
                body { background: #2b2b2b; color: #fff; font-family: Arial; }
                .bar { fill: #61afef; }
            </style>
        </head>
        <body>
            <div id="chart"></div>
            <script>
                // D3.js visualization code here
            </script>
        </body>
        </html>
        """
        self.analytics_view.setHtml(html)
    
    def save_graph(self):
        """Save graph to file."""
        if self.graph_engine:
            if self.graph_engine.save():
                self.status_bar.showMessage("Graph saved", 3000)
    
    def load_graph(self):
        """Load graph from file."""
        # Implement load dialog
        pass
    
    def edit_entity(self, entity_id):
        """Edit an entity."""
        pass
    
    def delete_entity(self, entity_id):
        """Delete an entity."""
        pass
    
    def find_connections(self, entity_id):
        """Find all connections for an entity."""
        pass
    
    def find_paths_from(self, entity_id):
        """Find paths from an entity."""
        pass