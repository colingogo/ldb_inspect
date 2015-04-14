# ldb_inspect

A tool written in Python to visually inspect the LevelDB sets created for Caffe (http://caffe.berkeleyvision.org/), a deep learning framework.

**To use the tool:**
 1. Edit `resources/general.ini` and set the caffe path
 2. Run `inspector -i <leveldb address>

**Current Limitations (V1):**
 1. Only works with grayscale image
 2. The images are stored in the float type with pixel values in [0.0, 1.0]
Both are easy to fix, the next version will lift these limitations.
