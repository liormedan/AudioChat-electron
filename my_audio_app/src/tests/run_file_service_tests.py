import os
import sys
import unittest

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the test module
from tests.test_file_service import TestFileService

if __name__ == "__main__":
    # Run the tests
    unittest.main(module="tests.test_file_service")
