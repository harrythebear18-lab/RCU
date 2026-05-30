# Git LFS Setup Guide

## Quick Setup (5 minutes)

### For Windows Users:

1. **Install Git LFS** (one-time setup):
```bash
# Option 1: Download installer
# Visit: https://git-lfs.github.com/

# Option 2: Install via winget
winget install Git-LFS

# Option 3: Install via Chocolatey
choco install git-lfs
```

2. **Initialize Git LFS** (one-time per machine):
```bash
git lfs install
```

3. **Clone the repository**:
```bash
git clone https://github.com/harrythebear18-lab/Homelab-Tools.git
cd Homelab-Tools
```

4. **Pull LFS files** (only for large files):
```bash
git lfs pull
```

## What Uses LFS?

Only these large files use Git LFS:
- `rdma_memory_pool.bin` (4.2GB) - RDMA memory pool
- `memory_pool.bin` - Additional memory pools
- Files over 100MB (`*.100mb+`)

## All Other Files

All other files (Python code, configs, small binaries, logs, etc.) are tracked normally and don't need LFS.

## Troubleshooting

### If you get LFS errors:
```bash
# Skip LFS files (you can still use all tools)
git config core.hooksspath ""

# Or install LFS properly:
git lfs install
git lfs pull
```

### If cloning is slow:
```bash
# Clone without LFS files first
git clone --no-filter https://github.com/harrythebear18-lab/Homelab-Tools.git

# Then pull LFS files later if needed
git lfs pull
```

## Verification

Check if LFS is working:
```bash
git lfs ls-files
```

This should show only the large memory pool files.

## Notes

- **71 tools work without LFS** - All Python functionality works immediately
- **Only memory pools need LFS** - For advanced RDMA features
- **Repository size without LFS**: ~50MB
- **Repository size with LFS**: ~4.3GB (due to memory pools)
