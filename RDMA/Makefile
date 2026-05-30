# Makefile for Virtual DMA Kernel Driver
# Build system for Software-Defined RDMA Project

# Kernel module build configuration
obj-m := virtual_dma_driver.o

# Kernel directory (auto-detect)
KDIR := /lib/modules/$(shell uname -r)/build

# Default target
all: kernel userspace

# Kernel driver build
kernel:
	@echo "Building Virtual DMA Kernel Driver..."
	$(MAKE) -C $(KDIR) M=$(PWD) modules
	@echo "Kernel driver built successfully"

# Userspace components
userspace:
	@echo "Building userspace components..."
	python3 -m py_compile *.py
	@echo "Userspace components compiled"

# Install kernel module
install-kernel: kernel
	@echo "Installing Virtual DMA Kernel Driver..."
	sudo insmod virtual_dma_driver.ko
	sudo chmod 666 /dev/virtual_dma
	@echo "Kernel driver installed"
	@echo "Check with: lsmod | grep virtual_dma"

# Remove kernel module
uninstall-kernel:
	@echo "Removing Virtual DMA Kernel Driver..."
	sudo rmmod virtual_dma_driver
	@echo "Kernel driver removed"

# Install Python dependencies
install-deps:
	@echo "Installing Python dependencies..."
	pip3 install -r requirements.txt
	@echo "Dependencies installed"

# Full installation
install: install-deps install-kernel
	@echo "Full installation completed"

# Full uninstall
uninstall: uninstall-kernel
	@echo "Uninstall completed"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	$(MAKE) -C $(KDIR) M=$(PWD) clean
	rm -f *.pyc *.pyo __pycache__/*.pyc
	rm -rf __pycache__
	@echo "Clean completed"

# Test suite
test:
	@echo "Running comprehensive test suite..."
	python3 test_suite.py

# Quick test (basic functionality)
test-quick:
	@echo "Running quick tests..."
	python3 -c "
import sys
sys.path.insert(0, '.')
from test_suite import TestZeroCopyRDMA, TestRobustNetworkLayer
import unittest

suite = unittest.TestSuite()
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestZeroCopyRDMA))
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRobustNetworkLayer))

runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
"

# Performance benchmark
benchmark:
	@echo "Running performance benchmarks..."
	python3 -c "
import sys
sys.path.insert(0, '.')
from test_suite import PerformanceBenchmark
import unittest

suite = unittest.TestLoader().loadTestsFromTestCase(PerformanceBenchmark)
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
"

# Demo all components
demo:
	@echo "Starting demo of all components..."
	@echo "1. Zero-Copy RDMA Demo"
	python3 zero_copy_rdmda.py benchmark &
	sleep 2
	@echo "2. Virtual PCIe Tunnel Demo"
	python3 virtual_pcie_tunnel.py target &
	sleep 2
	@echo "3. UDP Memory Bridge Demo"
	python3 udp_memory_bridge.py server &
	sleep 2
	@echo "All demos running. Check output above."
	@echo "Press Ctrl+C to stop all demos"
	wait

# Development setup
dev-setup:
	@echo "Setting up development environment..."
	@echo "Installing development dependencies..."
	pip3 install pytest pytest-cov black flake8 mypy
	@echo "Setting up pre-commit hooks..."
	@echo "Development environment ready"

# Code formatting
format:
	@echo "Formatting Python code..."
	black *.py
	@echo "Code formatted"

# Code linting
lint:
	@echo "Linting Python code..."
	flake8 *.py --max-line-length=100 --ignore=E501,W503
	mypy *.py --ignore-missing-imports
	@echo "Linting completed"

# Security audit
audit:
	@echo "Running security audit..."
	pip3 install bandit safety
	bandit -r . -f json -o bandit-report.json
	safety check --json --output safety-report.json
	@echo "Security audit completed"

# Documentation generation
docs:
	@echo "Generating documentation..."
	pip3 install sphinx sphinx-rtd-theme
	@echo "Documentation would be generated here"
	@echo "See README.md for user documentation"

# Package creation
package:
	@echo "Creating distribution package..."
	@mkdir -p dist
	@tar -czf dist/software-defined-rdma.tar.gz \
		--exclude='__pycache__' \
		--exclude='*.pyc' \
		--exclude='dist' \
		--exclude='.git' \
		--exclude='*.ko' \
		--exclude='*.o' \
		--exclude='.tmp_versions' \
		--exclude='Module.symvers' \
		--exclude='modules.order' \
		.
	@echo "Package created: dist/software-defined-rdma.tar.gz"

# Help target
help:
	@echo "Software-Defined RDMA Build System"
	@echo "=================================="
	@echo ""
	@echo "Available targets:"
	@echo "  all          - Build kernel driver and userspace components"
	@echo "  kernel       - Build kernel driver only"
	@echo "  userspace    - Build userspace components only"
	@echo "  install      - Full installation (deps + kernel)"
	@echo "  uninstall    - Full uninstall"
	@echo "  install-kernel - Install kernel module only"
	@echo "  uninstall-kernel - Remove kernel module only"
	@echo "  install-deps - Install Python dependencies"
	@echo "  test         - Run comprehensive test suite"
	@echo "  test-quick   - Run quick tests"
	@echo "  benchmark    - Run performance benchmarks"
	@echo "  demo         - Demo all components"
	@echo "  dev-setup    - Setup development environment"
	@echo "  format       - Format Python code"
	@echo "  lint         - Lint Python code"
	@echo "  audit        - Run security audit"
	@echo "  docs         - Generate documentation"
	@echo "  package      - Create distribution package"
	@echo "  clean        - Clean build artifacts"
	@echo "  help         - Show this help"
	@echo ""
	@echo "Examples:"
	@echo "  make install      # Full installation"
	@echo "  make test         # Run all tests"
	@echo "  make benchmark    # Performance tests"
	@echo "  make demo         # See everything in action"

# Phony targets
.PHONY: all kernel userspace install-kernel uninstall-kernel install-deps install uninstall clean test test-quick benchmark demo dev-setup format lint audit docs package help

# Default goal
.DEFAULT_GOAL := all
