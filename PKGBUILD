pkgbase=test_toolkit
pkgname=('test_toolkit')
pkgver=1.0
pkgrel=2
pkgdesc="Test Toolkit"
arch=('any')
url="http:"
license=('GPL')
makedepends=('python' 'python-build')
depends=('python')
source=()

pkgver() {
	pushd .. > /dev/null
    python version.py
	popd > /dev/null
}

build() {
    pushd ..
    python -m build
    popd
}


package() {
    pushd ..
    pip install --root=$pkgdir --force-reinstall dist/Test_Toolkit-$pkgver-py3-none-any.whl
    popd
}

