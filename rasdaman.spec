# TODO: complete Java parts
# - build r[as]view program from sources
# NOTE:
# - inter-library dependencies contain too many cycles to make shared libraries
# - some libraries have too common names to put them into system lib directory
# ...so we package static libraries (with PIC enabled, so they could be linked
# into shared library/module) in private tree
#
# Conditional build:
%bcond_without	hdf4		# HDF 4 support
%bcond_without	java		# Java-based components
%bcond_without	netcdf		# NetCDF support
%bcond_with	doc		# Build documentation
#
Summary:	Rasdaman - intelligent multidimensional raster server
Summary(pl.UTF-8):	Rasdaman - inteligentny, wielowymiarowy serwer danych rastrowych
Name:		rasdaman
Version:	8.4.0
Release:	7
License:	GPL v3+
Group:		Libraries
#Source0Download: http://rasdaman.eecs.jacobs-university.de/wiki/Versions
Source0:	http://rasdaman.eecs.jacobs-university.de/raw-attachment/wiki/Versions/%{name}-v%{version}.tgz
# Source0-md5:	c9a687ea3a723444b03d26d94b7b64aa
# for newer versions, not archived on trac:
# git clone git://kahlua.eecs.jacobs-university.de/rasdaman.git
# git archive --prefix=rasdaman-%{version}/ -o ../rasdaman-%{version}.tar.gz v%{version}
Patch0:		%{name}-configure.patch
Patch1:		%{name}-libpng.patch
Patch2:		%{name}-bison.patch
Patch3:		%{name}-shared.patch
URL:		http://rasdaman.eecs.jacobs-university.de/
BuildRequires:	autoconf >= 2.61
BuildRequires:	automake >= 1:1.9
BuildRequires:	bison
BuildRequires:	doxygen
BuildRequires:	flex
BuildRequires:	gdal-devel
%{?with_hdf4:BuildRequires:	hdf-devel >= 4}
%{?with_java:BuildRequires:	jdk}
BuildRequires:	libjpeg-devel >= 6b
BuildRequires:	libpng-devel
#BuildRequires:	libsigsegv
BuildRequires:	libstdc++-devel
BuildRequires:	libtiff-devel
BuildRequires:	ncurses-devel
%{?with_netcdf:BuildRequires:	netcdf-devel}
%{?with_netcdf:BuildRequires:	netcdf-cxx-devel}
BuildRequires:	netpbm-devel
BuildRequires:	openssl-devel
BuildRequires:	postgresql-devel >= 7.4.6
BuildRequires:	postgresql-ecpg-devel >= 7.4.6
BuildRequires:	readline-devel
BuildRequires:	zlib-devel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Rasdaman Community is a free, open-source middleware extending
standard relational database systems with the ability to efficiently
query and manipulate multi-dimensional arrays of unlimited size. Such
arrays are also called "raster data", "gridded data" etc. depending on
the application domain.

%description -l pl.UTF-8
Rasdaman Community to wolnodostępny, mający otwarte źródła system baz
danych pośredniczących, rozszerzających standard, mających możliwość
wydajnego wyszukiwania i modyfikowania tabel wielowymiarowych bez
ograniczeń rozmiaru. Tabele takie są nazywane "danymi rastrowymi" lub
"danymi tablicowymi" w zależności od dziedziny aplikacji.

%package devel
Summary:	Header files and static rasdaman libraries
Summary(pl.UTF-8):	Pliki nagłówkowe i statyczne biblioteki rasdaman
Group:		Development/Libraries

%description devel
Header files and static rasdaman libraries.

%description devel -l pl.UTF-8
Pliki nagłówkowe i statyczne biblioteki rasdaman.

%package static
Summary:	Static rasdaman libraries
Summary(pl.UTF-8):	Statyczne biblioteki rasdaman
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static rasdaman libraries.

%description static -l pl.UTF-8
Statyczne biblioteki rasdaman.

%package doc
Summary:	Rasdaman middleware documentation
Summary(pl.UTF-8):	Dokumentacja do oprogramowania pośredniego rasdaman
Group:		Documentation

%description doc
Rasdaman middleware documentation.

%description doc -l pl.UTF-8
Dokumentacja do oprogramowania pośredniego rasdaman.

%prep
%setup -q -c
%patch -P0 -p1
%patch -P1 -p1
%patch -P2 -p1
#patch3 -p1

ln -sf oql.hh qlparser/oql.h
ln -sf odl.hh rasdl/odl.h

# TODO: kill precompiled binary, force rebuild (no makefile as of 8.4.0)
#%{__rm} applications/rview/rview

%build
%{__libtoolize}
%{__aclocal} -I m4
%{__autoconf}
%{__automake}
CPPFLAGS="%{rpmcppflags} -I/usr/include/ecpg"
CFLAGS="%{rpmcflags} -fPIC"
CXXFLAGS="%{rpmcxxflags} -fPIC"
%configure \
	--includedir=%{_includedir}/rasdaman \
	--libdir=%{_libdir}/rasdaman/lib \
	%{!?with_java:--disable-java} \
	%{__with_without docs} \
	%{?with_hdf4:--with-hdf4} \
	--with-logdir=/var/log/rasdaman \
	%{?with_netcdf:--with-netcdf}
%{__make} -j1

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_docdir},%{_examplesdir}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

# potential or real name conflicts
%{__mv} $RPM_BUILD_ROOT%{_bindir}/{create_db,ras_create_db}.sh
%{__mv} $RPM_BUILD_ROOT%{_bindir}/{insertppm,ras_insertppm}
%{__mv} $RPM_BUILD_ROOT%{_bindir}/{rview,rasview}
%{__mv} $RPM_BUILD_ROOT%{_bindir}/{update_db,ras_update_db}.sh
# XXX: needs patch
%{__mv} $RPM_BUILD_ROOT%{_bindir}/labels.txt $RPM_BUILD_ROOT%{_datadir}/rasdaman

%{__mv} $RPM_BUILD_ROOT%{_datadir}/rasdaman/examples $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}

%if %{with doc}
%{__mv} $RPM_BUILD_ROOT%{_datadir}/rasdaman/doc $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
# package just PDFs, no MS DOCs
%{__rm} $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/pdf/*.doc
%endif

# provide "include" and "lib" inside %{_libdir}/rasdaman tree
ln -sf %{_includedir}/rasdaman $RPM_BUILD_ROOT%{_libdir}/rasdaman/include

# should(?) belong to log4j
%{__rm} $RPM_BUILD_ROOT%{_sysconfdir}/log4j.properties
# ???
%{__rm} $RPM_BUILD_ROOT%{_prefix}/.rviewrc
%{__rm} $RPM_BUILD_ROOT/var/log/rasdaman/empty

# precompiled x86 binary (TODO: compile it)
%{__rm} $RPM_BUILD_ROOT%{_bindir}/rasview

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/add_wms_service.sh
%attr(755,root,root) %{_bindir}/drop_wms.sh
%attr(755,root,root) %{_bindir}/fill_pyramid.sh
%attr(755,root,root) %{_bindir}/fillpyramid
%attr(755,root,root) %{_bindir}/init_wms.sh
%attr(755,root,root) %{_bindir}/initpyramid
%attr(755,root,root) %{_bindir}/petascope_insertdemo.sh
%attr(755,root,root) %{_bindir}/ras_create_db.sh
%attr(755,root,root) %{_bindir}/ras_insertppm
%attr(755,root,root) %{_bindir}/ras_update_db.sh
%attr(755,root,root) %{_bindir}/rascontrol
%attr(755,root,root) %{_bindir}/rasdaman_insertdemo.sh
%attr(755,root,root) %{_bindir}/rasdl
%attr(755,root,root) %{_bindir}/raserase
%attr(755,root,root) %{_bindir}/rasimport
%attr(755,root,root) %{_bindir}/rasmgr
%attr(755,root,root) %{_bindir}/raspasswd
%attr(755,root,root) %{_bindir}/rasql
%attr(755,root,root) %{_bindir}/rasserver
#%attr(755,root,root) %{_bindir}/rasview
%attr(755,root,root) %{_bindir}/start_rasdaman.sh
%attr(755,root,root) %{_bindir}/stop_rasdaman.sh
%attr(755,root,root) %{_bindir}/update_petascopedb.sh
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/rasmgr.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/petascope.properties
%dir %{_datadir}/rasdaman
%{_datadir}/rasdaman/db_updates
%{_datadir}/rasdaman/petascope
%{_datadir}/rasdaman/raswct
%{_datadir}/rasdaman/war
%{_datadir}/rasdaman/errtxts
%lang(de) %{_datadir}/rasdaman/errtxts_de
%lang(en) %{_datadir}/rasdaman/errtxts_en
%lang(fr) %{_datadir}/rasdaman/errtxts_fr
%{_datadir}/rasdaman/labels.txt
%dir /var/log/rasdaman

%files devel
%defattr(644,root,root,755)
%{_includedir}/rasdaman
%dir %{_libdir}/rasdaman
%{_libdir}/rasdaman/include
%dir %{_libdir}/rasdaman/lib
%{_libdir}/rasdaman/lib/libcatalogmgr.a
%{_libdir}/rasdaman/lib/libclientcomm.a
%{_libdir}/rasdaman/lib/libcommline.a
%{_libdir}/rasdaman/lib/libconversion.a
%{_libdir}/rasdaman/lib/libhttpserver.a
%{_libdir}/rasdaman/lib/libindexmgr.a
%{_libdir}/rasdaman/lib/libmddmgr.a
%{_libdir}/rasdaman/lib/libnetwork.a
%{_libdir}/rasdaman/lib/libqlparser.a
%{_libdir}/rasdaman/lib/libraslib.a
%{_libdir}/rasdaman/lib/librasodmg.a
%{_libdir}/rasdaman/lib/libreladminif.a
%{_libdir}/rasdaman/lib/librelblobif.a
%{_libdir}/rasdaman/lib/librelcatalogif.a
%{_libdir}/rasdaman/lib/librelindexif.a
%{_libdir}/rasdaman/lib/librelmddif.a
%{_libdir}/rasdaman/lib/librelstorageif.a
%{_libdir}/rasdaman/lib/libservercomm.a
%{_libdir}/rasdaman/lib/libstoragemgr.a
%{_libdir}/rasdaman/lib/libtilemgr.a

%if 0
%files static
%defattr(644,root,root,755)
# TODO
%endif

%files doc
%defattr(644,root,root,755)
%if %{with doc}
%{_docdir}/%{name}-%{version}
%endif
%{_examplesdir}/%{name}-%{version}
