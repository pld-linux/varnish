Summary:	Varnish - a high-performance HTTP accelerator
Summary(pl):	Varnish - wydajny akcelerator HTTP
Name:		varnish
Version:	1.0.2
Release:	0.8
License:	BSD-like
Group:		Daemons
Source0:	http://dl.sourceforge.net/varnish/%{name}-%{version}.tar.gz
# Source0-md5:	d905f63a6665224c370154eb006ca4cc
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}.conf
URL:		http://www.varnish-cache.org/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libstdc++-devel
BuildRequires:	libtool >= 2:1.5
BuildRequires:	ncurses-devel
Requires(post):	/sbin/ldconfig
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/%{name}

%description
The goal of the Varnish project is to develop a state-of-the-art,
high-performance HTTP accelerator.

Varnish is targeted primarily at the FreeBSD 6 and Linux 2.6
platforms, and will take full advantage of the advanced I/O features
offered by these operating systems.

%description -l pl
Celem projektu Varnish jest stworzenie wydajnego akceleratora HTTP.

Varnish jest tworzony g³ównie z my¶l± o platformach FreeBSD 6 i Linux
2.6 i bêdzie wykorzystywa³ w pe³ni zaawansowane mo¿liwo¶ci we/we
oferowane przez te systemy operacyjne.

%package devel
Summary:	Header files for varnish library
Summary(pl):	Pliki nag³ówkowe biblioteki varnish
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Header files for varnish library.

%description devel -l pl
Pliki nag³ówkowe biblioteki varnish.

%package static
Summary:	Static varnish library
Summary(pl):	Statyczna biblioteka varnish
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static varnish library.

%description static -l pl
Statyczna biblioteka varnish.

%prep
%setup -q

%build
export CPPFLAGS="-I/usr/include/ncurses"
./autogen.sh
%configure
%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

# make dirs after make install to know which ones needs spec and which ones make install
install -d $RPM_BUILD_ROOT{%{_sysconfdir},/etc/{rc.d/init.d,sysconfig},/var/lib/varnish}

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/varnish
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/varnish
install %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/vcl.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/ldconfig
/sbin/chkconfig --add varnish
%service %{name} restart

%postun	-p /sbin/ldconfig

%preun
if [ "$1" = "0" ]; then
	%service -q %{name} stop
	/sbin/chkconfig --del %{name}
fi

%files
%defattr(644,root,root,755)
%doc INSTALL LICENSE README ChangeLog
%dir %{_sysconfdir}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/vcl.conf
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/varnish
%attr(754,root,root) /etc/rc.d/init.d/varnish
%attr(755,root,root) %{_sbindir}/varnishd
%attr(755,root,root) %{_bindir}/varnishhist
%attr(755,root,root) %{_bindir}/varnishlog
%attr(755,root,root) %{_bindir}/varnishncsa
%attr(755,root,root) %{_bindir}/varnishstat
%attr(755,root,root) %{_bindir}/varnishtop
%attr(755,root,root) %{_libdir}/libvarnish.so.0.0.0
%attr(755,root,root) %{_libdir}/libvarnishapi.so.0.0.0
%attr(755,root,root) %{_libdir}/libvcl.so.0.0.0
/var/lib/varnish
%{_mandir}/man1/varnishd.1*
%{_mandir}/man1/varnishhist.1*
%{_mandir}/man1/varnishlog.1*
%{_mandir}/man1/varnishncsa.1*
%{_mandir}/man1/varnishstat.1*
%{_mandir}/man1/varnishtop.1*
%{_mandir}/man7/vcl.7*

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libvarnish.so
%attr(755,root,root) %{_libdir}/libvarnishapi.so
%attr(755,root,root) %{_libdir}/libvcl.so
%{_libdir}/libvarnish.la
%{_libdir}/libvarnishapi.la
%{_libdir}/libvcl.la

%files static
%defattr(644,root,root,755)
%{_libdir}/libvarnish.a
%{_libdir}/libvarnishapi.a
%{_libdir}/libvcl.a
