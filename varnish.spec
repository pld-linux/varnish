Summary:	Varnish is a high-performance HTTP accelerator
Name:		varnish
Version:	1.0.2
Release:	0.7
License:	BSD-like
Group:		Daemons
URL:		http://www.varnish-cache.org/
Source0:	http://downloads.sourceforge.net/varnish/%{name}-%{version}.tar.gz
# Source0-md5:	d905f63a6665224c370154eb006ca4cc
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libtool
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

%package devel
Summary:	Header files for varnish library
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Header files for varnish library.

%package static
Summary:	Static varnish library
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static varnish library.

%prep
%setup -q

%build
export CPPFLAGS="-I/usr/include/ncurses"
./autogen.sh
%configure
%{__make}

sed -e ' s/8080/80/g ' etc/vcl.conf > redhat/vcl.conf

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{_sbindir}
install -d $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
install -d $RPM_BUILD_ROOT%{_sysconfdir}/varnish
install -d $RPM_BUILD_ROOT%{_sysconfdir}/init.d
install -d $RPM_BUILD_ROOT/etc/sysconfig
install -d $RPM_BUILD_ROOT/var/lib/varnish

install INSTALL $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/INSTALL
install LICENSE $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/LICENSE
install README $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/README
install ChangeLog $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/ChangeLog
install redhat/README.redhat $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/README.redhat
install redhat/vcl.conf $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/vcl.example.conf
install redhat/vcl.conf $RPM_BUILD_ROOT%{_sysconfdir}/varnish/vcl.conf
install redhat/varnish.sysconfig $RPM_BUILD_ROOT/etc/sysconfig/varnish
install redhat/varnish.initrc $RPM_BUILD_ROOT%{_sysconfdir}/init.d/varnish

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
%doc %{_docdir}/%{name}-%{version}
%config(noreplace) %{_sysconfdir}/vcl.conf
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
%{_var}/lib/varnish
%{_mandir}/man1/varnishd.1*
%{_mandir}/man1/varnishhist.1*
%{_mandir}/man1/varnishlog.1*
%{_mandir}/man1/varnishncsa.1*
%{_mandir}/man1/varnishstat.1*
%{_mandir}/man1/varnishtop.1*
%{_mandir}/man7/vcl.7*

%files devel
%defattr(644,root,root,755)
%{_libdir}/libvarnish.la
%{_libdir}/libvarnishapi.la
%{_libdir}/libvcl.la
%attr(755,root,root) %{_libdir}/libvarnish.so
%attr(755,root,root) %{_libdir}/libvarnishapi.so
%attr(755,root,root) %{_libdir}/libvcl.so

%files static
%defattr(644,root,root,755)
%{_libdir}/libvarnish.a
%{_libdir}/libvarnishapi.a
%{_libdir}/libvcl.a
