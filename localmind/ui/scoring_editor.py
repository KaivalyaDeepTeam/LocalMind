"""
LocalMind Scoring Editor

Visual editor for configuring scoring parameters with drag-drop weight adjustment.
"""

from typing import Optional, List
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QComboBox, QLabel, QGroupBox, QSlider,
    QSpinBox, QDoubleSpinBox, QCheckBox, QLineEdit, QTextEdit,
    QDialogButtonBox, QMessageBox, QFileDialog, QInputDialog,
    QStyledItemDelegate, QStyleOptionViewItem, QAbstractItemView,
    QSplitter, QFrame, QToolBar,
)
from PySide6.QtCore import Qt, Signal, Slot, QModelIndex
from PySide6.QtGui import QColor, QPainter, QBrush, QAction

from localmind.config.scoring_parameters import (
    ScoringParameter, ScoringProfile, ParameterCategory,
    get_profile_manager, get_default_profile,
)


class WeightSliderDelegate(QStyledItemDelegate):
    """Custom delegate for weight slider in table."""

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        """Paint weight as a visual bar."""
        if index.column() == 3:  # Weight column
            weight = index.data(Qt.ItemDataRole.UserRole)
            if weight is not None:
                # Draw background
                painter.save()
                rect = option.rect.adjusted(2, 2, -2, -2)

                # Background
                painter.fillRect(rect, QColor(240, 240, 240))

                # Weight bar (max weight is 3.0)
                bar_width = int((weight / 3.0) * rect.width())
                bar_rect = rect.adjusted(0, 0, -(rect.width() - bar_width), 0)

                # Color based on weight
                if weight >= 2.0:
                    color = QColor(76, 175, 80)  # Green
                elif weight >= 1.0:
                    color = QColor(33, 150, 243)  # Blue
                else:
                    color = QColor(158, 158, 158)  # Gray

                painter.fillRect(bar_rect, color)

                # Draw text
                painter.setPen(Qt.GlobalColor.black)
                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, f"{weight:.1f}x")

                painter.restore()
                return

        super().paint(painter, option, index)


class ParameterEditWidget(QWidget):
    """Widget for editing a single parameter's details."""

    parameter_changed = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._parameter: Optional[ScoringParameter] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        layout = QVBoxLayout(self)

        # Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self._name_edit = QLineEdit()
        self._name_edit.setReadOnly(True)
        name_layout.addWidget(self._name_edit)
        layout.addLayout(name_layout)

        # Display Name
        display_layout = QHBoxLayout()
        display_layout.addWidget(QLabel("Display Name:"))
        self._display_edit = QLineEdit()
        self._display_edit.textChanged.connect(self._on_changed)
        display_layout.addWidget(self._display_edit)
        layout.addLayout(display_layout)

        # Description
        layout.addWidget(QLabel("Description:"))
        self._description_edit = QTextEdit()
        self._description_edit.setMaximumHeight(80)
        self._description_edit.textChanged.connect(self._on_changed)
        layout.addWidget(self._description_edit)

        # Max Score
        score_layout = QHBoxLayout()
        score_layout.addWidget(QLabel("Max Score:"))
        self._max_score_spin = QDoubleSpinBox()
        self._max_score_spin.setRange(1, 100)
        self._max_score_spin.setValue(10)
        self._max_score_spin.valueChanged.connect(self._on_changed)
        score_layout.addWidget(self._max_score_spin)
        score_layout.addStretch()
        layout.addLayout(score_layout)

        # Weight with slider
        weight_layout = QHBoxLayout()
        weight_layout.addWidget(QLabel("Weight:"))

        self._weight_slider = QSlider(Qt.Orientation.Horizontal)
        self._weight_slider.setRange(1, 30)  # 0.1 to 3.0
        self._weight_slider.setValue(10)
        self._weight_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._weight_slider.setTickInterval(5)  # Tick at 0.5x intervals
        self._weight_slider.setToolTip("Adjust parameter weight (0.1x to 3.0x)")
        self._weight_slider.valueChanged.connect(self._on_weight_slider_changed)
        weight_layout.addWidget(self._weight_slider)

        self._weight_label = QLabel("1.0x")
        self._weight_label.setMinimumWidth(40)
        weight_layout.addWidget(self._weight_label)

        layout.addLayout(weight_layout)

        # Weight scale labels
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel(""))  # Spacer for "Weight:" label alignment
        scale_layout.addWidget(QLabel("0.1x"))
        scale_layout.addStretch()
        mid_label = QLabel("1.5x")
        mid_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scale_layout.addWidget(mid_label)
        scale_layout.addStretch()
        scale_layout.addWidget(QLabel("3.0x"))
        scale_layout.addWidget(QLabel(""))  # Spacer for weight value alignment
        layout.addLayout(scale_layout)

        # Weight presets
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Presets:"))

        for weight, label in [(0.5, "Low"), (1.0, "Normal"), (1.5, "High"), (2.0, "Critical")]:
            btn = QPushButton(label)
            btn.setFixedWidth(60)
            btn.clicked.connect(lambda checked, w=weight: self._set_weight(w))
            preset_layout.addWidget(btn)

        preset_layout.addStretch()
        layout.addLayout(preset_layout)

        # Category
        cat_layout = QHBoxLayout()
        cat_layout.addWidget(QLabel("Category:"))
        self._category_combo = QComboBox()
        for cat in ParameterCategory:
            self._category_combo.addItem(cat.value.title(), cat)
        self._category_combo.currentIndexChanged.connect(self._on_changed)
        cat_layout.addWidget(self._category_combo)
        cat_layout.addStretch()
        layout.addLayout(cat_layout)

        # Enabled
        self._enabled_check = QCheckBox("Enabled")
        self._enabled_check.setChecked(True)
        self._enabled_check.stateChanged.connect(self._on_changed)
        layout.addWidget(self._enabled_check)

        layout.addStretch()

    def set_parameter(self, param: Optional[ScoringParameter]) -> None:
        """Set the parameter to edit."""
        self._parameter = param

        if param is None:
            self.setEnabled(False)
            return

        self.setEnabled(True)

        # Block signals during update
        self._name_edit.setText(param.name)
        self._display_edit.setText(param.display_name)
        self._description_edit.setPlainText(param.description)
        self._max_score_spin.setValue(param.max_score)
        self._weight_slider.setValue(int(param.weight * 10))
        self._weight_label.setText(f"{param.weight:.1f}x")
        self._enabled_check.setChecked(param.enabled)

        # Set category
        for i in range(self._category_combo.count()):
            if self._category_combo.itemData(i) == param.category:
                self._category_combo.setCurrentIndex(i)
                break

    def _set_weight(self, weight: float) -> None:
        """Set weight from preset."""
        self._weight_slider.setValue(int(weight * 10))

    @Slot()
    def _on_weight_slider_changed(self) -> None:
        """Handle weight slider change."""
        weight = self._weight_slider.value() / 10.0
        self._weight_label.setText(f"{weight:.1f}x")
        self._on_changed()

    @Slot()
    def _on_changed(self) -> None:
        """Handle any change."""
        if self._parameter is None:
            return

        self._parameter.display_name = self._display_edit.text()
        self._parameter.description = self._description_edit.toPlainText()
        self._parameter.max_score = self._max_score_spin.value()
        self._parameter.weight = self._weight_slider.value() / 10.0
        self._parameter.category = self._category_combo.currentData()
        self._parameter.enabled = self._enabled_check.isChecked()

        self.parameter_changed.emit()


class ScoringEditorDialog(QDialog):
    """Dialog for editing scoring parameters."""

    profile_saved = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._profile_manager = get_profile_manager()
        self._current_profile: Optional[ScoringProfile] = None
        self._modified = False

        self._setup_ui()
        self._load_profile_list()
        self._load_current_profile()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        self.setWindowTitle("Scoring Parameters Editor")
        self.setMinimumSize(900, 600)

        layout = QVBoxLayout(self)

        # Toolbar
        toolbar = QToolBar()
        toolbar.setMovable(False)

        # Profile selector
        toolbar.addWidget(QLabel("Profile: "))
        self._profile_combo = QComboBox()
        self._profile_combo.setMinimumWidth(150)
        self._profile_combo.currentTextChanged.connect(self._on_profile_selected)
        toolbar.addWidget(self._profile_combo)

        toolbar.addSeparator()

        # Profile actions
        new_action = QAction("New", self)
        new_action.triggered.connect(self._on_new_profile)
        toolbar.addAction(new_action)

        duplicate_action = QAction("Duplicate", self)
        duplicate_action.triggered.connect(self._on_duplicate_profile)
        toolbar.addAction(duplicate_action)

        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self._on_delete_profile)
        toolbar.addAction(delete_action)

        toolbar.addSeparator()

        import_action = QAction("Import", self)
        import_action.setToolTip("Import scoring profile from JSON file")
        import_action.triggered.connect(self._on_import_profile)
        toolbar.addAction(import_action)

        export_action = QAction("Export", self)
        export_action.setToolTip("Export scoring profile to JSON file")
        export_action.triggered.connect(self._on_export_profile)
        toolbar.addAction(export_action)

        format_help_action = QAction("Format Help", self)
        format_help_action.setToolTip("View JSON export format documentation")
        format_help_action.triggered.connect(self._on_show_format_help)
        toolbar.addAction(format_help_action)

        toolbar.addSeparator()

        reset_action = QAction("Reset to Default", self)
        reset_action.triggered.connect(self._on_reset_profile)
        toolbar.addAction(reset_action)

        layout.addWidget(toolbar)

        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Parameter table
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        left_layout.addWidget(QLabel("Parameters:"))

        self._param_table = QTableWidget()
        self._param_table.setColumnCount(5)
        self._param_table.setHorizontalHeaderLabels([
            "Enabled", "Name", "Category", "Weight", "Max"
        ])
        self._param_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._param_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._param_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._param_table.setItemDelegateForColumn(3, WeightSliderDelegate())
        self._param_table.itemSelectionChanged.connect(self._on_selection_changed)
        self._param_table.cellChanged.connect(self._on_cell_changed)
        left_layout.addWidget(self._param_table)

        # Add/Remove parameter buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Parameter")
        add_btn.clicked.connect(self._on_add_parameter)
        btn_layout.addWidget(add_btn)

        remove_btn = QPushButton("Remove Parameter")
        remove_btn.clicked.connect(self._on_remove_parameter)
        btn_layout.addWidget(remove_btn)

        btn_layout.addStretch()
        left_layout.addLayout(btn_layout)

        splitter.addWidget(left_widget)

        # Right: Parameter editor
        right_widget = QGroupBox("Parameter Details")
        right_layout = QVBoxLayout(right_widget)

        self._param_editor = ParameterEditWidget()
        self._param_editor.parameter_changed.connect(self._on_parameter_changed)
        self._param_editor.setEnabled(False)
        right_layout.addWidget(self._param_editor)

        splitter.addWidget(right_widget)
        splitter.setSizes([500, 400])

        layout.addWidget(splitter)

        # Summary
        summary_frame = QFrame()
        summary_frame.setFrameShape(QFrame.Shape.StyledPanel)
        summary_layout = QHBoxLayout(summary_frame)

        self._total_weight_label = QLabel("Total Weight: 0.0")
        summary_layout.addWidget(self._total_weight_label)

        self._max_score_label = QLabel("Max Possible Score: 0.0")
        summary_layout.addWidget(self._max_score_label)

        self._param_count_label = QLabel("Parameters: 0 enabled")
        summary_layout.addWidget(self._param_count_label)

        summary_layout.addStretch()

        layout.addWidget(summary_frame)

        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._on_save)
        button_box.rejected.connect(self._on_cancel)
        layout.addWidget(button_box)

    def _load_profile_list(self) -> None:
        """Load the list of available profiles."""
        self._profile_combo.clear()
        profiles = self._profile_manager.list_profiles()
        for profile in profiles:
            self._profile_combo.addItem(profile.replace("_", " ").title())

    def _load_current_profile(self) -> None:
        """Load the current profile."""
        try:
            self._current_profile = self._profile_manager.get_current_profile()
        except Exception:
            self._current_profile = get_default_profile()

        self._update_table()
        self._update_summary()
        self._modified = False

    def _update_table(self) -> None:
        """Update the parameter table."""
        self._param_table.blockSignals(True)
        self._param_table.setRowCount(0)

        if self._current_profile is None:
            self._param_table.blockSignals(False)
            return

        for param in self._current_profile.parameters:
            row = self._param_table.rowCount()
            self._param_table.insertRow(row)

            # Enabled checkbox
            enabled_item = QTableWidgetItem()
            enabled_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            enabled_item.setCheckState(
                Qt.CheckState.Checked if param.enabled else Qt.CheckState.Unchecked
            )
            self._param_table.setItem(row, 0, enabled_item)

            # Name
            name_item = QTableWidgetItem(param.display_name)
            name_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self._param_table.setItem(row, 1, name_item)

            # Category
            cat_item = QTableWidgetItem(param.category.value.title())
            cat_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self._param_table.setItem(row, 2, cat_item)

            # Weight (with visual)
            weight_item = QTableWidgetItem()
            weight_item.setData(Qt.ItemDataRole.UserRole, param.weight)
            weight_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self._param_table.setItem(row, 3, weight_item)

            # Max Score
            max_item = QTableWidgetItem(str(param.max_score))
            max_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self._param_table.setItem(row, 4, max_item)

        self._param_table.blockSignals(False)

    def _update_summary(self) -> None:
        """Update the summary labels."""
        if self._current_profile is None:
            return

        enabled = self._current_profile.get_enabled_parameters()
        total_weight = self._current_profile.get_total_weight()
        max_score = self._current_profile.get_max_possible_score()

        self._total_weight_label.setText(f"Total Weight: {total_weight:.1f}")
        self._max_score_label.setText(f"Max Possible Score: {max_score:.1f}")
        self._param_count_label.setText(f"Parameters: {len(enabled)} enabled")

    @Slot()
    def _on_profile_selected(self) -> None:
        """Handle profile selection."""
        if self._modified:
            result = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Discard them?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if result == QMessageBox.StandardButton.No:
                return

        profile_name = self._profile_combo.currentText().lower().replace(" ", "_")
        try:
            self._current_profile = self._profile_manager.load_profile(profile_name)
            self._update_table()
            self._update_summary()
            self._modified = False
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load profile: {e}")

    @Slot()
    def _on_selection_changed(self) -> None:
        """Handle table selection change."""
        rows = self._param_table.selectionModel().selectedRows()
        if rows and self._current_profile:
            row = rows[0].row()
            if row < len(self._current_profile.parameters):
                param = self._current_profile.parameters[row]
                self._param_editor.set_parameter(param)
        else:
            self._param_editor.set_parameter(None)

    @Slot()
    def _on_cell_changed(self) -> None:
        """Handle cell change (enabled checkbox)."""
        row = self._param_table.currentRow()
        if row >= 0 and self._current_profile:
            enabled_item = self._param_table.item(row, 0)
            if enabled_item:
                self._current_profile.parameters[row].enabled = (
                    enabled_item.checkState() == Qt.CheckState.Checked
                )
                self._modified = True
                self._update_summary()

    @Slot()
    def _on_parameter_changed(self) -> None:
        """Handle parameter edit."""
        self._modified = True
        self._update_table()
        self._update_summary()

    @Slot()
    def _on_add_parameter(self) -> None:
        """Add a new parameter."""
        if self._current_profile is None:
            return

        name, ok = QInputDialog.getText(self, "New Parameter", "Parameter name:")
        if ok and name:
            param = ScoringParameter(
                name=name.lower().replace(" ", "_"),
                display_name=name,
                description="",
            )
            self._current_profile.parameters.append(param)
            self._modified = True
            self._update_table()
            self._update_summary()

    @Slot()
    def _on_remove_parameter(self) -> None:
        """Remove selected parameter."""
        rows = self._param_table.selectionModel().selectedRows()
        if not rows or self._current_profile is None:
            return

        row = rows[0].row()
        if row < len(self._current_profile.parameters):
            del self._current_profile.parameters[row]
            self._modified = True
            self._update_table()
            self._update_summary()
            self._param_editor.set_parameter(None)

    @Slot()
    def _on_new_profile(self) -> None:
        """Create a new profile."""
        name, ok = QInputDialog.getText(self, "New Profile", "Profile name:")
        if ok and name:
            from datetime import datetime
            now = datetime.now().isoformat()

            self._current_profile = ScoringProfile(
                name=name,
                description="",
                parameters=[],
                created_at=now,
                modified_at=now,
            )
            self._profile_manager.save_profile(self._current_profile)
            self._load_profile_list()

            # Select the new profile
            for i in range(self._profile_combo.count()):
                if self._profile_combo.itemText(i).lower().replace(" ", "_") == name.lower().replace(" ", "_"):
                    self._profile_combo.setCurrentIndex(i)
                    break

            self._update_table()
            self._update_summary()

    @Slot()
    def _on_duplicate_profile(self) -> None:
        """Duplicate current profile."""
        if self._current_profile is None:
            return

        name, ok = QInputDialog.getText(
            self, "Duplicate Profile",
            "New profile name:",
            text=f"{self._current_profile.name} Copy"
        )
        if ok and name:
            source_name = self._current_profile.name.lower().replace(" ", "_")
            self._profile_manager.duplicate_profile(source_name, name)
            self._load_profile_list()

    @Slot()
    def _on_delete_profile(self) -> None:
        """Delete current profile."""
        if self._current_profile is None:
            return

        if self._current_profile.name.lower() == "default":
            QMessageBox.warning(self, "Cannot Delete", "Cannot delete the default profile.")
            return

        result = QMessageBox.question(
            self, "Delete Profile",
            f"Delete profile '{self._current_profile.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if result == QMessageBox.StandardButton.Yes:
            name = self._current_profile.name.lower().replace(" ", "_")
            self._profile_manager.delete_profile(name)
            self._load_profile_list()
            self._load_current_profile()

    @Slot()
    def _on_import_profile(self) -> None:
        """Import a profile from file."""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Import Profile", str(Path.home()),
            "JSON Files (*.json)"
        )
        if filepath:
            try:
                self._profile_manager.import_profile(Path(filepath))
                self._load_profile_list()
                QMessageBox.information(self, "Success", "Profile imported successfully.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to import: {e}")

    @Slot()
    def _on_export_profile(self) -> None:
        """Export current profile to file."""
        if self._current_profile is None:
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Profile",
            str(Path.home() / f"{self._current_profile.name}.json"),
            "JSON Files (*.json)"
        )
        if filepath:
            try:
                name = self._current_profile.name.lower().replace(" ", "_")
                self._profile_manager.export_profile(name, Path(filepath))
                QMessageBox.information(self, "Success", "Profile exported successfully.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to export: {e}")

    @Slot()
    def _on_show_format_help(self) -> None:
        """Show JSON export format documentation."""
        help_text = """
        <h3>Scoring Profile JSON Format</h3>

        <p>Scoring profiles are exported as JSON files with the following structure:</p>

        <pre style="background: #f5f5f5; padding: 10px; font-family: monospace; font-size: 11px;">
{
  "name": "my_profile",
  "description": "Custom scoring profile",
  "parameters": [
    {
      "name": "greeting",
      "display_name": "Greeting",
      "description": "Agent greets customer properly",
      "category": "compliance",
      "max_score": 10.0,
      "weight": 1.5,
      "enabled": true
    }
  ]
}
        </pre>

        <h4>Field Descriptions:</h4>
        <ul>
            <li><b>name</b>: Internal identifier (lowercase, underscores)</li>
            <li><b>display_name</b>: Human-readable name shown in UI</li>
            <li><b>description</b>: What this parameter measures</li>
            <li><b>category</b>: "compliance", "quality", "communication", or "custom"</li>
            <li><b>max_score</b>: Maximum points (typically 10)</li>
            <li><b>weight</b>: Importance multiplier (0.1 to 3.0)</li>
            <li><b>enabled</b>: Whether to include in scoring</li>
        </ul>

        <h4>Tips:</h4>
        <ul>
            <li>Higher weight = more impact on final score</li>
            <li>Disabled parameters are saved but not used</li>
            <li>Categories help organize parameters in reports</li>
        </ul>
        """
        QMessageBox.information(self, "Export Format Help", help_text)

    @Slot()
    def _on_reset_profile(self) -> None:
        """Reset profile to default values."""
        result = QMessageBox.question(
            self, "Reset Profile",
            "Reset all parameters to default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if result == QMessageBox.StandardButton.Yes:
            self._current_profile = self._profile_manager.reset_to_default()
            self._update_table()
            self._update_summary()
            self._modified = False

    @Slot()
    def _on_save(self) -> None:
        """Save the current profile."""
        if self._current_profile:
            self._profile_manager.save_profile(self._current_profile)
            self.profile_saved.emit(self._current_profile.name)
            self._modified = False
        self.accept()

    @Slot()
    def _on_cancel(self) -> None:
        """Cancel and close."""
        if self._modified:
            result = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Discard them?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if result == QMessageBox.StandardButton.No:
                return

        self.reject()

    def get_current_parameters(self) -> List[dict]:
        """Get current parameters as list of dicts for audit worker."""
        if self._current_profile is None:
            return []

        return [
            {
                "name": p.name,
                "max_score": p.max_score,
                "weight": p.weight,
                "description": p.description,
            }
            for p in self._current_profile.get_enabled_parameters()
        ]
