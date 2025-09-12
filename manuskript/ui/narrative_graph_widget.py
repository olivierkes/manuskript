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
                            QHeaderView, QAbstractItemView, QMessageBox, QDockWidget)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot, QSize
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon

from manuskript import settings
import logging
from typing import Dict, List, Optional, Any

LOGGER = logging.getLogger(__name__)

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
        
        self.setupUI()
        self.setupTimer()
        
    def setupUI(self):
        """Set up the user interface."""
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
        
        # Refresh button
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setMaximumWidth(80)
        self.refresh_btn.clicked.connect(self.refresh_data)
        title_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(title_layout)
        
        # Progress bar for analysis
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(4)
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
        """Set up the tabbed interface."""
        
        # Tab 1: Character Overview
        self.characters_tab = self.create_characters_tab()
        self.tab_widget.addTab(self.characters_tab, "Characters")
        
        # Tab 2: Relationships
        self.relationships_tab = self.create_relationships_tab()
        self.tab_widget.addTab(self.relationships_tab, "Relationships")
        
        # Tab 3: Plot Events
        self.events_tab = self.create_events_tab()
        self.tab_widget.addTab(self.events_tab, "Events")
        
        # Tab 4: Consistency Check
        self.consistency_tab = self.create_consistency_tab()
        self.tab_widget.addTab(self.consistency_tab, "Consistency")
        
        # Tab 5: Graph Visualization (if available)
        try:
            import matplotlib
            self.viz_tab = self.create_visualization_tab()
            self.tab_widget.addTab(self.viz_tab, "Graph View")
        except ImportError:
            # Add a placeholder tab
            placeholder = QLabel("Graph visualization requires matplotlib.\nInstall with: pip install matplotlib")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet("color: #888; padding: 20px;")
            self.tab_widget.addTab(placeholder, "Graph View")
    
    def create_characters_tab(self):
        """Create the characters overview tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Characters table
        self.characters_table = QTableWidget()
        self.characters_table.setColumnCount(4)
        self.characters_table.setHorizontalHeaderLabels(["Name", "Importance", "Relationships", "First Seen"])
        
        # Make table read-only and selectable
        self.characters_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.characters_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.characters_table.itemSelectionChanged.connect(self.on_character_selected)
        
        # Auto-resize columns
        header = self.characters_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.characters_table)
        
        # Character details panel
        details_group = QGroupBox("Character Details")
        details_layout = QVBoxLayout(details_group)
        
        self.character_details = QTextEdit()
        self.character_details.setMaximumHeight(120)
        self.character_details.setPlaceholderText("Select a character to see details...")
        details_layout.addWidget(self.character_details)
        
        layout.addWidget(details_group)
        
        return widget
    
    def create_relationships_tab(self):
        """Create the relationships tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Relationships table
        self.relationships_table = QTableWidget()
        self.relationships_table.setColumnCount(3)
        self.relationships_table.setHorizontalHeaderLabels(["From", "Relationship", "To"])
        
        self.relationships_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.relationships_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        # Auto-resize columns
        header = self.relationships_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.relationships_table)
        
        # Relationship strength visualization
        strength_group = QGroupBox("Relationship Strength")
        strength_layout = QVBoxLayout(strength_group)
        
        self.relationship_details = QTextEdit()
        self.relationship_details.setMaximumHeight(100)
        self.relationship_details.setPlaceholderText("Relationship analysis will appear here...")
        strength_layout.addWidget(self.relationship_details)
        
        layout.addWidget(strength_group)
        
        return widget
    
    def create_events_tab(self):
        """Create the plot events tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Events tree
        self.events_tree = QTreeWidget()
        self.events_tree.setHeaderLabels(["Event", "Type", "Participants", "Context"])
        self.events_tree.setAlternatingRowColors(True)
        
        layout.addWidget(self.events_tree)
        
        # Event timeline info
        timeline_group = QGroupBox("Timeline Analysis")
        timeline_layout = QVBoxLayout(timeline_group)
        
        self.timeline_info = QTextEdit()
        self.timeline_info.setMaximumHeight(80)
        self.timeline_info.setPlaceholderText("Plot progression analysis...")
        timeline_layout.addWidget(self.timeline_info)
        
        layout.addWidget(timeline_group)
        
        return widget
    
    def create_consistency_tab(self):
        """Create the consistency checker tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Consistency check controls
        controls_layout = QHBoxLayout()
        
        self.check_btn = QPushButton("Run Consistency Check")
        self.check_btn.clicked.connect(self.run_consistency_check)
        controls_layout.addWidget(self.check_btn)
        
        controls_layout.addStretch()
        
        self.check_status = QLabel("Ready")
        self.check_status.setStyleSheet("color: #666;")
        controls_layout.addWidget(self.check_status)
        
        layout.addLayout(controls_layout)
        
        # Issues table
        self.issues_table = QTableWidget()
        self.issues_table.setColumnCount(3)
        self.issues_table.setHorizontalHeaderLabels(["Severity", "Issue", "Suggestion"])
        
        self.issues_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # Auto-resize columns
        header = self.issues_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        
        layout.addWidget(self.issues_table)
        
        return widget
    
    def create_visualization_tab(self):
        """Create the graph visualization tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.layout_btn = QPushButton("Spring Layout")
        self.layout_btn.clicked.connect(self.update_graph_layout)
        controls_layout.addWidget(self.layout_btn)
        
        self.filter_btn = QPushButton("Filter Nodes")
        controls_layout.addWidget(self.filter_btn)
        
        controls_layout.addStretch()
        
        self.zoom_label = QLabel("Zoom: 100%")
        controls_layout.addWidget(self.zoom_label)
        
        layout.addLayout(controls_layout)
        
        # Try to create matplotlib canvas
        try:
            from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
            from matplotlib.figure import Figure
            
            self.graph_figure = Figure(figsize=(8, 6))
            self.graph_canvas = FigureCanvas(self.graph_figure)
            self.graph_axes = self.graph_figure.add_subplot(111)
            layout.addWidget(self.graph_canvas)
            
            # Initial empty plot
            self.graph_axes.text(0.5, 0.5, 'No graph data to display\nAnalyze some text to see the narrative graph',
                               ha='center', va='center', transform=self.graph_axes.transAxes,
                               fontsize=12, color='gray')
            self.graph_axes.set_xticks([])
            self.graph_axes.set_yticks([])
            self.graph_figure.tight_layout()
            
        except ImportError:
            # Fallback to simple label
            self.graph_canvas = QLabel("Graph visualization requires matplotlib.\nInstall with: pip install matplotlib")
            self.graph_canvas.setAlignment(Qt.AlignCenter)
            self.graph_canvas.setStyleSheet("border: 1px solid #ccc; background: white; min-height: 300px;")
            layout.addWidget(self.graph_canvas)
            self.graph_figure = None
            self.graph_axes = None
        
        return widget
    
    def setupTimer(self):
        """Set up automatic refresh timer."""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(5000)  # Refresh every 5 seconds
    
    def set_graph_storage(self, storage):
        """Set the graph storage instance."""
        self.graph_storage = storage
        self.refresh_data()
    
    def set_last_text(self, text):
        """Store the last processed text for consistency checking."""
        self._last_text = text
    
    def refresh_data(self):
        """Refresh all displayed data."""
        if not self.graph_storage:
            self.status_label.setText("No graph data")
            return
        
        try:
            # Check if feature is enabled
            if not settings.aiFeatures.get("narrativeGraphMemory", False):
                self.status_label.setText("Feature disabled")
                self.clear_all_data()
                return
            
            self.status_label.setText("Refreshing...")
            
            # Get current stats
            stats = self.graph_storage.get_stats()
            session_info = self.graph_storage.get_session_info()
            
            # Update stats display
            stats_text = f"Nodes: {stats.get('total_nodes', 0)} | "
            stats_text += f"Characters: {stats.get('characters', 0)} | "
            stats_text += f"Events: {stats.get('events', 0)} | "
            stats_text += f"Changes: {session_info.get('changes_since_save', 0)}"
            self.stats_label.setText(stats_text)
            
            # Update individual tabs
            self.update_characters_tab()
            self.update_relationships_tab()
            self.update_events_tab()
            
            # Update visualization if available
            if hasattr(self, 'graph_figure') and self.graph_figure:
                self.update_graph_layout()
            
            self.status_label.setText("Ready")
            
        except Exception as e:
            LOGGER.error(f"Failed to refresh graph data: {e}")
            self.status_label.setText(f"Error: {str(e)}")
    
    def clear_all_data(self):
        """Clear all displayed data."""
        self.characters_table.setRowCount(0)
        self.relationships_table.setRowCount(0)
        self.events_tree.clear()
        self.issues_table.setRowCount(0)
        self.character_details.clear()
        self.relationship_details.clear()
        self.timeline_info.clear()
    
    def update_characters_tab(self):
        """Update the characters tab with current data."""
        if not self.graph_storage:
            return
        
        try:
            # Get character data from graph
            characters_data = self.get_characters_data()
            
            self.characters_table.setRowCount(len(characters_data))
            
            for row, (name, data) in enumerate(characters_data.items()):
                # Name
                self.characters_table.setItem(row, 0, QTableWidgetItem(name))
                
                # Importance (based on centrality if available)
                importance = data.get('importance', 'Unknown')
                self.characters_table.setItem(row, 1, QTableWidgetItem(str(importance)))
                
                # Relationship count
                rel_count = data.get('relationships', 0)
                self.characters_table.setItem(row, 2, QTableWidgetItem(str(rel_count)))
                
                # First seen
                first_seen = data.get('first_seen', 'Unknown')
                self.characters_table.setItem(row, 3, QTableWidgetItem(first_seen))
                
        except Exception as e:
            LOGGER.error(f"Failed to update characters tab: {e}")
    
    def update_relationships_tab(self):
        """Update the relationships tab."""
        if not self.graph_storage:
            return
        
        try:
            relationships = self.get_relationships_data()
            
            self.relationships_table.setRowCount(len(relationships))
            
            for row, rel in enumerate(relationships):
                self.relationships_table.setItem(row, 0, QTableWidgetItem(rel.get('source', '')))
                self.relationships_table.setItem(row, 1, QTableWidgetItem(rel.get('type', '')))
                self.relationships_table.setItem(row, 2, QTableWidgetItem(rel.get('target', '')))
                
        except Exception as e:
            LOGGER.error(f"Failed to update relationships tab: {e}")
    
    def update_events_tab(self):
        """Update the events tab."""
        if not self.graph_storage:
            return
        
        try:
            self.events_tree.clear()
            
            events = self.get_events_data()
            
            for event in events:
                item = QTreeWidgetItem([
                    event.get('name', 'Unknown Event'),
                    event.get('type', 'Unknown'),
                    ', '.join(event.get('participants', [])),
                    event.get('description', '')[:50] + '...' if len(event.get('description', '')) > 50 else event.get('description', '')
                ])
                self.events_tree.addTopLevelItem(item)
                
        except Exception as e:
            LOGGER.error(f"Failed to update events tab: {e}")
    
    def get_characters_data(self):
        """Extract character data from graph."""
        if not self.graph_storage:
            return {}
        
        try:
            # Get NetworkX graph or fallback storage
            if hasattr(self.graph_storage, 'graph'):
                graph = self.graph_storage.graph
                characters = {}
                
                if hasattr(graph, 'nodes'):
                    # NetworkX graph
                    for node, data in graph.nodes(data=True):
                        if data.get('node_type') == 'character':
                            characters[node] = {
                                'importance': data.get('importance', 'Unknown'),
                                'relationships': len(list(graph.neighbors(node))),
                                'first_seen': data.get('first_seen', 'Unknown')
                            }
                else:
                    # Dict-based fallback
                    nodes = graph.get('nodes', {})
                    for node_id, node_data in nodes.items():
                        if node_data.get('node_type') == 'character':
                            characters[node_id] = {
                                'importance': node_data.get('importance', 'Unknown'),
                                'relationships': len(node_data.get('edges', [])),
                                'first_seen': node_data.get('first_seen', 'Unknown')
                            }
                
                return characters
            else:
                return {}
        except Exception as e:
            LOGGER.error(f"Failed to get characters data: {e}")
            return {}
    
    def get_relationships_data(self):
        """Extract relationship data from graph."""
        if not self.graph_storage:
            return []
        
        try:
            relationships = []
            if hasattr(self.graph_storage, 'graph'):
                graph = self.graph_storage.graph
                
                if hasattr(graph, 'edges'):
                    # NetworkX graph
                    for source, target, data in graph.edges(data=True):
                        relationships.append({
                            'source': source,
                            'type': data.get('relationship_type', 'unknown'),
                            'target': target
                        })
                else:
                    # Dict-based fallback
                    edges = graph.get('edges', [])
                    for edge in edges:
                        relationships.append({
                            'source': edge.get('source', ''),
                            'type': edge.get('type', 'unknown'),
                            'target': edge.get('target', '')
                        })
            
            return relationships
        except Exception as e:
            LOGGER.error(f"Failed to get relationships data: {e}")
            return []
    
    def get_events_data(self):
        """Extract event data from graph."""
        if not self.graph_storage:
            return []
        
        try:
            events = []
            if hasattr(self.graph_storage, 'graph'):
                graph = self.graph_storage.graph
                
                if hasattr(graph, 'nodes'):
                    # NetworkX graph
                    for node, data in graph.nodes(data=True):
                        if data.get('node_type') == 'event':
                            events.append({
                                'name': node,
                                'type': data.get('event_type', 'unknown'),
                                'participants': data.get('participants', []),
                                'description': data.get('description', '')
                            })
                else:
                    # Dict-based fallback
                    nodes = graph.get('nodes', {})
                    for node_id, node_data in nodes.items():
                        if node_data.get('node_type') == 'event':
                            events.append({
                                'name': node_id,
                                'type': node_data.get('event_type', 'unknown'),
                                'participants': node_data.get('participants', []),
                                'description': node_data.get('description', '')
                            })
            
            return events
        except Exception as e:
            LOGGER.error(f"Failed to get events data: {e}")
            return []
    
    @pyqtSlot()
    def on_character_selected(self):
        """Handle character selection in table."""
        current_row = self.characters_table.currentRow()
        if current_row >= 0:
            char_name = self.characters_table.item(current_row, 0).text()
            self.character_selected.emit(char_name)
            
            # Update details panel
            details = f"Character: {char_name}\n"
            details += "Relationships: Loading...\n"
            details += "Character arc: Analysis in progress..."
            self.character_details.setText(details)
    
    @pyqtSlot()
    def run_consistency_check(self):
        """Run consistency check on the narrative."""
        self.check_status.setText("Checking...")
        self.check_btn.setEnabled(False)
        
        try:
            # Call the actual consistency checker
            if self.graph_storage:
                from manuskript.ai.narrative_graph.narrative_graph import suggest_consistency_check
                # Use the last processed text or a default
                text_to_check = self._last_text if self._last_text else "Sample text with characters Alice and Bob."
                issues = suggest_consistency_check(text_to_check)
                
                # Convert to expected format
                formatted_issues = []
                for issue in issues:
                    formatted_issues.append({
                        "severity": issue.get('type', 'info').title(),
                        "issue": issue.get('message', ''),
                        "suggestion": "Review the flagged content for potential issues"
                    })
                issues = formatted_issues
            else:
                issues = [{"severity": "Info", "issue": "No graph data available", "suggestion": "Enable AI features and analyze some text first"}]
            
            self.issues_table.setRowCount(len(issues))
            
            for row, issue in enumerate(issues):
                # Color-code severity
                severity_item = QTableWidgetItem(issue['severity'])
                if issue['severity'] == 'Warning':
                    severity_item.setBackground(QColor(255, 255, 0, 50))
                elif issue['severity'] == 'Error':
                    severity_item.setBackground(QColor(255, 0, 0, 50))
                
                self.issues_table.setItem(row, 0, severity_item)
                self.issues_table.setItem(row, 1, QTableWidgetItem(issue['issue']))
                self.issues_table.setItem(row, 2, QTableWidgetItem(issue['suggestion']))
            
            self.check_status.setText(f"Found {len(issues)} issues")
            
        except Exception as e:
            LOGGER.error(f"Consistency check failed: {e}")
            self.check_status.setText("Check failed")
        
        finally:
            self.check_btn.setEnabled(True)
    
    @pyqtSlot()
    def update_graph_layout(self):
        """Update the graph visualization layout."""
        if not self.graph_figure or not self.graph_axes:
            return
        
        self.status_label.setText("Updating layout...")
        
        try:
            # Clear the previous plot
            self.graph_axes.clear()
            
            if not self.graph_storage:
                self.graph_axes.text(0.5, 0.5, 'No graph storage available',
                                   ha='center', va='center', transform=self.graph_axes.transAxes,
                                   fontsize=12, color='gray')
                self.graph_figure.canvas.draw()
                self.status_label.setText("Ready")
                return
            
            # Try to plot the NetworkX graph
            try:
                import networkx as nx
                import matplotlib.pyplot as plt
                
                if hasattr(self.graph_storage, 'graph') and hasattr(self.graph_storage.graph, 'nodes'):
                    G = self.graph_storage.graph
                    
                    if len(G.nodes()) == 0:
                        self.graph_axes.text(0.5, 0.5, 'Graph is empty\nAnalyze some text to populate it',
                                           ha='center', va='center', transform=self.graph_axes.transAxes,
                                           fontsize=12, color='gray')
                    else:
                        # Create layout
                        pos = nx.spring_layout(G, k=1, iterations=50)
                        
                        # Draw nodes with different colors for different types
                        character_nodes = [n for n, d in G.nodes(data=True) if d.get('node_type') == 'character']
                        location_nodes = [n for n, d in G.nodes(data=True) if d.get('node_type') == 'location']
                        event_nodes = [n for n, d in G.nodes(data=True) if d.get('node_type') == 'event']
                        
                        if character_nodes:
                            nx.draw_networkx_nodes(G, pos, nodelist=character_nodes, 
                                                 node_color='lightblue', node_size=300, 
                                                 ax=self.graph_axes, alpha=0.8)
                        if location_nodes:
                            nx.draw_networkx_nodes(G, pos, nodelist=location_nodes,
                                                 node_color='lightgreen', node_size=200,
                                                 ax=self.graph_axes, alpha=0.8)
                        if event_nodes:
                            nx.draw_networkx_nodes(G, pos, nodelist=event_nodes,
                                                 node_color='lightcoral', node_size=250,
                                                 ax=self.graph_axes, alpha=0.8)
                        
                        # Draw edges
                        nx.draw_networkx_edges(G, pos, ax=self.graph_axes, alpha=0.5, width=1)
                        
                        # Draw labels
                        nx.draw_networkx_labels(G, pos, ax=self.graph_axes, font_size=8)
                        
                        self.graph_axes.set_title("Narrative Graph Visualization")
                        
                        # Add legend
                        from matplotlib.patches import Patch
                        legend_elements = [
                            Patch(facecolor='lightblue', label='Characters'),
                            Patch(facecolor='lightgreen', label='Locations'),
                            Patch(facecolor='lightcoral', label='Events')
                        ]
                        self.graph_axes.legend(handles=legend_elements, loc='upper right')
                        
                else:
                    self.graph_axes.text(0.5, 0.5, 'NetworkX graph not available\nUsing fallback storage',
                                       ha='center', va='center', transform=self.graph_axes.transAxes,
                                       fontsize=12, color='gray')
                
            except ImportError:
                self.graph_axes.text(0.5, 0.5, 'NetworkX required for graph visualization\nInstall with: pip install networkx',
                                   ha='center', va='center', transform=self.graph_axes.transAxes,
                                   fontsize=12, color='gray')
            
            self.graph_axes.set_xticks([])
            self.graph_axes.set_yticks([])
            self.graph_figure.tight_layout()
            self.graph_figure.canvas.draw()
            
        except Exception as e:
            LOGGER.error(f"Failed to update graph layout: {e}")
            self.graph_axes.text(0.5, 0.5, f'Error creating visualization:\n{str(e)}',
                               ha='center', va='center', transform=self.graph_axes.transAxes,
                               fontsize=10, color='red')
            self.graph_figure.canvas.draw()
        
        self.status_label.setText("Ready")
    
    def showEvent(self, event):
        """Handle widget show event."""
        super().showEvent(event)
        self.refresh_data()
    
    def closeEvent(self, event):
        """Handle widget close event."""
        if self.refresh_timer:
            self.refresh_timer.stop()
        super().closeEvent(event)