# TODO
# - debian/reload-vcl
Summary:	Varnish - a high-performance HTTP accelerator
Summary(pl.UTF-8):	Varnish - wydajny akcelerator HTTP
Name:		varnish
Version:	2.0.4
Release:	1
License:	BSD
Group:		Networking/Daemons/HTTP
Source0:	http://dl.sourceforge.net/varnish/%{name}-%{version}.tar.gz
# Source0-md5:	8044d59cb6d2ec6d09b7ae6033f06bbf
Source1:	%{name}.init
Source2:	%{name}log.init
Source3:	%{name}ncsa.init
Source4:	%{name}.sysconfig
Source5:	%{name}ncsa.sysconfig
Source6:	%{name}.logrotate
Source7:	%{name}.conf
Patch0:		%{name}-build.patch
URL:		http://www.varnish-cache.org/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	groff
BuildRequires:	libstdc++-devel
BuildRequires:	libtool >= 2:1.5
BuildRequires:	ncurses-devel
Requires(post):	/sbin/ldconfig
Requires(postun):	/sbin/ldconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	gcc
Requires:	glibc-devel
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

%package devel
Summary:	Header files for varnish library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki varnish
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

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
%patch0 -p1

%build
export CPPFLAGS="-I/usr/include/ncurses"
%{__aclocal}
%{__libtoolize}
%{__autoheader}
%{__automake}
%{__autoconf}
%configure \
%ifarch hppa s390 sparc ppc
	--disable-jemalloc
%endif

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

# make dirs after make install to know which ones needs spec and which ones make install
install -d $RPM_BUILD_ROOT{%{_sysconfdir},/etc/{logrotate.d,rc.d/init.d,sysconfig},/var/{run,lib}/varnish} \
	$RPM_BUILD_ROOT/var/log/{archive/,varnish}

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/varnish
install %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/varnishlog
install %{SOURCE3} $RPM_BUILD_ROOT/etc/rc.d/init.d/varnishncsa
install %{SOURCE4} $RPM_BUILD_ROOT/etc/sysconfig/varnish
install %{SOURCE5} $RPM_BUILD_ROOT/etc/sysconfig/varnishncsa
install %{SOURCE6} $RPM_BUILD_ROOT/etc/logrotate.d/varnish
install %{SOURCE7} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/default.vcl

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/ldconfig
/sbin/chkconfig --add varnish
/sbin/chkconfig --add varnishlog
/sbin/chkconfig --add varnishncsa
%service varnish restart
%service varnishlog restart
%service varnishncsa restart

%pre
%groupadd -g 241 %{name}
%useradd -u 241 -d /var/lib/%{name} -g %{name} -c "Varnishd User" %{name}

%postun
/sbin/ldconfig
if [ "$1" = "0" ]; then
	%userremove %{name}
	%groupremove %{name}
fi


%preun
if [ "$1" = "0" ]; then
	%service -q varnish stop
	%service -q varnishlog stop
	%service -q varnishncsa stop
	/sbin/chkconfig --del varnish
	/sbin/chkconfig --del varnishlog
	/sbin/chkconfig --del varnishncsa
fi

%files
%defattr(644,root,root,755)
%doc LICENSE README ChangeLog
%dir %{_sysconfdir}/%{name}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/default.vcl
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/varnish
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/varnishncsa
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/varnish
%attr(754,root,root) /etc/rc.d/init.d/varnish
%attr(754,root,root) /etc/rc.d/init.d/varnishlog
%attr(754,root,root) /etc/rc.d/init.d/varnishncsa
%attr(755,root,root) %{_sbindir}/varnishd
%attr(755,root,root) %{_bindir}/varnish*
%attr(755,root,root) %{_libdir}/libvarnish*.so.*.*.*
%attr(755,root,root) %{_libdir}/libvcl.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libvarnish*.so.1
%attr(755,root,root) %ghost %{_libdir}/libvcl.so.1
%{_mandir}/man1/*
%{_mandir}/man7/*
/var/lib/varnish
/var/run/varnish

%files devel
%defattr(644,root,root,755)
%{_includedir}/varnish
%attr(755,root,root) %{_libdir}/*.so
%{_libdir}/*.la
%{_pkgconfigdir}/*.pc

%files static
%defattr(644,root,root,755)
%{_libdir}/*.a
