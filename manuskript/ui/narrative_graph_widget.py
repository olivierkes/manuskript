#!/usr/bin/env python
# --!-- coding: utf8 --!--
"""
Narrative Graph Widget

GUI component for viewing and interacting with the narrative graph.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
                            QTableWidget, QTableWidgetItem, QTextEdit, QLabel, 
                            QPushButton, QSplitter, QTreeWidget, QTreeWidgetItem,
                            QProgressBar, QGroupBox, QScrollArea, QFrame, 
                            QHeaderView, QAbstractItemView, QMessageBox, QDockWidget,
                            QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,
                            QGraphicsTextItem, QGraphicsLineItem)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot, QSize, QRectF, QPointF
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon, QPen, QBrush, QWheelEvent, QTransform, QPainter

from manuskript import settings
import logging
from typing import Dict, List, Optional, Any
import math
import random

LOGGER = logging.getLogger(__name__)

class ScanThread(QThread):
    """Thread for scanning project content without blocking UI."""
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        
    def run(self):
        """Run the scan in a separate thread."""
        try:
            from manuskript.ai.narrative_graph import narrative_graph
            from manuskript import functions as F
            
            main_window = F.mainWindow()
            if not main_window:
                self.status.emit("No project loaded")
                return
                
            # Initialize if needed - check both engine and storage
            if (not hasattr(narrative_graph, 'current_graph_engine') or narrative_graph.current_graph_engine is None) and \
               (not hasattr(narrative_graph, 'current_graph_storage') or narrative_graph.current_graph_storage is None):
                self.status.emit("Initializing graph...")
                self.progress.emit(10)
                if hasattr(main_window, 'currentProject'):
                    project_path = main_window.currentProject
                    narrative_graph.on_project_loaded(project_path, main_window)
                else:
                    self.status.emit("No project path available")
                    return
            
            # Trigger the actual scan using the _scan_project_content function
            self.status.emit("Scanning project content...")
            self.progress.emit(20)
            
            # Call the scan function directly
            from manuskript.ai.narrative_graph.narrative_graph import _scan_project_content
            _scan_project_content(main_window)
            
            self.progress.emit(90)
            
            # Import scanning components
            from manuskript.ai.narrative_graph.utils import extract_entities, analyze_relationships
            from manuskript.enums import Outline
            
            items_processed = 0
            total_items = self._count_items(main_window.mdlOutline.rootItem)
            
            # Scan items with progress using batch processing for memory efficiency
            self._scan_items_batch_processed(main_window.mdlOutline.rootItem, 
                                           narrative_graph.current_graph_storage,
                                           total_items)
            
            self.progress.emit(100)
            self.status.emit("Scan complete!")
            
        except Exception as e:
            LOGGER.error(f"Scan thread failed: {e}", exc_info=True)
            self.status.emit(f"Scan failed: {str(e)[:50]}")
    
    def _count_items(self, item):
        """Count total items to scan."""
        count = 1
        for i in range(item.childCount()):
            count += self._count_items(item.child(i))
        return count
    
    def _scan_items_recursive(self, item, storage, processed, total):
        """Recursively scan items and update progress."""
        from manuskript.enums import Outline
        
        # Try to use smart extraction if available
        try:
            from manuskript.ai.narrative_graph.smart_extraction import SmartEntityExtractor
            from manuskript import functions as F
            main_window = F.mainWindow()
            extractor = SmartEntityExtractor(main_window)
            use_smart = True
            
            # Get existing entities
            existing_chars = extractor.get_existing_characters()
            existing_locs = extractor.get_existing_locations()
        except ImportError:
            from manuskript.ai.narrative_graph.utils import extract_entities, analyze_relationships
            use_smart = False
        
        # Process this item
        text = item.data(Outline.text.value)
        title = item.data(Outline.title.value) or ""
        item_id = item.data(Outline.ID.value) or ""
        
        if text:
            try:
                if use_smart:
                    # Use smart extraction
                    entities = extractor.extract_from_text(text)
                    
                    # Add to storage (avoiding duplicates)
                    for character in entities.get("characters", []):
                        if character not in [c['name'] for c in existing_chars.values()]:
                            storage.add_character(character)
                    for location in entities.get("locations", []):
                        if location not in [l['name'] for l in existing_locs.values()]:
                            storage.add_location(location)
                    
                    # Analyze interactions
                    interactions = extractor.analyze_character_interactions(text, entities.get('characters', []))
                    for interaction in interactions:
                        storage.add_relationship(
                            interaction['character1'],
                            interaction['character2'],
                            interaction['type']
                        )
                else:
                    # Fall back to basic extraction
                    entities = extract_entities(text)
                    
                    # Add to storage (avoiding duplicates)
                    for character in entities.get("characters", []):
                        storage.add_character(character)
                    for location in entities.get("locations", []):
                        storage.add_location(location)
                    
                    # Add relationships
                    relationships = analyze_relationships(text, entities)
                    for source, rel_type, target in relationships:
                        if source and target and source != target:  # Avoid self-loops
                            storage.add_relationship(source, target, rel_type)
                        
            except Exception as e:
                LOGGER.debug(f"Failed to process item: {e}")
        
        # Update progress
        processed += 1
        progress_pct = min(20 + int((processed / total) * 70), 90)
        self.progress.emit(progress_pct)
        
        # Process children
        for i in range(item.childCount()):
            processed = self._scan_items_recursive(item.child(i), storage, processed, total)
        
        return processed
    
    def _scan_items_batch_processed(self, root_item, storage, total_items):
        """
        Scan items with batch processing to optimize memory usage and performance.
        Process items in chunks to prevent memory buildup and improve progress feedback.
        """
        import gc
        from manuskript.enums import Outline
        
        # Collect all items to process first (flattened tree)
        items_to_scan = []
        self._flatten_items_recursive(root_item, items_to_scan)
        
        # Process in batches for better memory management
        batch_size = 50  # Process 50 items at a time
        processed = 0
        
        for i in range(0, len(items_to_scan), batch_size):
            batch = items_to_scan[i:i + batch_size]
            
            # Process batch
            for item in batch:
                try:
                    # Get text content
                    text = item.data(Outline.text.value) or ""
                    if len(text.strip()) < 10:  # Skip very short text
                        continue
                    
                    # Process with smart extraction if available
                    self._process_item_text(item, text, storage)
                    
                except Exception as e:
                    LOGGER.debug(f"Failed to process batch item: {e}")
                
                # Update progress
                processed += 1
                if processed % 10 == 0:  # Update progress every 10 items
                    progress_pct = min(20 + int((processed / total_items) * 70), 90)
                    self.progress.emit(progress_pct)
            
            # Force garbage collection after each batch to free memory
            gc.collect()
    
    def _flatten_items_recursive(self, item, items_list):
        """Flatten the tree structure into a list for batch processing."""
        items_list.append(item)
        for i in range(item.childCount()):
            self._flatten_items_recursive(item.child(i), items_list)
    
    def _process_item_text(self, item, text, storage):
        """Process text content from an item using smart extraction."""
        try:
            from manuskript.ai.narrative_graph.smart_extraction import SmartEntityExtractor
            from manuskript import functions as F
            
            # Get or create extractor
            main_window = F.mainWindow()
            if not hasattr(self, '_extractor'):
                self._extractor = SmartEntityExtractor(main_window)
            
            # Extract entities using smart extraction
            result = self._extractor.extract_from_text(text)
            
            # Add extracted entities to storage (with deduplication)
            for character in result.get("characters", set()):
                storage.add_character(character)
            for location in result.get("locations", set()):
                storage.add_location(location)
            
            # Add interactions as relationships
            for char1, action, char2 in result.get("interactions", []):
                if char1 and char2 and char1 != char2:
                    storage.add_relationship(char1, char2, action)
                    
        except ImportError:
            # Fall back to basic extraction if smart extraction unavailable
            from manuskript.ai.narrative_graph.utils import extract_entities, analyze_relationships
            entities = extract_entities(text)
            
            for character in entities.get("characters", []):
                storage.add_character(character)
            for location in entities.get("locations", []):
                storage.add_location(location)
            
            relationships = analyze_relationships(text, entities)
            for source, rel_type, target in relationships:
                if source and target and source != target:
                    storage.add_relationship(source, target, rel_type)

class InteractiveGraphView(QGraphicsView):
    """Interactive graph visualization with zoom and pan."""
    
    # Signals
    nodeClicked = pyqtSignal(str, str)  # node_name, node_type
    nodeDoubleClicked = pyqtSignal(str, str)  # node_name, node_type
    
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        # Enable interaction
        self.setDragMode(QGraphicsView.RubberBandDrag)  # Allow selection
        self.setRenderHint(QPainter.Antialiasing)
        
        # Store node positions and items
        self.node_items = {}  # {node_name: (ellipse_item, text_item)}
        self.edge_items = []
        self.selected_node = None
        
        # Set background
        self.setBackgroundBrush(QBrush(QColor(250, 250, 250)))
        
        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)
        
    def wheelEvent(self, event):
        """Handle zoom with mouse wheel."""
        # Calculate zoom factor
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor
        
        # Save the scene pos
        old_pos = self.mapToScene(event.pos())
        
        # Zoom
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
        
        self.scale(zoom_factor, zoom_factor)
        
        # Get the new position
        new_pos = self.mapToScene(event.pos())
        
        # Move scene to old position
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())
    
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.LeftButton:
            # Check if we clicked on a node
            item = self.itemAt(event.pos())
            if isinstance(item, QGraphicsEllipseItem):
                node_name = item.data(0)
                node_type = item.data(1)
                if node_name:
                    self.selected_node = node_name
                    self.nodeClicked.emit(node_name, node_type)
                    # Highlight selected node
                    self._highlight_node(node_name)
            else:
                # Enable panning
                self.setDragMode(QGraphicsView.ScrollHandDrag)
        
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        # Reset to selection mode
        self.setDragMode(QGraphicsView.RubberBandDrag)
        super().mouseReleaseEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """Handle double-click events."""
        if event.button() == Qt.LeftButton:
            item = self.itemAt(event.pos())
            if isinstance(item, QGraphicsEllipseItem):
                node_name = item.data(0)
                node_type = item.data(1)
                if node_name:
                    self.nodeDoubleClicked.emit(node_name, node_type)
        
        super().mouseDoubleClickEvent(event)
    
    def _highlight_node(self, node_name):
        """Highlight a selected node."""
        # Reset all nodes to normal
        for name, (ellipse, text) in self.node_items.items():
            if name == node_name:
                # Highlight selected
                ellipse.setPen(QPen(QColor(255, 200, 0), 4))
            else:
                # Normal pen
                node_type = ellipse.data(1)
                if node_type == 'character':
                    color = QColor(100, 150, 200)
                elif node_type == 'location':
                    color = QColor(150, 200, 100)
                else:
                    color = QColor(150, 150, 150)
                ellipse.setPen(QPen(color.darker(), 2))
    
    def update_graph(self, graph_storage):
        """Update the graph visualization."""
        try:
            self.scene.clear()
            self.node_items.clear()
            self.edge_items.clear()
            
            if not graph_storage:
                return
                
            from manuskript.ai.narrative_graph.narrative_graph import NETWORKX_AVAILABLE
            
            if not NETWORKX_AVAILABLE or not hasattr(graph_storage, 'graph'):
                # Show message
                text = self.scene.addText("Graph visualization requires NetworkX\nInstall with: pip install networkx")
                text.setDefaultTextColor(QColor(100, 100, 100))
                return
            
            graph = graph_storage.graph
            if graph.number_of_nodes() == 0:
                text = self.scene.addText("No data to visualize\nClick 'Scan Content' to analyze project")
                text.setDefaultTextColor(QColor(100, 100, 100))
                return
            
            # Calculate layout using force-directed algorithm
            positions = self._calculate_layout(graph)
            
            # Draw edges first (so they appear behind nodes)
            for source, target in graph.edges():
                if source in positions and target in positions:
                    self._draw_edge(positions[source], positions[target], source, target)
            
            # Draw nodes
            for node, (x, y) in positions.items():
                node_data = graph.nodes[node]
                node_type = node_data.get('node_type', 'unknown')
                self._draw_node(x, y, node, node_type)
            
            # Fit in view
            self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
            
        except Exception as e:
            LOGGER.error(f"Failed to update graph view: {e}")
    
    def _calculate_layout(self, graph):
        """Calculate node positions using a simple force-directed layout."""
        positions = {}
        nodes = list(graph.nodes())
        
        if not nodes:
            return positions
        
        # Initialize random positions
        for i, node in enumerate(nodes):
            angle = 2 * math.pi * i / len(nodes)
            radius = 200
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            positions[node] = (x, y)
        
        # Simple force-directed iterations
        for _ in range(50):
            forces = {node: (0, 0) for node in nodes}
            
            # Repulsive forces between all nodes
            for i, node1 in enumerate(nodes):
                for node2 in nodes[i+1:]:
                    x1, y1 = positions[node1]
                    x2, y2 = positions[node2]
                    dx = x2 - x1
                    dy = y2 - y1
                    dist = math.sqrt(dx*dx + dy*dy) + 0.01
                    force = 5000 / (dist * dist)
                    fx = -force * dx / dist
                    fy = -force * dy / dist
                    forces[node1] = (forces[node1][0] + fx, forces[node1][1] + fy)
                    forces[node2] = (forces[node2][0] - fx, forces[node2][1] - fy)
            
            # Attractive forces for edges
            for source, target in graph.edges():
                if source in positions and target in positions:
                    x1, y1 = positions[source]
                    x2, y2 = positions[target]
                    dx = x2 - x1
                    dy = y2 - y1
                    dist = math.sqrt(dx*dx + dy*dy) + 0.01
                    force = dist / 100
                    fx = force * dx / dist
                    fy = force * dy / dist
                    forces[source] = (forces[source][0] + fx, forces[source][1] + fy)
                    forces[target] = (forces[target][0] - fx, forces[target][1] - fy)
            
            # Apply forces
            for node in nodes:
                fx, fy = forces[node]
                x, y = positions[node]
                positions[node] = (x + fx * 0.01, y + fy * 0.01)
        
        return positions
    
    def _draw_node(self, x, y, label, node_type):
        """Draw a node in the graph."""
        # Choose color based on type
        if node_type == 'character':
            color = QColor(100, 150, 200)
        elif node_type == 'location':
            color = QColor(150, 200, 100)
        elif node_type == 'event':
            color = QColor(200, 150, 100)
        else:
            color = QColor(150, 150, 150)
        
        # Draw circle
        radius = 25
        ellipse = self.scene.addEllipse(x - radius, y - radius, radius * 2, radius * 2,
                                       QPen(color.darker(), 2), QBrush(color))
        
        # Make it interactive
        ellipse.setFlag(QGraphicsEllipseItem.ItemIsSelectable, True)
        ellipse.setCursor(Qt.PointingHandCursor)
        ellipse.setData(0, label)  # Store node name
        ellipse.setData(1, node_type)  # Store node type
        
        # Draw label
        text = self.scene.addText(label[:20])  # Truncate long labels
        text.setPos(x - text.boundingRect().width() / 2, y - text.boundingRect().height() / 2)
        text.setDefaultTextColor(Qt.white)
        font = QFont()
        font.setPointSize(9)
        font.setBold(True)
        text.setFont(font)
        text.setFlag(QGraphicsTextItem.ItemIsSelectable, False)  # Text not selectable
        
        # Add hover tooltip
        ellipse.setToolTip(f"{node_type.capitalize()}: {label}")
        
        self.node_items[label] = (ellipse, text)
    
    def _draw_edge(self, pos1, pos2, source, target):
        """Draw an edge between two nodes."""
        x1, y1 = pos1
        x2, y2 = pos2
        
        line = self.scene.addLine(x1, y1, x2, y2, QPen(QColor(180, 180, 180), 1))
        self.edge_items.append(line)

class NarrativeGraphWidget(QWidget):
    """
    Main widget for displaying narrative graph information.
    """
    
    # Signals
    refresh_requested = pyqtSignal()
    character_selected = pyqtSignal(str)  # character name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.graph_storage = None
        self._last_stats = {}
        self._last_text = ""  # Store last processed text for consistency checking
        self.scan_thread = None
        
        # Set minimum size for the widget
        self.setMinimumSize(400, 300)
        
        self.setupUI()
        self.setupTimer()
        
    def setupUI(self):
        """Set up the user interface."""
        # Set size policy to expand like other panels
        from PyQt5.QtWidgets import QSizePolicy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Title and status
        title_layout = QHBoxLayout()
        
        title_label = QLabel("Narrative Graph Memory")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        # Status indicator
        self.status_label = QLabel("Analyzing...")
        self.status_label.setStyleSheet("color: #666; font-size: 10px;")
        title_layout.addWidget(self.status_label)
        
        # Scan button to manually trigger content scanning
        self.scan_btn = QPushButton("Scan Content")
        self.scan_btn.setMaximumWidth(100)
        self.scan_btn.clicked.connect(self.scan_project_content)
        title_layout.addWidget(self.scan_btn)
        
        # Refresh button
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setMaximumWidth(80)
        self.refresh_btn.clicked.connect(self.refresh_data)
        title_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(title_layout)
        
        # Progress bar for analysis
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(10)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Main content tabs
        self.tab_widget = QTabWidget()
        self.setupTabs()
        layout.addWidget(self.tab_widget)
        
        # Stats footer
        self.stats_label = QLabel("No data available")
        self.stats_label.setStyleSheet("color: #888; font-size: 10px; padding: 5px;")
        layout.addWidget(self.stats_label)
        
    def setupTabs(self):
        """Set up the tab widgets."""
        # Characters tab
        self.characters_table = self.create_characters_table()
        self.tab_widget.addTab(self.characters_table, "Characters")
        
        # Locations tab
        self.locations_table = self.create_locations_table()
        self.tab_widget.addTab(self.locations_table, "Locations")
        
        # Relationships tab
        self.relationships_table = self.create_relationships_table()
        self.tab_widget.addTab(self.relationships_table, "Relationships")
        
        # Graph View tab
        self.graph_view = self.create_graph_view()
        self.tab_widget.addTab(self.graph_view, "Graph View")
        
        # Consistency tab
        self.consistency_widget = self.create_consistency_widget()
        self.tab_widget.addTab(self.consistency_widget, "Consistency")
        
    def create_characters_table(self):
        """Create the characters table."""
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Name", "Role", "Appearances", "Connections", "First Seen"])
        table.horizontalHeader().setStretchLastSection(False)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        # Connect double-click to open character in main window
        table.cellDoubleClicked.connect(self.on_character_double_clicked)
        return table
        
    def create_locations_table(self):
        """Create the locations table."""
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Location", "Type", "Mentions", "Description"])
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        # Connect double-click to open location in main window
        table.cellDoubleClicked.connect(self.on_location_double_clicked)
        return table
        
    def create_relationships_table(self):
        """Create the relationships table."""
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Source", "Target", "Type"])
        table.horizontalHeader().setStretchLastSection(True)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        return table
        
    def create_graph_view(self):
        """Create a visual graph view."""
        # Create interactive graph view
        self.graph_view = InteractiveGraphView()
        # Connect double-click to open character/location
        self.graph_view.nodeDoubleClicked.connect(self.on_graph_node_double_clicked)
        return self.graph_view
        
    def create_consistency_widget(self):
        """Create the consistency checking widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Instructions
        info_label = QLabel("Consistency checking helps identify potential issues in your narrative.")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Check button
        check_btn = QPushButton("Check Current Text")
        check_btn.clicked.connect(self.check_consistency)
        layout.addWidget(check_btn)
        
        # Results area
        self.consistency_results = QTextEdit()
        self.consistency_results.setReadOnly(True)
        layout.addWidget(self.consistency_results)
        
        return widget
        
    def setupTimer(self):
        """Set up auto-refresh timer."""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.auto_refresh)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
        
    def auto_refresh(self):
        """Auto-refresh the display if data has changed."""
        try:
            if self.graph_storage:
                current_stats = self.graph_storage.get_stats()
                if current_stats != self._last_stats:
                    self.refresh_data()
                    self._last_stats = current_stats
        except Exception as e:
            LOGGER.debug(f"Auto-refresh failed: {e}")
            
    def refresh_data(self):
        """Refresh all displayed data."""
        # Get the current graph storage/engine from the narrative_graph module
        from manuskript.ai.narrative_graph import narrative_graph
        
        # Prefer engine over storage
        if hasattr(narrative_graph, 'current_graph_engine') and narrative_graph.current_graph_engine:
            self.graph_engine = narrative_graph.current_graph_engine
            # Create a compatibility wrapper for the engine
            self._use_engine = True
            if not self.graph_engine:
                self.status_label.setText("No graph engine")
                return
        else:
            self.graph_storage = narrative_graph.current_graph_storage
            self._use_engine = False
            if not self.graph_storage:
                self.status_label.setText("No graph data")
                return
            
        try:
            # Update all tables
            self.update_characters_table()
            self.update_locations_table()
            self.update_relationships_table()
            
            # Update graph view and stats based on data source
            if self._use_engine:
                # Create a simple storage adapter for graph view
                stats = self.graph_engine.get_statistics()
                # Temporarily create a storage-like object for the graph view
                self.graph_view.update_graph(self.graph_storage if hasattr(self, 'graph_storage') else None)
            else:
                self.graph_view.update_graph(self.graph_storage)
                stats = self.graph_storage.get_stats()
            # Update stats display based on data source
            if self._use_engine:
                # Parse engine stats format
                total_entities = stats.get('total_entities', 0)
                total_relationships = stats.get('total_relationships', 0)
                entities_by_type = stats.get('entities_by_type', {})
                characters = entities_by_type.get('CHARACTER', 0)
                locations = entities_by_type.get('LOCATION', 0)
                self.stats_label.setText(
                    f"Characters: {characters} | "
                    f"Locations: {locations} | "
                    f"Relationships: {total_relationships}"
                )
            else:
                self.stats_label.setText(
                    f"Characters: {stats.get('characters', 0)} | "
                    f"Locations: {stats.get('locations', 0)} | "
                    f"Relationships: {stats.get('relationships', 0)}"
                )
            self.status_label.setText("Ready")
            
        except Exception as e:
            LOGGER.error(f"Failed to refresh data: {e}")
            self.status_label.setText("Error refreshing data")
    
    def update_characters_table(self):
        """Update the characters table."""
        if self._use_engine and not self.graph_engine:
            return
        if not self._use_engine and not self.graph_storage:
            return
            
        try:
            # Get character data
            characters = []
            
            if self._use_engine:
                # Use the new engine API
                from manuskript.ai.narrative_graph.graph_engine import EntityType
                char_entities = self.graph_engine.find_entities(entity_type=EntityType.CHARACTER)
                for entity in char_entities:
                    # Count connections (relationships)
                    connections = len(self.graph_engine.index.outgoing_edges.get(entity.id, [])) + \
                                 len(self.graph_engine.index.incoming_edges.get(entity.id, []))
                    appearances = entity.mention_count
                    characters.append((entity.name, appearances, connections))
            else:
                # Import NetworkX availability check
                from manuskript.ai.narrative_graph.narrative_graph import NETWORKX_AVAILABLE
                
                if NETWORKX_AVAILABLE and hasattr(self.graph_storage, 'graph'):
                    for node, data in self.graph_storage.graph.nodes(data=True):
                        if data.get('node_type') == 'character':
                            # Count connections
                            connections = self.graph_storage.graph.degree(node)
                            appearances = data.get('appearances', 1)
                            characters.append((node, appearances, connections))
            
            # Sort by connections (most connected first)
            characters.sort(key=lambda x: x[2], reverse=True)
            
            # Update table with new columns
            self.characters_table.setRowCount(len(characters))
            for i, (name, appearances, connections) in enumerate(characters):
                # Get additional character data based on data source
                if self._use_engine:
                    # Get entity data from engine
                    entity = next((e for e in char_entities if e.name == name), None)
                    if entity:
                        role = entity.attributes.get('role', 'Character')
                        first_seen = entity.attributes.get('first_seen', 'Unknown')
                    else:
                        role = 'Character'
                        first_seen = 'Unknown'
                else:
                    # Get data from graph storage
                    if hasattr(self.graph_storage, 'graph') and name in self.graph_storage.graph.nodes:
                        node_data = self.graph_storage.graph.nodes[name]
                        role = node_data.get('attributes', {}).get('role', 'Character')
                        first_seen = node_data.get('first_seen', 'Unknown')
                    else:
                        role = 'Character'
                        first_seen = 'Unknown'
                
                # Format date if needed
                if first_seen != 'Unknown' and 'T' in str(first_seen):
                    first_seen = first_seen.split('T')[0]  # Just the date part
                
                self.characters_table.setItem(i, 0, QTableWidgetItem(name))
                self.characters_table.setItem(i, 1, QTableWidgetItem(role))
                self.characters_table.setItem(i, 2, QTableWidgetItem(str(appearances)))
                self.characters_table.setItem(i, 3, QTableWidgetItem(str(connections)))
                self.characters_table.setItem(i, 4, QTableWidgetItem(str(first_seen)))
                
        except Exception as e:
            LOGGER.error(f"Failed to update characters table: {e}")
    
    def update_locations_table(self):
        """Update the locations table."""
        if not self.graph_storage:
            return
            
        try:
            # Get location data
            locations = []
            
            # Import NetworkX availability check
            from manuskript.ai.narrative_graph.narrative_graph import NETWORKX_AVAILABLE
            
            if NETWORKX_AVAILABLE and hasattr(self.graph_storage, 'graph'):
                for node, data in self.graph_storage.graph.nodes(data=True):
                    if data.get('node_type') == 'location':
                        mentions = data.get('mentions', 1)
                        locations.append((node, mentions))
            
            # Sort by mentions
            locations.sort(key=lambda x: x[1], reverse=True)
            
            # Update table with new columns
            self.locations_table.setRowCount(len(locations))
            for i, (name, mentions) in enumerate(locations):
                # Get additional location data
                node_data = self.graph_storage.graph.nodes[name]
                loc_type = node_data.get('location_type', 'Place')
                description = node_data.get('description', '')
                
                self.locations_table.setItem(i, 0, QTableWidgetItem(name))
                self.locations_table.setItem(i, 1, QTableWidgetItem(loc_type))
                self.locations_table.setItem(i, 2, QTableWidgetItem(str(mentions)))
                self.locations_table.setItem(i, 3, QTableWidgetItem(description))
                
        except Exception as e:
            LOGGER.error(f"Failed to update locations table: {e}")
    
    def update_relationships_table(self):
        """Update the relationships table."""
        if not self.graph_storage:
            return
            
        try:
            # Get relationships from the graph
            relationships = set()  # Use set to avoid duplicates
            
            # Import NetworkX availability check
            from manuskript.ai.narrative_graph.narrative_graph import NETWORKX_AVAILABLE
            
            if NETWORKX_AVAILABLE and hasattr(self.graph_storage, 'graph'):
                # Get edges with attributes
                for source, target, data in self.graph_storage.graph.edges(data=True):
                    rel_type = data.get('relationship', data.get('rel_type', 'connected'))
                    # Only show character-to-character relationships
                    source_data = self.graph_storage.graph.nodes.get(source, {})
                    target_data = self.graph_storage.graph.nodes.get(target, {})
                    if (source_data.get('node_type') == 'character' and 
                        target_data.get('node_type') == 'character'):
                        relationships.add((source, target, rel_type))
            
            # Convert to sorted list
            relationships = sorted(list(relationships))
            
            # Update table
            self.relationships_table.setRowCount(len(relationships))
            for i, (source, target, rel_type) in enumerate(relationships):
                self.relationships_table.setItem(i, 0, QTableWidgetItem(source))
                self.relationships_table.setItem(i, 1, QTableWidgetItem(target))
                self.relationships_table.setItem(i, 2, QTableWidgetItem(rel_type))
                
        except Exception as e:
            LOGGER.error(f"Failed to update relationships table: {e}")
    
    def scan_project_content(self):
        """Manually trigger a scan of all project content."""
        try:
            # Disable scan button during scan
            self.scan_btn.setEnabled(False)
            self.status_label.setText("Starting scan...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            # Create and start scan thread
            self.scan_thread = ScanThread(self)
            self.scan_thread.progress.connect(self.update_scan_progress)
            self.scan_thread.status.connect(self.update_scan_status)
            self.scan_thread.finished.connect(self.scan_complete)
            self.scan_thread.start()
                
        except Exception as e:
            LOGGER.error(f"Failed to start scan: {e}")
            self.status_label.setText(f"Scan failed: {str(e)[:50]}")
            self.scan_btn.setEnabled(True)
            self.progress_bar.setVisible(False)
    
    @pyqtSlot(int)
    def update_scan_progress(self, value):
        """Update progress bar during scan."""
        self.progress_bar.setValue(value)
    
    @pyqtSlot(str)
    def update_scan_status(self, status):
        """Update status label during scan."""
        self.status_label.setText(status)
    
    @pyqtSlot()
    def scan_complete(self):
        """Called when scan is complete."""
        self.scan_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Scan complete")
        # Refresh the display
        self.refresh_data()
    
    def check_consistency(self):
        """Check consistency of the current text."""
        try:
            from manuskript import functions as F
            
            # Get current text from editor
            main_window = F.mainWindow()
            if main_window and hasattr(main_window, 'mainEditor') and hasattr(main_window.mainEditor, 'currentEditor'):
                editor = main_window.mainEditor.currentEditor
                if editor:
                    current_text = editor.toPlainText()
                    
                    if current_text:
                        # Simple consistency checks based on graph data
                        if self.graph_storage:
                            result_text = "Consistency Analysis:\n\n"
                            
                            # Extract entities from current text
                            from manuskript.ai.narrative_graph.utils import extract_entities
                            entities = extract_entities(current_text)
                            
                            # Check for new characters not in graph
                            new_chars = []
                            for char in entities.get('characters', []):
                                if not self.graph_storage.graph.has_node(char):
                                    new_chars.append(char)
                            
                            if new_chars:
                                result_text += f"ℹ️ New characters detected: {', '.join(new_chars)}\n\n"
                            
                            # Check for new locations
                            new_locs = []
                            for loc in entities.get('locations', []):
                                if not self.graph_storage.graph.has_node(loc):
                                    new_locs.append(loc)
                            
                            if new_locs:
                                result_text += f"ℹ️ New locations detected: {', '.join(new_locs)}\n\n"
                            
                            # Count existing references
                            existing_chars = [c for c in entities.get('characters', []) if self.graph_storage.graph.has_node(c)]
                            existing_locs = [l for l in entities.get('locations', []) if self.graph_storage.graph.has_node(l)]
                            
                            if existing_chars:
                                result_text += f"✓ Referenced {len(existing_chars)} existing characters\n"
                            if existing_locs:
                                result_text += f"✓ Referenced {len(existing_locs)} existing locations\n"
                            
                            if not new_chars and not new_locs and not existing_chars and not existing_locs:
                                result_text += "No narrative entities detected in current text."
                            
                            self.consistency_results.setPlainText(result_text)
                        else:
                            self.consistency_results.setPlainText("No graph data available. Run 'Scan Content' first.")
                    else:
                        self.consistency_results.setPlainText("No text to check. Open a scene in the editor.")
                else:
                    self.consistency_results.setPlainText("No editor available.")
            else:
                self.consistency_results.setPlainText("Editor not available")
                
        except Exception as e:
            LOGGER.error(f"Failed to check consistency: {e}")
            self.consistency_results.setPlainText(f"Error checking consistency: {str(e)[:100]}")
    
    def set_graph_storage(self, storage):
        """Set the graph storage object."""
        self.graph_storage = storage
        self.refresh_data()
    
    def set_graph_engine(self, engine):
        """Set the graph engine object."""
        # Convert engine data to be compatible with graph_storage interface
        self.graph_engine = engine
        # Refresh the display
        self.refresh_data()
        
    def closeEvent(self, event):
        """Handle widget close event."""
        # Stop timer
        if hasattr(self, 'refresh_timer'):
            self.refresh_timer.stop()
        
        # Stop scan thread if running
        if self.scan_thread and self.scan_thread.isRunning():
            self.scan_thread.terminate()
            self.scan_thread.wait()
        
        super().closeEvent(event)
    
    def sizeHint(self):
        """Provide a reasonable default size for the widget."""
        return QSize(450, 600)
    
    def minimumSizeHint(self):
        """Provide minimum size for the widget."""
        return QSize(350, 400)
    
    def on_character_double_clicked(self, row, column, override_name=None):
        """Handle double-click on character table."""
        try:
            from manuskript import functions as F
            
            # Get character name from row or use override
            if override_name:
                character_name = override_name
            else:
                name_item = self.characters_table.item(row, 0)
                if not name_item:
                    return
                character_name = name_item.text()
            
            # Get main window and character model
            main_window = F.mainWindow()
            if main_window and hasattr(main_window, 'mdlCharacter'):
                # Find character in model
                for i in range(main_window.mdlCharacter.rowCount()):
                    char_index = main_window.mdlCharacter.index(i, 0)
                    if main_window.mdlCharacter.data(char_index) == character_name:
                        # Switch to character tab and select this character
                        main_window.tabMain.setCurrentIndex(2)  # Characters tab
                        main_window.lstCharacters.setCurrentIndex(char_index)
                        break
                else:
                    # Character not found in model, offer to create it
                    from PyQt5.QtWidgets import QMessageBox
                    reply = QMessageBox.question(self, 'Create Character',
                                                f"Character '{character_name}' not found in character list.\n"
                                                "Would you like to add it?",
                                                QMessageBox.Yes | QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        # Add character to model with default importance 0 (minor) and name
                        new_char = main_window.mdlCharacter.addCharacter(importance=0, name=character_name)
                        # Switch to character tab
                        main_window.tabMain.setCurrentIndex(2)
                        # Select the new character
                        if new_char:
                            item = main_window.lstCharacters.getItemByID(new_char.ID())
                            if item:
                                main_window.lstCharacters.setCurrentItem(item)
        except Exception as e:
            LOGGER.error(f"Failed to open character: {e}")
    
    def on_location_double_clicked(self, row, column, override_name=None):
        """Handle double-click on location table."""
        try:
            from manuskript import functions as F
            
            # Get location name from row or use override
            if override_name:
                location_name = override_name
            else:
                name_item = self.locations_table.item(row, 0)
                if not name_item:
                    return
                location_name = name_item.text()
            
            # Get main window and world model
            main_window = F.mainWindow()
            if main_window and hasattr(main_window, 'mdlWorld'):
                # Find location in world model
                def find_item(parent_item, name):
                    """Recursively find item in tree."""
                    for i in range(parent_item.rowCount()):
                        item = parent_item.child(i, 0)
                        if item.text() == name:
                            return item
                        # Check children
                        found = find_item(item, name)
                        if found:
                            return found
                    return None
                
                # Search in world model
                root_item = main_window.mdlWorld.invisibleRootItem()
                found_item = find_item(root_item, location_name)
                
                if found_item:
                    # Switch to world tab and select this location
                    main_window.tabMain.setCurrentIndex(3)  # World tab
                    index = main_window.mdlWorld.indexFromItem(found_item)
                    main_window.treeWorld.setCurrentIndex(index)
                else:
                    # Location not found, offer to create it
                    from PyQt5.QtWidgets import QMessageBox
                    reply = QMessageBox.question(self, 'Create Location',
                                                f"Location '{location_name}' not found in world.\n"
                                                "Would you like to add it?",
                                                QMessageBox.Yes | QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        # Add location to world model under Places
                        # Find or create Places category
                        places_item = find_item(root_item, "Places")
                        if not places_item:
                            # Create Places category
                            places_item = main_window.mdlWorld.addItem("Places")
                        
                        # Add location under Places
                        main_window.mdlWorld.addItem(location_name, parent=places_item)
                        # Switch to world tab
                        main_window.tabMain.setCurrentIndex(3)
        except Exception as e:
            LOGGER.error(f"Failed to open location: {e}")
    
    def on_graph_node_double_clicked(self, node_name, node_type):
        """Handle double-click on graph node."""
        if node_type == "character":
            # Simulate character table double-click
            self.on_character_double_clicked(0, 0, node_name)
        elif node_type == "location":
            # Simulate location table double-click
            self.on_location_double_clicked(0, 0, node_name)