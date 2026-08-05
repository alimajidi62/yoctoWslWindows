#!/bin/bash
# Remove broken cuda PATH lines and re-add them correctly
sed -i '/export PATH=\/usr\/local\/cuda/d' ~/.bashrc
sed -i '/export LD_LIBRARY_PATH=\/usr\/local\/cuda/d' ~/.bashrc

cat >> ~/.bashrc << 'EOF'
export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
EOF

echo "Fixed. New lines:"
grep cuda ~/.bashrc
