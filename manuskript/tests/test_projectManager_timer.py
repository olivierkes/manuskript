import unittest
from unittest.mock import MagicMock, patch, ANY
from PyQt5.QtCore import QTimer, QObject
from manuskript.projectManager import ProjectManager

class TestProjectManagerTimer(unittest.TestCase):

    def setUp(self):
        self.window = MagicMock()
        self.window.tr = lambda x: x

        # Create separate mocks for each timer instance
        self.mock_save_timer = MagicMock()
        self.mock_save_timer.timeout = MagicMock()
        self.mock_save_timer_no_changes = MagicMock()
        self.mock_save_timer_no_changes.timeout = MagicMock()
        
        # Mock QTimer to return different instances for each call
        self.timer_instances = [self.mock_save_timer, self.mock_save_timer_no_changes]
        self.timer_call_count = 0
        
        def mock_qtimer_constructor():
            timer = self.timer_instances[self.timer_call_count]
            self.timer_call_count += 1
            return timer
            
        self.mock_qtimer_class = patch("manuskript.projectManager.QTimer", side_effect=mock_qtimer_constructor).start()

        # Patch QStandardItemModel to avoid TypeError
        self.mock_qstandarditemmodel_class = patch("manuskript.projectManager.QStandardItemModel", autospec=True).start()

        self.project_manager = ProjectManager(self.window)

    def tearDown(self):
        patch.stopall()

    def _load_project_helper(self, auto_save, auto_save_no_changes):
        with patch("manuskript.projectManager.settings") as mock_settings, \
             patch("importlib.reload"), \
             patch("os.path.exists", return_value=True), \
             patch.object(self.project_manager, "loadDatas", return_value=True), \
             patch.object(self.project_manager, "loadEmptyDatas"), \
             patch.object(self.window, "makeConnections"):
            mock_settings.autoSave = auto_save
            mock_settings.autoSaveDelay = 15
            mock_settings.autoSaveNoChanges = auto_save_no_changes
            mock_settings.autoSaveNoChangesDelay = 3
            mock_settings.openIndexes = []
            mock_settings.viewSettings = {"Tree": {"iconSize": 24}}
            mock_settings.lastTab = 0
            mock_settings.corkSizeFactor = 100
            mock_settings.spellcheck = False
            mock_settings.folderView = False
            mock_settings.viewMode = "fiction"

            self.project_manager.loadProject("dummy_project.msk")

    def test_save_timer_starts_on_load_with_autosave_enabled(self):
        self._load_project_helper(auto_save=True, auto_save_no_changes=False)
        # Timer interval is always set during loadProject
        self.mock_save_timer.setInterval.assert_called_with(15 * 60 * 1000)
        # Timer only starts if autoSave is enabled
        self.mock_save_timer.start.assert_called_once()

    def test_save_timer_does_not_start_with_autosave_disabled(self):
        self._load_project_helper(auto_save=False, auto_save_no_changes=False)
        self.mock_save_timer.start.assert_not_called()

    def test_save_timer_stops_on_project_close(self):
        self._load_project_helper(auto_save=True, auto_save_no_changes=False)
        with patch.object(self.project_manager, "handleUnsavedChanges", return_value=True), \
             patch.object(self.project_manager, "loadEmptyDatas"):
            self.project_manager.closeProject()
        self.mock_save_timer.stop.assert_called_once()

    def test_save_timer_no_changes_starts_on_data_change(self):
        self._load_project_helper(auto_save=True, auto_save_no_changes=True)
        # Reset the mock to ignore calls made during project loading
        self.mock_save_timer_no_changes.start.reset_mock()
        self.project_manager.startTimerNoChanges()
        self.mock_save_timer_no_changes.start.assert_called_once()
        self.assertTrue(self.window.projectDirty)

    def test_save_timer_no_changes_does_not_start_with_autosave_disabled(self):
        self._load_project_helper(auto_save=False, auto_save_no_changes=False)
        # Need to mock settings during the actual startTimerNoChanges call
        with patch("manuskript.projectManager.settings") as mock_settings:
            mock_settings.autoSaveNoChanges = False
            self.project_manager.startTimerNoChanges()
        self.mock_save_timer_no_changes.start.assert_not_called()

    def test_save_timer_no_changes_stops_on_project_close(self):
        self._load_project_helper(auto_save=True, auto_save_no_changes=True)
        self.project_manager.startTimerNoChanges()
        with patch.object(self.project_manager, "handleUnsavedChanges", return_value=True), \
             patch.object(self.project_manager, "loadEmptyDatas"):
            self.project_manager.closeProject()
        self.mock_save_timer_no_changes.stop.assert_called()

    def test_save_timer_no_changes_stops_after_saving(self):
        self._load_project_helper(auto_save=True, auto_save_no_changes=True)
        self.project_manager.startTimerNoChanges()
        with patch("manuskript.loadSave.saveProject", return_value=True):
            self.project_manager.saveDatas()
        self.mock_save_timer_no_changes.stop.assert_called()

    @patch("manuskript.loadSave.saveProject", return_value=True)
    def test_save_timer_triggers_save_datas(self, mock_save_project):
        self._load_project_helper(auto_save=True, auto_save_no_changes=False)
        # Manually trigger the timeout signal
        self.project_manager.saveTimer.timeout.connect.call_args[0][0]()
        mock_save_project.assert_called_once()

    @patch("manuskript.loadSave.saveProject", return_value=True)
    def test_save_timer_no_changes_triggers_save_datas(self, mock_save_project):
        self._load_project_helper(auto_save=True, auto_save_no_changes=True)
        self.project_manager.startTimerNoChanges()
        # Manually trigger the timeout signal
        self.project_manager.saveTimerNoChanges.timeout.connect.call_args[0][0]()
        mock_save_project.assert_called_once()

if __name__ == "__main__":
    unittest.main()