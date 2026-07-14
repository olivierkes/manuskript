import unittest
from unittest.mock import MagicMock, patch

from manuskript.projectManager import ProjectManager

class TestProjectManager(unittest.TestCase):

    def setUp(self):
        self.window = MagicMock()
        self.project_manager = ProjectManager(self.window)

    @patch('manuskript.functions.statusMessage')
    @patch('os.path.exists')
    def test_load_project_file_not_exists(self, mock_exists, mock_status_message):
        # Test case: file doesn't exist
        mock_exists.return_value = False
        expected_message = "The file {} does not exist. Has it been moved or deleted?"
        self.window.tr.return_value = expected_message
        
        self.project_manager.loadProject("non_existent_project.msk")
        
        # Verify the translation function was called with correct message
        self.window.tr.assert_called_with("The file {} does not exist. Has it been moved or deleted?")
        # Verify statusMessage was called with the translated message and importance=3
        mock_status_message.assert_called_once_with(expected_message.format("non_existent_project.msk"), importance=3)
        
    @patch('manuskript.functions.statusMessage')
    @patch('os.path.exists')
    def test_load_project_file_exists(self, mock_exists, mock_status_message):
        # Test case: file exists - should proceed with loading
        mock_exists.return_value = True
        
        # Mock the loading methods to avoid complex setup
        with patch.object(self.project_manager, 'loadEmptyDatas'), \
             patch.object(self.project_manager, 'loadDatas', return_value=True), \
             patch.object(self.window, 'makeConnections'), \
             patch('manuskript.settings.openIndexes', []), \
             patch('manuskript.settings.viewSettings', {"Tree": {"iconSize": 24}}):
            
            self.project_manager.loadProject("existing_project.msk")
            
            # Should not call the error message about file not existing
            error_calls = [call for call in self.window.tr.call_args_list 
                          if "does not exist" in str(call)]
            self.assertEqual(len(error_calls), 0, "Should not show file not found error")
            
            # Should not call statusMessage with importance=3 (error level)
            error_status_calls = [call for call in mock_status_message.call_args_list 
                                if len(call.kwargs) > 0 and call.kwargs.get('importance') == 3]
            self.assertEqual(len(error_status_calls), 0, "Should not show error status message")

if __name__ == '__main__':
    unittest.main()
