pkgbase=test_toolkit
pkgname=('test_toolkit')
pkgver=1.0
pkgrel=1
pkgdesc="Test Toolkit"
arch=('any')
url="http:"
license=('GPL')
makedepends=('python')
depends=('python')
source=()

pkgver() {
    python ../setup.py -V
}

check() {
    pushd ..
    python setup.py check
    popd
}

package() {
    pushd ..
    python setup.py install --root=$pkgdir
    popd
}

