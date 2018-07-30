# Don't try fancy stuff like debuginfo, which is useless on binary-only
# packages. Don't strip binary too
# Be sure buildpolicy set to do nothing
%define name    manuskript
%define version {AppVersion}
%define release {PkgNumber}
%define        __spec_install_post %{nil}
%define          debug_package %{nil}
%define        __os_install_post %{_dbpath}/brp-compress

Summary: Manuskript open source tool for writers
Name: %{name}
Version: %{version}
Release: %{release}
License: GPL3+
Group: Applications/Editors
BuildArch: noarch
BuildRoot: %{_builddir}/%{name}-%{version}-%{release}-root
URL: http://www.theologeek.ch/manuskript/
SOURCE0 : %{name}-%{version}.tar.gz
Packager: Curtis Gedak <gedakc@gmail.com>
Provides: Manuskript
Requires: python3, python3-qt5, python3-lxml, zlib, python3-markdown, pandoc
%if 0%{?suse_version}
# Assume openSUSE
# Note - have to build rpm on openSUSE for this to work.
Requires: libQt5Svg5, python3-pyenchant
%else
# Assume Fedora and others
Requires: python3-qt5-webkit, qt5-qtsvg, python3-enchant
%endif

%description
Manuskript is an open source tool for writers.  It
provides a rich environment to help writers create
their first draft and then further refine and edit
their masterpiece.

%prep
%setup -q

%build
# Empty section.

%install
rm -rf %{buildroot}
mkdir -p  %{buildroot}

# in builddir
cp -a * %{buildroot}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
/usr/bin/manuskript
/usr/share/applications/manuskript.desktop
/usr/share/manuskript/*

%changelog
# Empty section.
