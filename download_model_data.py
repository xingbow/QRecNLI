import os
import gdown
import subprocess

prefix = "./backend/app/data/"
if not os.path.isdir(prefix):
    os.mkdir(prefix)

if not os.path.isdir(os.path.join(prefix, "model")):
    os.mkdir(os.path.join(prefix, "model"))

if not os.path.isdir(os.path.join(prefix, "dataset")):
    os.mkdir(os.path.join(prefix, "dataset"))

# install SmBop dependency
if not os.path.isdir(os.path.join(prefix, 'model/SmBop')):
    SmBop_git = "https://github.com/xingbow/SmBop.git"
    ps = subprocess.run(["git", "clone", SmBop_git, os.path.join(prefix,"model/SmBop")])
# SmBop model (text2sql)
if not os.path.isfile(os.path.join(prefix, 'model/smbop.tar.gz')):
    SmBop_url = 'https://drive.google.com/u/0/uc?id=1pQvg2sT7h9t_srgmN1nGGMfIPa62U9ag'
    output = os.path.join(prefix, 'model/smbop.tar.gz')
    gdown.download(SmBop_url, output, quiet=False)


# Spider dataset
if not os.path.join(prefix, 'dataset/spider.zip'):
    Spider_url = 'https://drive.google.com/uc?export=download&id=1_AckYkinAnhqmRQtGsQgUKAnTHxxX5J0'
    output = os.path.join(prefix, 'dataset/spider.zip')
    gdown.download(Spider_url, output, quiet=False)
    ps = subprocess.run(["unzip", "-q", output, "-d", os.path.join(prefix, "dataset")])

# nvBench
nvBench_url = "https://github.com/TsinghuaDatabaseGroup/nvBench.git"
if not os.path.isdir(os.path.join(prefix, 'dataset/nvBench')):
    ps = subprocess.run(["git", "clone", nvBench_url, os.path.join(prefix,"dataset/nvBench")])
    ps = subprocess.run(["unzip", "-q", os.path.join(prefix,"dataset/nvBench/databases.zip"), "-d", os.path.join(prefix,"dataset/nvBench/")])

# UnifiedSKG
if not os.path.isdir(os.path.join(prefix, 'model/UnifiedSKG')):
    unifiedSKG_git = "git@github.com:xingbow/UnifiedSKG.git"
    ps = subprocess.run(["git", "clone", "--recurse-submodules", unifiedSKG_git, os.path.join(prefix,"model/UnifiedSKG")])


