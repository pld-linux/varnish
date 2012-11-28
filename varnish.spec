# TODO
# - make tests use secure dir, not /tmp, see varnish-2.0.6/bin/varnishtest
# - hungs ac builders: tests/a00009.vtc

# Conditional build:
%bcond_without	doc		# build documentation
%bcond_without	tests	# build without tests. binds daemon on 127.0.0.1 9080, 9081, 9001 ports

Summary:	Varnish - a high-performance HTTP accelerator
Summary(pl.UTF-8):	Varnish - wydajny akcelerator HTTP
Name:		varnish
Version:	3.0.3
Release:	2
License:	BSD
Group:		Networking/Daemons/HTTP
Source0:	http://repo.varnish-cache.org/source/%{name}-%{version}.tar.gz
# Source0-md5:	714310c83fdbd2061d897dacd3f63d8b
Source1:	%{name}.init
Source3:	%{name}ncsa.init
Source4:	%{name}.sysconfig
Source5:	%{name}ncsa.sysconfig
Source6:	%{name}.logrotate
Source8:	%{name}.tmpfiles
#Patch100:	branch.diff
Patch0:		no-ccache.patch
URL:		http://www.varnish-cache.org/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libstdc++-devel
BuildRequires:	libtool >= 2:1.5
BuildRequires:	ncurses-devel
BuildRequires:	pcre-devel
BuildRequires:	pkgconfig
BuildRequires:	rpmbuild(macros) >= 1.647
%if %{with doc}
BuildRequires:	docutils
BuildRequires:	groff
BuildRequires:	libxslt-progs
%endif
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	%{name}-libs = %{version}-%{release}
Requires:	gcc
Requires:	glibc-devel
Requires:	rc-scripts >= 0.4.1.26
Suggests:	vim-syntax-vcl
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_localstatedir	/var/run

%description
The goal of the Varnish project is to develop a state-of-the-art,
high-performance HTTP accelerator.

Varnish is targeted primarily at the FreeBSD 6 and Linux 2.6
platforms, and will take full advantage of the advanced I/O features
offered by these operating systems.

%description -l pl.UTF-8
Celem projektu Varnish jest stworzenie wydajnego akceleratora HTTP.

Varnish jest tworzony głównie z myślą o platformach FreeBSD 6 i Linux
2.6 i będzie wykorzystywał w pełni zaawansowane możliwości we/we
oferowane przez te systemy operacyjne.

%package libs
Summary:	Libraries for Varnish
Group:		Libraries
Conflicts:	varnish < 2.0.4-2

%description libs
Libraies for Varnish.

%package devel
Summary:	Header files for varnish library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki varnish
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}

%description devel
Header files for varnish library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki varnish.

%package static
Summary:	Static varnish library
Summary(pl.UTF-8):	Statyczna biblioteka varnish
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static varnish library.

%description static -l pl.UTF-8
Statyczna biblioteka varnish.

%prep
%setup -q
#%patch100 -p0
%patch0 -p1

%build
export CPPFLAGS="-I/usr/include/ncurses"
%{__aclocal} -I m4
%{__libtoolize}
%{__autoheader}
%{__automake}
%{__autoconf}
%configure \
%ifarch hppa s390 sparc ppc
	--disable-jemalloc
%endif

%{__make}

%if %{with tests}
%{__make} check \
	LD_LIBRARY_PATH="../../lib/libvarnish/.libs:../../lib/libvarnishcompat/.libs:../../lib/libvarnishapi/.libs:../../lib/libvcl/.libs"
%endif

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	INSTALL="install -p" \
	DESTDIR=$RPM_BUILD_ROOT

# make dirs after make install to know which ones needs spec and which ones make install
install -d $RPM_BUILD_ROOT{%{_sysconfdir},/etc/{logrotate.d,rc.d/init.d,sysconfig},/var/{run,lib}/varnish} \
	$RPM_BUILD_ROOT/var/log/{archive/,}varnish \
	$RPM_BUILD_ROOT%{systemdtmpfilesdir}

install -p %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/varnish
install -p %{SOURCE3} $RPM_BUILD_ROOT/etc/rc.d/init.d/varnishncsa
cp -p %{SOURCE4} $RPM_BUILD_ROOT/etc/sysconfig/varnish
cp -p %{SOURCE5} $RPM_BUILD_ROOT/etc/sysconfig/varnishncsa
cp -p %{SOURCE6} $RPM_BUILD_ROOT/etc/logrotate.d/varnish
cp -p %{SOURCE8} $RPM_BUILD_ROOT%{systemdtmpfilesdir}/%{name}.conf
touch $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/secret

%{__rm} $RPM_BUILD_ROOT%{_libdir}/%{name}/*.la
%{__rm} $RPM_BUILD_ROOT%{_libdir}/%{name}/vmods/*.la

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add varnish
/sbin/chkconfig --add varnishncsa
%service varnish restart
%service varnishncsa restart

%pre
%groupadd -g 241 %{name}
%useradd -u 241 -d /var/lib/%{name} -g %{name} -c "Varnishd User" %{name}

%postun
if [ "$1" = "0" ]; then
	%userremove %{name}
	%groupremove %{name}
fi

%preun
if [ "$1" = "0" ]; then
	%service -q varnish stop
	%service -q varnishncsa stop
	/sbin/chkconfig --del varnish
	/sbin/chkconfig --del varnishncsa
fi

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc LICENSE README ChangeLog etc/*.vcl
%dir %attr(750,root,root) %{_sysconfdir}/%{name}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/default.vcl
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/varnish
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/varnishncsa
%ghost %attr(600,root,root) %{_sysconfdir}/%{name}/secret
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/varnish
%attr(754,root,root) /etc/rc.d/init.d/varnish
%attr(754,root,root) /etc/rc.d/init.d/varnishncsa
%attr(755,root,root) %{_sbindir}/varnishd
%attr(755,root,root) %{_bindir}/varnishadm
%attr(755,root,root) %{_bindir}/varnishhist
%attr(755,root,root) %{_bindir}/varnishlog
%attr(755,root,root) %{_bindir}/varnishncsa
%attr(755,root,root) %{_bindir}/varnishreplay
%attr(755,root,root) %{_bindir}/varnishsizes
%attr(755,root,root) %{_bindir}/varnishstat
%attr(755,root,root) %{_bindir}/varnishtest
%attr(755,root,root) %{_bindir}/varnishtop
%dir %{_libdir}/%{name}
%attr(755,root,root) %{_libdir}/%{name}/libvarnish.so
%attr(755,root,root) %{_libdir}/%{name}/libvarnishcompat.so
%attr(755,root,root) %{_libdir}/%{name}/libvcl.so
%attr(755,root,root) %{_libdir}/%{name}/libvgz.so
%dir %{_libdir}/%{name}/vmods
%attr(755,root,root) %{_libdir}/%{name}/vmods/libvmod_std.so
%{_mandir}/man1/varnishadm.1*
%{_mandir}/man1/varnishd.1*
%{_mandir}/man1/varnishhist.1*
%{_mandir}/man1/varnishlog.1*
%{_mandir}/man1/varnishncsa.1*
%{_mandir}/man1/varnishreplay.1*
%{_mandir}/man1/varnishsizes.1*
%{_mandir}/man1/varnishstat.1*
%{_mandir}/man1/varnishtest.1*
%{_mandir}/man1/varnishtop.1*
%{_mandir}/man3/vmod_std.3*
%{_mandir}/man7/varnish-cli.7*
%{_mandir}/man7/varnish-counters.7*
%{_mandir}/man7/vcl.7*
%dir /var/lib/varnish
%dir /var/run/varnish
%{systemdtmpfilesdir}/%{name}.conf

%dir %attr(751,root,root) /var/log/varnish
%dir %attr(750,root,root) /var/log/archive/varnish

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libvarnishapi.so.*.*.*
%ghost %{_libdir}/libvarnishapi.so.1

%files devel
%defattr(644,root,root,755)
%{_includedir}/varnish
%{_libdir}/libvarnishapi.la
%{_libdir}/libvarnishapi.so
%{_pkgconfigdir}/varnishapi.pc

%files static
%defattr(644,root,root,755)
%{_libdir}/libvarnishapi.a
%{_libdir}/%{name}/libvarnish.a
%{_libdir}/%{name}/libvarnishcompat.a
%{_libdir}/%{name}/libvcl.a
%{_libdir}/%{name}/libvgz.a
%{_libdir}/%{name}/vmods/libvmod_std.a
