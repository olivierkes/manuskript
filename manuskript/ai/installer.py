#!/usr/bin/env python
# --!-- coding: utf8 --!--
"""
AI Dependencies Installer

Handles automatic installation of AI dependencies when user enables features.
"""

import os
import sys
import subprocess
import logging
from typing import List, Dict, Tuple, Optional

LOGGER = logging.getLogger(__name__)

class DependencyInstaller:
    """
    Manages installation of AI dependencies.
    """
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.requirements_file = os.path.join(self.base_dir, "requirements-ai.txt")
    
    def check_dependencies(self) -> Dict[str, bool]:
        """
        Check which AI dependencies are installed.
        
        Returns:
            Dict mapping dependency names to installation status
        """
        deps_status = {}
        
        # Check NetworkX
        try:
            import networkx
            deps_status['networkx'] = True
            LOGGER.debug(f"NetworkX version: {networkx.__version__}")
        except ImportError:
            deps_status['networkx'] = False
        
        # Check spaCy
        try:
            import spacy
            deps_status['spacy'] = True
            LOGGER.debug(f"spaCy version: {spacy.__version__}")
        except ImportError:
            deps_status['spacy'] = False
        
        # Check spaCy model
        if deps_status['spacy']:
            try:
                import spacy
                nlp = spacy.load("en_core_web_sm")
                deps_status['en_core_web_sm'] = True
                LOGGER.debug("spaCy English model loaded successfully")
            except OSError:
                deps_status['en_core_web_sm'] = False
        else:
            deps_status['en_core_web_sm'] = False
        
        # Check fastcoref
        try:
            import fastcoref
            deps_status['fastcoref'] = True
            LOGGER.debug(f"fastcoref available")
        except ImportError:
            deps_status['fastcoref'] = False
        
        return deps_status
    
    def install_package(self, package: str, upgrade: bool = False, max_retries: int = 3) -> bool:
        """
        Install a single package using pip with retry logic.
        
        Args:
            package: Package name to install
            upgrade: Whether to upgrade if already installed
            max_retries: Number of retry attempts
            
        Returns:
            True if successful, False otherwise
        """
        for attempt in range(max_retries):
            try:
                cmd = [sys.executable, '-m', 'pip', 'install']
                if upgrade:
                    cmd.append('--upgrade')
                cmd.append(package)
                
                attempt_msg = f" (attempt {attempt + 1}/{max_retries})" if attempt > 0 else ""
                LOGGER.info(f"Installing {package}{attempt_msg}...")
                
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=300  # 5 minutes timeout
                )
                
                if result.returncode == 0:
                    LOGGER.info(f"Successfully installed {package}")
                    return True
                else:
                    LOGGER.warning(f"Failed to install {package} (attempt {attempt + 1}): {result.stderr}")
                    if attempt < max_retries - 1:
                        LOGGER.info(f"Retrying in 2 seconds...")
                        import time
                        time.sleep(2)
                    
            except subprocess.TimeoutExpired:
                LOGGER.warning(f"Installation of {package} timed out (attempt {attempt + 1})")
                if attempt < max_retries - 1:
                    LOGGER.info("Retrying with shorter timeout...")
            except Exception as e:
                LOGGER.warning(f"Error installing {package} (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(1)
        
        LOGGER.error(f"Failed to install {package} after {max_retries} attempts")
        return False
    
    def download_spacy_model(self, model: str = "en_core_web_sm") -> bool:
        """
        Download a spaCy language model.
        
        Args:
            model: Model name to download
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cmd = [sys.executable, '-m', 'spacy', 'download', model]
            
            LOGGER.info(f"Downloading spaCy model: {model}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout for model download
            )
            
            if result.returncode == 0:
                LOGGER.info(f"Successfully downloaded {model}")
                return True
            else:
                LOGGER.error(f"Failed to download {model}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            LOGGER.error(f"Download of {model} timed out")
            return False
        except Exception as e:
            LOGGER.error(f"Error downloading {model}: {e}")
            return False
    
    def install_ai_dependencies(self, progress_callback: Optional[callable] = None) -> Tuple[bool, List[str]]:
        """
        Install all AI dependencies with graceful degradation.
        
        Args:
            progress_callback: Optional callback for progress updates
            
        Returns:
            Tuple of (success, list of error messages)
        """
        errors = []
        warnings = []
        total_steps = 4
        current_step = 0
        
        def update_progress(message: str):
            nonlocal current_step
            current_step += 1
            if progress_callback:
                progress_callback(current_step, total_steps, message)
            LOGGER.info(f"Step {current_step}/{total_steps}: {message}")
        
        # Step 1: Install NetworkX (required for graph features)
        update_progress("Installing NetworkX...")
        if not self.install_package("networkx>=3.0", max_retries=3):
            errors.append("Failed to install NetworkX - graph features will be limited")
        
        # Step 2: Install spaCy (required for advanced NLP)
        update_progress("Installing spaCy...")
        if not self.install_package("spacy>=3.7.0", max_retries=3):
            errors.append("Failed to install spaCy - NLP features will use fallback methods")
        else:
            # Step 3: Download spaCy model (only if spaCy installed successfully)
            update_progress("Downloading spaCy English model...")
            if not self.download_spacy_model("en_core_web_sm"):
                warnings.append("Failed to download spaCy English model - using basic NLP")
        
        # Step 4: Install fastcoref (optional enhancement)
        update_progress("Installing fastcoref (optional)...")
        if not self.install_package("fastcoref>=2.1.6", max_retries=2):
            warnings.append("Failed to install fastcoref - coreference resolution disabled")
        
        # Determine overall success
        # Core features work if at least one major component is available
        core_deps_available = any([
            self.check_dependencies().get('networkx', False),
            self.check_dependencies().get('spacy', False)
        ])
        
        if not core_deps_available:
            errors.insert(0, "No core AI dependencies installed - AI features will be severely limited")
        
        # Report summary
        success = len(errors) == 0
        if warnings:
            LOGGER.info(f"Installation completed with warnings: {'; '.join(warnings)}")
        
        return success, errors + warnings
    
    def get_installation_status(self) -> Dict[str, str]:
        """
        Get detailed installation status for UI display.
        
        Returns:
            Dict with status information
        """
        deps = self.check_dependencies()
        
        status = {
            'networkx': 'installed' if deps['networkx'] else 'missing',
            'spacy': 'installed' if deps['spacy'] else 'missing',
            'en_core_web_sm': 'installed' if deps['en_core_web_sm'] else 'missing',
            'fastcoref': 'installed' if deps['fastcoref'] else 'optional'
        }
        
        # Overall status
        required_deps = ['networkx', 'spacy', 'en_core_web_sm']
        all_required = all(deps[dep] for dep in required_deps)
        
        status['overall'] = 'ready' if all_required else 'incomplete'
        
        return status
    
    def uninstall_ai_dependencies(self) -> Tuple[bool, List[str]]:
        """
        Uninstall AI dependencies (for cleanup).
        
        Returns:
            Tuple of (success, list of error messages)
        """
        errors = []
        packages = ['fastcoref', 'spacy', 'networkx']
        
        for package in packages:
            try:
                cmd = [sys.executable, '-m', 'pip', 'uninstall', '-y', package]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    LOGGER.info(f"Uninstalled {package}")
                else:
                    LOGGER.warning(f"Could not uninstall {package}: {result.stderr}")
            
            except Exception as e:
                errors.append(f"Error uninstalling {package}: {e}")
        
        return len(errors) == 0, errors

# Global installer instance
_installer = None

def get_installer() -> DependencyInstaller:
    """Get or create the global installer instance."""
    global _installer
    if _installer is None:
        _installer = DependencyInstaller()
    return _installer

def check_ai_dependencies() -> Dict[str, bool]:
    """Quick check of AI dependencies status."""
    return get_installer().check_dependencies()

def install_ai_dependencies(progress_callback: Optional[callable] = None) -> Tuple[bool, List[str]]:
    """Install AI dependencies with optional progress tracking."""
    return get_installer().install_ai_dependencies(progress_callback)

def get_installation_status() -> Dict[str, str]:
    """Get installation status for UI display."""
    return get_installer().get_installation_status()

# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    installer = DependencyInstaller()
    
    print("Current dependency status:")
    status = installer.get_installation_status()
    for dep, stat in status.items():
        print(f"  {dep}: {stat}")
    
    if status['overall'] != 'ready':
        print("\nInstalling dependencies...")
        
        def progress(step, total, message):
            print(f"[{step}/{total}] {message}")
        
        success, errors = installer.install_ai_dependencies(progress)
        
        if success:
            print("✓ All dependencies installed successfully!")
        else:
            print("✗ Some installations failed:")
            for error in errors:
                print(f"  - {error}")
    else:
        print("✓ All dependencies are ready!")