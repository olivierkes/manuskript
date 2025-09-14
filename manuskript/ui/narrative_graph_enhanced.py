#!/usr/bin/env python
# --!-- coding: utf8 --!--
"""
Enhanced Narrative Graph Widget with Neo4j-like interface

Features:
- Interactive graph visualization
- Right-click context menus
- Editable entities and relationships
- Add/remove functionality
- Clean, organized graph layout
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
                            QTableWidget, QTableWidgetItem, QTextEdit, QLabel, 
                            QPushButton, QSplitter, QTreeWidget, QTreeWidgetItem,
                            QProgressBar, QGroupBox, QScrollArea, QFrame, 
                            QHeaderView, QAbstractItemView, QMessageBox, QDockWidget,
                            QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,
                            QGraphicsTextItem, QGraphicsLineItem, QMenu, QAction,
                            QInputDialog, QDialog, QDialogButtonBox, QFormLayout,
                            QLineEdit, QComboBox, QToolBar, QSlider)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot, QSize, QRectF, QPointF, QLineF
from PyQt5.QtGui import (QFont, QColor, QPalette, QIcon, QPen, QBrush, QWheelEvent, 
                        QTransform, QPainter, QPolygonF, QCursor, QPixmap, QPainterPath)

from manuskript import settings
import logging
from typing import Dict, List, Optional, Any, Tuple
import math
import random
import json

LOGGER = logging.getLogger(__name__)

class EntityEditDialog(QDialog):
    """Dialog for editing entity properties."""
    
    def __init__(self, entity_type, entity_data=None, parent=None):
        super().__init__(parent)
        self.entity_type = entity_type
        self.entity_data = entity_data or {}
        self.setupUI()
        
    def setupUI(self):
        self.setWindowTitle(f"Edit {self.entity_type.title()}")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # Name field
        self.name_edit = QLineEdit(self.entity_data.get('name', ''))
        form_layout.addRow("Name:", self.name_edit)
        
        if self.entity_type == 'character':
            # Character-specific fields
            self.role_edit = QLineEdit(self.entity_data.get('role', ''))
            form_layout.addRow("Role:", self.role_edit)
            
            self.motivation_edit = QTextEdit()
            self.motivation_edit.setPlainText(self.entity_data.get('motivation', ''))
            self.motivation_edit.setMaximumHeight(100)
            form_layout.addRow("Motivation:", self.motivation_edit)
            
        elif self.entity_type == 'location':
            # Location-specific fields
            self.type_edit = QComboBox()
            self.type_edit.addItems(['City', 'Country', 'Building', 'Room', 'Outdoor', 'Other'])
            self.type_edit.setCurrentText(self.entity_data.get('location_type', 'Other'))
            form_layout.addRow("Type:", self.type_edit)
            
            self.description_edit = QTextEdit()
            self.description_edit.setPlainText(self.entity_data.get('description', ''))
            self.description_edit.setMaximumHeight(100)
            form_layout.addRow("Description:", self.description_edit)
            
        elif self.entity_type == 'relationship':
            # Relationship-specific fields
            self.source_edit = QLineEdit(self.entity_data.get('source', ''))
            form_layout.addRow("Source:", self.source_edit)
            
            self.target_edit = QLineEdit(self.entity_data.get('target', ''))
            form_layout.addRow("Target:", self.target_edit)
            
            self.type_combo = QComboBox()
            self.type_combo.addItems(['knows', 'loves', 'hates', 'works_with', 'related_to', 
                                    'located_at', 'travels_to', 'conflicts_with', 'helps', 'other'])
            self.type_combo.setCurrentText(self.entity_data.get('rel_type', 'knows'))
            form_layout.addRow("Type:", self.type_combo)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
    def get_data(self):
        """Get the edited data."""
        data = {'name': self.name_edit.text()}
        
        if self.entity_type == 'character':
            data['role'] = self.role_edit.text()
            data['motivation'] = self.motivation_edit.toPlainText()
        elif self.entity_type == 'location':
            data['location_type'] = self.type_edit.currentText()
            data['description'] = self.description_edit.toPlainText()
        elif self.entity_type == 'relationship':
            data['source'] = self.source_edit.text()
            data['target'] = self.target_edit.text()
            data['rel_type'] = self.type_combo.currentText()
            
        return data

class Neo4jGraphView(QGraphicsView):
    """Neo4j-style interactive graph visualization."""
    
    # Signals
    nodeClicked = pyqtSignal(str, str)
    nodeDoubleClicked = pyqtSignal(str, str)
    nodeRightClicked = pyqtSignal(str, str, QPoint)
    edgeRightClicked = pyqtSignal(str, str, str, QPoint)
    
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        # Enable interaction
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        
        # Store nodes and edges
        self.nodes = {}  # {node_id: {'item': QGraphicsEllipseItem, 'text': QGraphicsTextItem, 'data': dict}}
        self.edges = {}  # {(source, target): {'line': QGraphicsLineItem, 'arrow': QGraphicsPolygonItem}}
        self.selected_nodes = set()
        
        # Visual settings (Neo4j-like)
        self.node_colors = {
            'character': QColor(106, 168, 79),  # Green
            'location': QColor(255, 187, 51),   # Orange
            'event': QColor(147, 112, 219),     # Purple
            'object': QColor(66, 133, 244),     # Blue
            'theme': QColor(234, 67, 53)        # Red
        }
        
        # Set dark background like Neo4j
        self.setBackgroundBrush(QBrush(QColor(34, 34, 34)))
        
        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)
        
        # Layout settings
        self.layout_type = 'force'  # 'force', 'circular', 'hierarchical'
        self.zoom_level = 1.0
        
    def update_graph(self, graph_storage):
        """Update the graph visualization with Neo4j-style layout."""
        self.scene.clear()
        self.nodes.clear()
        self.edges.clear()
        
        if not graph_storage or not hasattr(graph_storage, 'graph'):
            return
            
        try:
            import networkx as nx
            graph = graph_storage.graph
            
            if graph.number_of_nodes() == 0:
                return
            
            # Calculate layout
            if self.layout_type == 'force':
                pos = nx.spring_layout(graph, k=2, iterations=50, scale=500)
            elif self.layout_type == 'circular':
                pos = nx.circular_layout(graph, scale=300)
            else:  # hierarchical
                pos = nx.shell_layout(graph, scale=300)
            
            # Draw nodes
            for node, (x, y) in pos.items():
                node_data = graph.nodes[node]
                node_type = node_data.get('node_type', 'character')
                self.add_node(node, x * 2, y * 2, node_type, node_data)
            
            # Draw edges with arrows
            for source, target, edge_data in graph.edges(data=True):
                if source in pos and target in pos:
                    self.add_edge(source, target, edge_data)
                    
            # Fit view
            self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
            
        except Exception as e:
            LOGGER.error(f"Failed to update graph: {e}")
    
    def add_node(self, node_id, x, y, node_type, node_data):
        """Add a Neo4j-style node to the graph."""
        # Node circle
        radius = 30
        color = self.node_colors.get(node_type, QColor(128, 128, 128))
        
        # Create circle
        node_item = self.scene.addEllipse(
            -radius, -radius, radius * 2, radius * 2,
            QPen(color.darker(150), 2),
            QBrush(color)
        )
        node_item.setPos(x, y)
        node_item.setFlag(QGraphicsEllipseItem.ItemIsMovable)
        node_item.setFlag(QGraphicsEllipseItem.ItemIsSelectable)
        node_item.setCursor(Qt.PointingHandCursor)
        node_item.setData(0, node_id)
        node_item.setData(1, node_type)
        node_item.setZValue(2)
        
        # Add text label
        text = self.scene.addText(node_id[:15], QFont("Arial", 10))
        text.setDefaultTextColor(Qt.white)
        text.setPos(x - text.boundingRect().width()/2, y - text.boundingRect().height()/2)
        text.setZValue(3)
        
        self.nodes[node_id] = {
            'item': node_item,
            'text': text,
            'data': node_data,
            'type': node_type
        }
    
    def add_edge(self, source, target, edge_data):
        """Add a Neo4j-style edge with arrow."""
        if source not in self.nodes or target not in self.nodes:
            return
            
        source_item = self.nodes[source]['item']
        target_item = self.nodes[target]['item']
        
        # Calculate line positions
        source_pos = source_item.pos()
        target_pos = target_item.pos()
        
        # Draw line
        line = self.scene.addLine(
            source_pos.x(), source_pos.y(),
            target_pos.x(), target_pos.y(),
            QPen(QColor(150, 150, 150), 1.5)
        )
        line.setZValue(0)
        
        # Add arrow at the end
        angle = math.atan2(target_pos.y() - source_pos.y(), 
                          target_pos.x() - source_pos.x())
        
        # Arrow points
        arrow_length = 15
        arrow_angle = math.pi / 6
        
        # Calculate arrow position (at edge of target node)
        radius = 30
        end_x = target_pos.x() - radius * math.cos(angle)
        end_y = target_pos.y() - radius * math.sin(angle)
        
        p1 = QPointF(end_x, end_y)
        p2 = QPointF(end_x - arrow_length * math.cos(angle - arrow_angle),
                    end_y - arrow_length * math.sin(angle - arrow_angle))
        p3 = QPointF(end_x - arrow_length * math.cos(angle + arrow_angle),
                    end_y - arrow_length * math.sin(angle + arrow_angle))
        
        arrow = QPolygonF([p1, p2, p3])
        arrow_item = self.scene.addPolygon(arrow, QPen(QColor(150, 150, 150)), 
                                          QBrush(QColor(150, 150, 150)))
        arrow_item.setZValue(1)
        
        # Add relationship label
        rel_type = edge_data.get('relationship', edge_data.get('rel_type', ''))
        if rel_type:
            mid_x = (source_pos.x() + target_pos.x()) / 2
            mid_y = (source_pos.y() + target_pos.y()) / 2
            label = self.scene.addText(rel_type, QFont("Arial", 8))
            label.setDefaultTextColor(QColor(200, 200, 200))
            label.setPos(mid_x - label.boundingRect().width()/2, 
                        mid_y - label.boundingRect().height()/2)
            label.setZValue(1)
        
        self.edges[(source, target)] = {
            'line': line,
            'arrow': arrow_item,
            'data': edge_data
        }
    
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        item = self.itemAt(event.pos())
        
        if event.button() == Qt.RightButton:
            # Right-click context menu
            if isinstance(item, QGraphicsEllipseItem):
                node_id = item.data(0)
                node_type = item.data(1)
                if node_id:
                    self.nodeRightClicked.emit(node_id, node_type, event.globalPos())
            elif isinstance(item, QGraphicsLineItem):
                # Find which edge this line belongs to
                for (source, target), edge_data in self.edges.items():
                    if edge_data['line'] == item:
                        self.edgeRightClicked.emit(source, target, 
                                                  edge_data['data'].get('rel_type', ''),
                                                  event.globalPos())
                        break
        elif event.button() == Qt.LeftButton:
            if isinstance(item, QGraphicsEllipseItem):
                node_id = item.data(0)
                node_type = item.data(1)
                if node_id:
                    # Toggle selection
                    if node_id in self.selected_nodes:
                        self.selected_nodes.remove(node_id)
                        item.setPen(QPen(self.node_colors.get(node_type, QColor(128, 128, 128)).darker(150), 2))
                    else:
                        self.selected_nodes.add(node_id)
                        item.setPen(QPen(Qt.cyan, 3))
                    self.nodeClicked.emit(node_id, node_type)
            else:
                # Enable panning
                self.setDragMode(QGraphicsView.ScrollHandDrag)
        
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        self.setDragMode(QGraphicsView.RubberBandDrag)
        super().mouseReleaseEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """Handle double-click events."""
        item = self.itemAt(event.pos())
        if isinstance(item, QGraphicsEllipseItem):
            node_id = item.data(0)
            node_type = item.data(1)
            if node_id:
                self.nodeDoubleClicked.emit(node_id, node_type)
        super().mouseDoubleClickEvent(event)
    
    def wheelEvent(self, event):
        """Handle zoom with mouse wheel."""
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor
        
        # Save the scene pos
        old_pos = self.mapToScene(event.pos())
        
        # Zoom
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
            self.zoom_level *= zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
            self.zoom_level *= zoom_out_factor
        
        # Limit zoom
        if self.zoom_level < 0.1:
            self.zoom_level = 0.1
            return
        elif self.zoom_level > 10:
            self.zoom_level = 10
            return
            
        self.scale(zoom_factor, zoom_factor)
        
        # Get the new position
        new_pos = self.mapToScene(event.pos())
        
        # Move scene to old position
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())
    
    def set_layout(self, layout_type):
        """Change the graph layout."""
        self.layout_type = layout_type
        # Trigger redraw
        from manuskript.ai.narrative_graph import narrative_graph
        if narrative_graph.current_graph_storage:
            self.update_graph(narrative_graph.current_graph_storage)

class EnhancedNarrativeGraphWidget(QWidget):
    """Enhanced narrative graph widget with full editing capabilities."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.graph_storage = None
        self.scan_thread = None
        self._last_stats = {}
        self.setupUI()
        self.setupTimer()
        
    def setupUI(self):
        """Set up the enhanced UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Toolbar
        toolbar = self.create_toolbar()
        main_layout.addWidget(toolbar)
        
        # Main content
        splitter = QSplitter(Qt.Vertical)
        
        # Graph view at top (Neo4j-style)
        self.graph_view = Neo4jGraphView()
        self.graph_view.nodeDoubleClicked.connect(self.on_node_double_clicked)
        self.graph_view.nodeRightClicked.connect(self.show_node_context_menu)
        self.graph_view.edgeRightClicked.connect(self.show_edge_context_menu)
        splitter.addWidget(self.graph_view)
        
        # Tabs at bottom
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_entities_panel(), "Entities")
        self.tabs.addTab(self.create_relationships_panel(), "Relationships")
        self.tabs.addTab(self.create_query_panel(), "Query")
        self.tabs.addTab(self.create_stats_panel(), "Statistics")
        splitter.addWidget(self.tabs)
        
        splitter.setSizes([400, 200])
        main_layout.addWidget(splitter)
        
        # Status bar
        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)
        
    def create_toolbar(self):
        """Create the toolbar with controls."""
        toolbar = QToolBar()
        
        # Scan button
        self.scan_action = QAction("📊 Scan Project", self)
        self.scan_action.triggered.connect(self.scan_project_content)
        toolbar.addAction(self.scan_action)
        
        toolbar.addSeparator()
        
        # Add entity actions
        add_char_action = QAction("➕ Add Character", self)
        add_char_action.triggered.connect(lambda: self.add_entity('character'))
        toolbar.addAction(add_char_action)
        
        add_loc_action = QAction("📍 Add Location", self)
        add_loc_action.triggered.connect(lambda: self.add_entity('location'))
        toolbar.addAction(add_loc_action)
        
        add_rel_action = QAction("🔗 Add Relationship", self)
        add_rel_action.triggered.connect(lambda: self.add_entity('relationship'))
        toolbar.addAction(add_rel_action)
        
        toolbar.addSeparator()
        
        # Layout options
        layout_action = QAction("📐 Layout", self)
        layout_menu = QMenu()
        layout_menu.addAction("Force Layout", lambda: self.graph_view.set_layout('force'))
        layout_menu.addAction("Circular Layout", lambda: self.graph_view.set_layout('circular'))
        layout_menu.addAction("Hierarchical Layout", lambda: self.graph_view.set_layout('hierarchical'))
        layout_action.setMenu(layout_menu)
        toolbar.addAction(layout_action)
        
        toolbar.addSeparator()
        
        # Zoom controls
        zoom_label = QLabel("Zoom:")
        toolbar.addWidget(zoom_label)
        
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(10, 200)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setMaximumWidth(100)
        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)
        toolbar.addWidget(self.zoom_slider)
        
        return toolbar
    
    def create_entities_panel(self):
        """Create the entities management panel."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Characters table
        layout.addWidget(QLabel("Characters:"))
        self.characters_table = QTableWidget()
        self.characters_table.setColumnCount(4)
        self.characters_table.setHorizontalHeaderLabels(["Name", "Role", "Connections", "Actions"])
        self.characters_table.horizontalHeader().setStretchLastSection(False)
        self.characters_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.characters_table.customContextMenuRequested.connect(self.show_character_context_menu)
        layout.addWidget(self.characters_table)
        
        # Locations table
        layout.addWidget(QLabel("Locations:"))
        self.locations_table = QTableWidget()
        self.locations_table.setColumnCount(4)
        self.locations_table.setHorizontalHeaderLabels(["Name", "Type", "Mentions", "Actions"])
        self.locations_table.horizontalHeader().setStretchLastSection(False)
        self.locations_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.locations_table.customContextMenuRequested.connect(self.show_location_context_menu)
        layout.addWidget(self.locations_table)
        
        return widget
    
    def create_relationships_panel(self):
        """Create the relationships management panel."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.relationships_table = QTableWidget()
        self.relationships_table.setColumnCount(4)
        self.relationships_table.setHorizontalHeaderLabels(["Source", "Type", "Target", "Actions"])
        self.relationships_table.horizontalHeader().setStretchLastSection(False)
        self.relationships_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.relationships_table.customContextMenuRequested.connect(self.show_relationship_context_menu)
        layout.addWidget(self.relationships_table)
        
        return widget
    
    def create_query_panel(self):
        """Create a query panel for graph queries."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("Query the narrative graph:"))
        
        # Query input
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("e.g., Find all characters who know Paul")
        layout.addWidget(self.query_input)
        
        # Query button
        query_btn = QPushButton("Execute Query")
        query_btn.clicked.connect(self.execute_query)
        layout.addWidget(query_btn)
        
        # Results
        self.query_results = QTextEdit()
        self.query_results.setReadOnly(True)
        layout.addWidget(self.query_results)
        
        return widget
    
    def create_stats_panel(self):
        """Create statistics panel."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        layout.addWidget(self.stats_text)
        
        return widget
    
    def setupTimer(self):
        """Set up auto-refresh timer."""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(5000)  # Refresh every 5 seconds
    
    def refresh_data(self):
        """Refresh all displayed data."""
        from manuskript.ai.narrative_graph import narrative_graph
        self.graph_storage = narrative_graph.current_graph_storage
        
        if not self.graph_storage:
            return
            
        try:
            # Update graph
            self.graph_view.update_graph(self.graph_storage)
            
            # Update tables
            self.update_entities_tables()
            self.update_relationships_table()
            self.update_statistics()
            
        except Exception as e:
            LOGGER.error(f"Failed to refresh data: {e}")
    
    def update_entities_tables(self):
        """Update character and location tables."""
        if not self.graph_storage or not hasattr(self.graph_storage, 'graph'):
            return
            
        graph = self.graph_storage.graph
        
        # Update characters
        characters = [(n, d) for n, d in graph.nodes(data=True) if d.get('node_type') == 'character']
        self.characters_table.setRowCount(len(characters))
        
        for i, (name, data) in enumerate(characters):
            self.characters_table.setItem(i, 0, QTableWidgetItem(name))
            self.characters_table.setItem(i, 1, QTableWidgetItem(data.get('role', '')))
            self.characters_table.setItem(i, 2, QTableWidgetItem(str(graph.degree(name))))
            
            # Actions button
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setMaximumSize(30, 25)
            edit_btn.clicked.connect(lambda checked, n=name: self.edit_entity('character', n))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setMaximumSize(30, 25)
            delete_btn.clicked.connect(lambda checked, n=name: self.delete_entity(n))
            actions_layout.addWidget(delete_btn)
            
            self.characters_table.setCellWidget(i, 3, actions_widget)
        
        # Update locations
        locations = [(n, d) for n, d in graph.nodes(data=True) if d.get('node_type') == 'location']
        self.locations_table.setRowCount(len(locations))
        
        for i, (name, data) in enumerate(locations):
            self.locations_table.setItem(i, 0, QTableWidgetItem(name))
            self.locations_table.setItem(i, 1, QTableWidgetItem(data.get('location_type', '')))
            self.locations_table.setItem(i, 2, QTableWidgetItem(str(data.get('mentions', 0))))
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setMaximumSize(30, 25)
            edit_btn.clicked.connect(lambda checked, n=name: self.edit_entity('location', n))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setMaximumSize(30, 25)
            delete_btn.clicked.connect(lambda checked, n=name: self.delete_entity(n))
            actions_layout.addWidget(delete_btn)
            
            self.locations_table.setCellWidget(i, 3, actions_widget)
    
    def update_relationships_table(self):
        """Update relationships table."""
        if not self.graph_storage or not hasattr(self.graph_storage, 'graph'):
            return
            
        graph = self.graph_storage.graph
        
        relationships = []
        for source, target, data in graph.edges(data=True):
            rel_type = data.get('relationship', data.get('rel_type', 'connected'))
            relationships.append((source, target, rel_type))
        
        self.relationships_table.setRowCount(len(relationships))
        
        for i, (source, target, rel_type) in enumerate(relationships):
            self.relationships_table.setItem(i, 0, QTableWidgetItem(source))
            self.relationships_table.setItem(i, 1, QTableWidgetItem(rel_type))
            self.relationships_table.setItem(i, 2, QTableWidgetItem(target))
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setMaximumSize(30, 25)
            edit_btn.clicked.connect(lambda checked, s=source, t=target: self.edit_relationship(s, t))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setMaximumSize(30, 25)
            delete_btn.clicked.connect(lambda checked, s=source, t=target: self.delete_relationship(s, t))
            actions_layout.addWidget(delete_btn)
            
            self.relationships_table.setCellWidget(i, 3, actions_widget)
    
    def update_statistics(self):
        """Update statistics panel."""
        if not self.graph_storage:
            return
            
        stats = self.graph_storage.get_stats()
        
        # Calculate additional statistics
        try:
            import networkx as nx
            graph = self.graph_storage.graph
            
            text = f"""
Graph Statistics:
================
Total Nodes: {stats.get('total_nodes', 0)}
- Characters: {stats.get('characters', 0)}
- Locations: {stats.get('locations', 0)}
- Events: {stats.get('events', 0)}

Total Relationships: {stats.get('relationships', 0)}

Network Metrics:
- Density: {nx.density(graph):.3f}
- Average Clustering: {nx.average_clustering(graph) if graph.number_of_nodes() > 0 else 0:.3f}
- Number of Components: {nx.number_connected_components(graph.to_undirected())}

Most Connected Characters:
"""
            # Get top 5 most connected characters
            chars = [(n, graph.degree(n)) for n, d in graph.nodes(data=True) 
                    if d.get('node_type') == 'character']
            chars.sort(key=lambda x: x[1], reverse=True)
            
            for name, degree in chars[:5]:
                text += f"- {name}: {degree} connections\n"
                
            self.stats_text.setPlainText(text)
            
        except Exception as e:
            self.stats_text.setPlainText(f"Statistics: {stats}")
    
    # Context menu actions
    def show_node_context_menu(self, node_id, node_type, pos):
        """Show context menu for a node."""
        menu = QMenu(self)
        
        # Edit action
        edit_action = menu.addAction("Edit")
        edit_action.triggered.connect(lambda: self.edit_entity(node_type, node_id))
        
        # Delete action
        delete_action = menu.addAction("Delete")
        delete_action.triggered.connect(lambda: self.delete_entity(node_id))
        
        menu.addSeparator()
        
        # View connections
        connections_action = menu.addAction("View Connections")
        connections_action.triggered.connect(lambda: self.view_connections(node_id))
        
        # Open in main window
        if node_type == 'character':
            open_action = menu.addAction("Open in Characters")
            open_action.triggered.connect(lambda: self.open_in_characters(node_id))
        elif node_type == 'location':
            open_action = menu.addAction("Open in World")
            open_action.triggered.connect(lambda: self.open_in_world(node_id))
        
        menu.exec_(pos)
    
    def show_edge_context_menu(self, source, target, rel_type, pos):
        """Show context menu for an edge."""
        menu = QMenu(self)
        
        edit_action = menu.addAction("Edit Relationship")
        edit_action.triggered.connect(lambda: self.edit_relationship(source, target))
        
        delete_action = menu.addAction("Delete Relationship")
        delete_action.triggered.connect(lambda: self.delete_relationship(source, target))
        
        menu.exec_(pos)
    
    def show_character_context_menu(self, pos):
        """Show context menu for character table."""
        item = self.characters_table.itemAt(pos)
        if item:
            row = item.row()
            name_item = self.characters_table.item(row, 0)
            if name_item:
                self.show_node_context_menu(name_item.text(), 'character', 
                                           self.characters_table.mapToGlobal(pos))
    
    def show_location_context_menu(self, pos):
        """Show context menu for location table."""
        item = self.locations_table.itemAt(pos)
        if item:
            row = item.row()
            name_item = self.locations_table.item(row, 0)
            if name_item:
                self.show_node_context_menu(name_item.text(), 'location',
                                           self.locations_table.mapToGlobal(pos))
    
    def show_relationship_context_menu(self, pos):
        """Show context menu for relationship table."""
        item = self.relationships_table.itemAt(pos)
        if item:
            row = item.row()
            source = self.relationships_table.item(row, 0).text()
            target = self.relationships_table.item(row, 2).text()
            rel_type = self.relationships_table.item(row, 1).text()
            self.show_edge_context_menu(source, target, rel_type,
                                       self.relationships_table.mapToGlobal(pos))
    
    # CRUD operations
    def add_entity(self, entity_type):
        """Add a new entity."""
        dialog = EntityEditDialog(entity_type, parent=self)
        if dialog.exec_():
            data = dialog.get_data()
            
            if self.graph_storage:
                if entity_type == 'character':
                    self.graph_storage.add_character(data['name'], 
                                                    description=data.get('motivation', ''))
                elif entity_type == 'location':
                    self.graph_storage.add_location(data['name'],
                                                  description=data.get('description', ''))
                elif entity_type == 'relationship':
                    self.graph_storage.add_relationship(data['source'],
                                                       data['target'],
                                                       data['rel_type'])
                
                self.refresh_data()
                self.status_label.setText(f"Added {entity_type}: {data.get('name', '')}")
    
    def edit_entity(self, entity_type, entity_id):
        """Edit an existing entity."""
        if not self.graph_storage:
            return
            
        # Get current data
        if entity_type in ['character', 'location']:
            if entity_id in self.graph_storage.graph.nodes:
                current_data = self.graph_storage.graph.nodes[entity_id].copy()
                current_data['name'] = entity_id
            else:
                return
        else:
            return
        
        dialog = EntityEditDialog(entity_type, current_data, parent=self)
        if dialog.exec_():
            data = dialog.get_data()
            
            # Update the graph
            for key, value in data.items():
                if key != 'name':
                    self.graph_storage.graph.nodes[entity_id][key] = value
            
            self.refresh_data()
            self.status_label.setText(f"Updated {entity_type}: {entity_id}")
    
    def delete_entity(self, entity_id):
        """Delete an entity."""
        reply = QMessageBox.question(self, 'Delete Entity',
                                    f"Delete '{entity_id}' and all its relationships?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.graph_storage and entity_id in self.graph_storage.graph.nodes:
                self.graph_storage.graph.remove_node(entity_id)
                self.refresh_data()
                self.status_label.setText(f"Deleted: {entity_id}")
    
    def edit_relationship(self, source, target):
        """Edit a relationship."""
        if not self.graph_storage:
            return
            
        if self.graph_storage.graph.has_edge(source, target):
            current_data = self.graph_storage.graph.edges[source, target].copy()
            current_data['source'] = source
            current_data['target'] = target
            
            dialog = EntityEditDialog('relationship', current_data, parent=self)
            if dialog.exec_():
                data = dialog.get_data()
                self.graph_storage.graph.edges[source, target]['rel_type'] = data['rel_type']
                self.graph_storage.graph.edges[source, target]['relationship'] = data['rel_type']
                self.refresh_data()
                self.status_label.setText(f"Updated relationship: {source} -> {target}")
    
    def delete_relationship(self, source, target):
        """Delete a relationship."""
        reply = QMessageBox.question(self, 'Delete Relationship',
                                    f"Delete relationship between '{source}' and '{target}'?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.graph_storage and self.graph_storage.graph.has_edge(source, target):
                self.graph_storage.graph.remove_edge(source, target)
                self.refresh_data()
                self.status_label.setText(f"Deleted relationship: {source} -> {target}")
    
    def view_connections(self, node_id):
        """View all connections for a node."""
        if not self.graph_storage or node_id not in self.graph_storage.graph.nodes:
            return
            
        connections = []
        for neighbor in self.graph_storage.graph.neighbors(node_id):
            edge_data = self.graph_storage.graph.edges[node_id, neighbor]
            rel_type = edge_data.get('relationship', edge_data.get('rel_type', 'connected'))
            connections.append(f"→ {neighbor} ({rel_type})")
        
        for neighbor in self.graph_storage.graph.predecessors(node_id):
            if neighbor != node_id:  # Skip self-loops
                edge_data = self.graph_storage.graph.edges[neighbor, node_id]
                rel_type = edge_data.get('relationship', edge_data.get('rel_type', 'connected'))
                connections.append(f"← {neighbor} ({rel_type})")
        
        text = f"Connections for {node_id}:\n" + "\n".join(connections)
        QMessageBox.information(self, f"Connections: {node_id}", text)
    
    def open_in_characters(self, character_name):
        """Open character in main characters window."""
        try:
            from manuskript import functions as F
            main_window = F.mainWindow()
            
            if main_window and hasattr(main_window, 'mdlCharacter'):
                # Find or create character
                model = main_window.mdlCharacter
                found = False
                
                for i in range(model.rowCount()):
                    index = model.index(i, 0)  # Name column
                    if model.data(index) == character_name:
                        # Switch to character tab and select
                        main_window.tabMain.setCurrentIndex(2)
                        main_window.lstCharacters.setCurrentIndex(index)
                        found = True
                        break
                
                if not found:
                    # Create new character
                    from manuskript.models import characterModel
                    new_char = characterModel.Character(model)
                    new_char.name = character_name
                    model.characters.append(new_char)
                    model.layoutChanged.emit()
                    
                    # Switch to character tab
                    main_window.tabMain.setCurrentIndex(2)
                    
        except Exception as e:
            LOGGER.error(f"Failed to open character: {e}")
    
    def open_in_world(self, location_name):
        """Open location in main world window."""
        try:
            from manuskript import functions as F
            main_window = F.mainWindow()
            
            if main_window and hasattr(main_window, 'mdlWorld'):
                # Implementation similar to character but for world model
                main_window.tabMain.setCurrentIndex(3)  # World tab
                
        except Exception as e:
            LOGGER.error(f"Failed to open location: {e}")
    
    def execute_query(self):
        """Execute a graph query."""
        query = self.query_input.text()
        if not query or not self.graph_storage:
            return
            
        try:
            # Simple query parsing
            results = []
            graph = self.graph_storage.graph
            
            if "who know" in query.lower():
                # Find connections
                for word in query.split():
                    if word in graph.nodes:
                        neighbors = list(graph.neighbors(word))
                        results.append(f"{word} knows: {', '.join(neighbors)}")
                        
            elif "characters" in query.lower():
                chars = [n for n, d in graph.nodes(data=True) if d.get('node_type') == 'character']
                results.append(f"Characters: {', '.join(chars)}")
                
            elif "locations" in query.lower():
                locs = [n for n, d in graph.nodes(data=True) if d.get('node_type') == 'location']
                results.append(f"Locations: {', '.join(locs)}")
            
            self.query_results.setPlainText("\n".join(results) if results else "No results found")
            
        except Exception as e:
            self.query_results.setPlainText(f"Query error: {e}")
    
    def on_node_double_clicked(self, node_id, node_type):
        """Handle node double-click."""
        if node_type == 'character':
            self.open_in_characters(node_id)
        elif node_type == 'location':
            self.open_in_world(node_id)
    
    def on_zoom_changed(self, value):
        """Handle zoom slider change."""
        scale = value / 100.0
        self.graph_view.resetTransform()
        self.graph_view.scale(scale, scale)
    
    def scan_project_content(self):
        """Scan project content (implement async scanning)."""
        self.status_label.setText("Scanning project...")
        # Trigger the narrative graph scan
        from manuskript.ai.narrative_graph import narrative_graph
        from manuskript import functions as F
        
        main_window = F.mainWindow()
        if main_window and narrative_graph.current_graph_storage:
            narrative_graph._scan_project_content(main_window)
            self.refresh_data()
            self.status_label.setText("Scan complete")
    
    def sizeHint(self):
        return QSize(800, 600)