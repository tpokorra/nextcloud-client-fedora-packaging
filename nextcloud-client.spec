%global _hardened_build 1

Name:           nextcloud-client
Version:        2.2.4
Release:        3%{?dist}
Summary:        The Nextcloud Client

# -libs are LGPLv2+, rest GPLv2
License:        LGPLv2+ and GPLv2
Url:            https://nextcloud.com/install/#install-clients
Source0:        https://github.com/nextcloud/client_theming/archive/v%{version}.tar.gz
Source1:        https://download.owncloud.com/desktop/stable/owncloudclient-%{version}.tar.xz
Source2:        %{name}.appdata.xml
Patch0:         %{name}-%{version}-syslibs.patch
# backport of https://github.com/owncloud/client/pull/5294
# Fedora Rawhide 26 ships OpenSSL 1.1.0 that no longer permits to call the old
# SSLeay_add_all_algorithms() that has been replaced with
# OpenSSL_add_all_algorithms() since OpenSSL version 0.9.5.
# I solved by adding a macro that calls:
# -SSLeay_add_all_algorithms() if the system uses OpenSSL <= 0.9.4
# -OpenSSL_add_all_algorithms() if the system uses OpenSSL > 0.9.4
Patch1:         %{name}-%{version}-appshortname.patch
Patch2:         openssl.patch

BuildRequires:  check
BuildRequires:  cmake
BuildRequires:  desktop-file-utils
BuildRequires:  doxygen
BuildRequires:  libappstream-glib
BuildRequires:  neon-devel
BuildRequires:  openssl-devel
BuildRequires:  python-sphinx
BuildRequires:  qtlockedfile-qt5-devel
BuildRequires:  qtkeychain-qt5-devel >= 0.7.0
BuildRequires:  qtsingleapplication-qt5-devel
BuildRequires:  qt5-qtbase
BuildRequires:  qt5-qtbase-devel
BuildRequires:  qt5-qtbase-gui
BuildRequires:  qt5-qtwebkit-devel
BuildRequires:  qt5-qtxmlpatterns-devel
BuildRequires:  qt5-qttools qt5-qttools-devel
BuildRequires:  extra-cmake-modules
BuildRequires:  kf5-kio-devel
BuildRequires:  kf5-kcoreaddons-devel
BuildRequires:  kf5-rpm-macros

BuildRequires:  sqlite-devel
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}

Provides: mirall = %{version}-%{release}
Obsoletes: mirall < 1.8.0

%description
Nextcloud-client enables you to connect to your private Nextcloud Server.
With it you can create folders in your home directory, and keep the contents
of those folders synced with your Nextcloud server. Simply copy a file into
the directory and the Nextcloud Client does the rest.


%package libs
Summary: Common files for nextcloud-client and nextcloud-client
License: LGPLv2+
Provides: mirall-common = %{version}-%{release}
Obsoletes: mirall-common < 1.8.0

%description libs
Provides common files for nextcloud-client such as the
configuration file that determines the excluded files in a sync.


%package devel
Summary: Development files for nextcloud-client
License: LGPLv2+
Requires: %{name}-libs%{?_isa} = %{version}-%{release}
Provides: %{name}-static = %{version}-%{release}
Provides: mirall-devel = %{version}-%{release}
Obsoletes: mirall-devel < 1.8.0

%description devel
Development headers for use of the nextcloud-client library

%package nautilus
Summary: nextcloud client nautilus extension
Requires: nautilus
Requires: nautilus-python
Provides: mirall-nautilus = %{version}-%{release}
Obsoletes: mirall-nautilus < 1.8.0


%description nautilus
The nextcloud desktop client nautilus extension.

%package nemo
Summary:        Nemo overlay icons
Requires:       nemo
Requires:       nemo-python

%description nemo
This package provides overlay icons to visualize the sync state
in the nemo file manager.

%if 0%{?fedora} >= 24 || 0%{?rhel} > 7
%package dolphin
Summary:        Dolphin overlay icons
Requires:       dolphin

%description dolphin
The nextcloud desktop client dolphin extension.
%endif

%prep
%setup -q -n client_theming-%{version}
%setup -T -D -a 1 -n client_theming-%{version}
rm -Rf client
mv owncloudclient-%{version} client
cd client
%patch0 -p1
cd -
%patch1 -p1
cd client
%patch2 -p1
cd -
rm -rf src/3rdparty/qtlockedfile src/3rdparty/qtsingleapplication


%build
mkdir build
pushd build
%cmake_kf5 .. -DCMAKE_SHARED_LINKER_FLAGS="-Wl,--as-needed" -D OEM_THEME_DIR=`pwd`/../nextcloudtheme ../client
make %{?_smp_mflags}
popd


%install
pushd build
make install DESTDIR=%{buildroot}
popd
%find_lang client --with-qt
mkdir -p %{buildroot}%{_datadir}/appdata/
install -m 644 %{SOURCE2} %{buildroot}%{_datadir}/appdata/%{name}.appdata.xml


%check
appstream-util validate-relax --nonet %{buildroot}%{_datadir}/appdata/%{name}.appdata.xml


%post
touch --no-create %{_datadir}/icons/hicolor &> /dev/null || :

%posttrans
gtk-update-icon-cache -f %{_datadir}/icons/hicolor &>/dev/null || :

%postun
if [ $1 -eq 0 ] ; then
    touch --no-create %{_datadir}/icons/hicolor &> /dev/null
    gtk-update-icon-cache -f %{_datadir}/icons/hicolor &> /dev/null || :
fi

%post libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig

%if 0%{?fedora} >= 24 || 0%{?rhel} > 7
%post dolphin -p /sbin/ldconfig
%postun dolphin -p /sbin/ldconfig
%endif

%files -f client.lang
%{_bindir}/nextcloud
%{_bindir}/nextcloudcmd
%{_datadir}/applications/nextcloud.desktop
%{_datadir}/icons/hicolor/*/apps/*
%{_datadir}/appdata/%{name}.appdata.xml

%files libs
%{_libdir}/libnextcloudsync.so.0
%{_libdir}/libnextcloudsync.so.%{version}
%{_libdir}/nextcloud/libocsync.so.*
%doc README.md
%license client/COPYING
%config %{_sysconfdir}/Nextcloud/sync-exclude.lst
%dir %{_sysconfdir}/Nextcloud

%files devel
%{_libdir}/libnextcloudsync.so
%{_includedir}/nextcloudsync/
%{_libdir}/libnextcloudsync.so
%{_libdir}/nextcloud/libocsync.so

%files nautilus
%{_datadir}/nautilus-python/extensions/*

%files nemo
%{_datadir}/nemo-python/extensions/*

%if 0%{?fedora} >= 24 || 0%{?rhel} > 7
%files dolphin
%{_libdir}/libnextclouddolphinpluginhelper.so
%{_kf5_plugindir}/overlayicon/nextclouddolphinoverlayplugin.so
%{_qt5_plugindir}/nextclouddolphinactionplugin.so
%{_kf5_datadir}/kservices5/nextclouddolphinactionplugin.desktop
%endif

%changelog
* Wed Nov 02 2016 Germano Massullo <germano.massullo@gmail.com> 2.2.4-3
- First release
