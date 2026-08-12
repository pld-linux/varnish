# Conditional build:
%bcond_without	doc		# build documentation
%bcond_without	tests		# build without tests. binds daemon on 127.0.0.1 9080, 9081, 9001 ports
%bcond_with	static_libs	# build static libraries
%bcond_with	source		# build source package

Summary:	Varnish - a high-performance HTTP accelerator
Summary(pl.UTF-8):	Varnish - wydajny akcelerator HTTP
Name:		varnish
Version:	9.0.3
Release:	2
License:	BSD
Group:		Networking/Daemons/HTTP
Source0:	https://github.com/varnish/varnish/releases/download/%{name}-%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	9830a825e8d808544855a521e89783ac
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
BuildRequires:	libtool >= 2:2.0
BuildRequires:	ncurses-devel
BuildRequires:	pcre-devel
BuildRequires:	pkgconfig
BuildRequires:	rpmbuild(macros) >= 1.647
BuildRequires:	sed >= 4.0
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
Obsoletes:	varnish-libvmod-cookie < 9.0
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

%package source
Summary:	Source code of Varnish for building VMODs
Group:		Documentation
Requires:	%{name}-devel = %{version}-%{release}

%description source
Source code of Varnish for building VMODs.

%prep
%setup -q
#%%patch100 -p0
%patch -P0 -p1

%{__sed} -i -e '1s,^#!.*python3,#!%{__python3},' \
	lib/libvcc/vmodtool.py \
	lib/libvsc/vsctool.py

%build
export CPPFLAGS="-I/usr/include/ncurses"
%{__aclocal} -I m4 -I .
%{__libtoolize}
%{__autoheader}
%{__automake}
%{__autoconf}
%configure \
%ifarch hppa s390 sparc ppc
	--disable-jemalloc
%endif

%{__make} V=1

%if %{with tests}
%{__make} check \
	LD_LIBRARY_PATH="../../lib/libvarnish/.libs:../../lib/libvarnishcompat/.libs:../../lib/libvarnishapi/.libs:../../lib/libvcl/.libs"
%endif

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	V=1 \
	INSTALL="install -p" \
	DESTDIR=$RPM_BUILD_ROOT

# make dirs after make install to know which ones needs spec and which ones make install
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/varnish,/etc/{logrotate.d,rc.d/init.d,sysconfig},/var/{run,lib}/varnish} \
	$RPM_BUILD_ROOT/var/log/{archive/,}varnish \
	$RPM_BUILD_ROOT%{systemdtmpfilesdir}

install -p %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/varnish
install -p %{SOURCE3} $RPM_BUILD_ROOT/etc/rc.d/init.d/varnishncsa
cp -p %{SOURCE4} $RPM_BUILD_ROOT/etc/sysconfig/varnish
cp -p %{SOURCE5} $RPM_BUILD_ROOT/etc/sysconfig/varnishncsa
cp -p %{SOURCE6} $RPM_BUILD_ROOT/etc/logrotate.d/varnish
cp -p %{SOURCE8} $RPM_BUILD_ROOT%{systemdtmpfilesdir}/%{name}.conf
touch $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/secret

%{__rm} $RPM_BUILD_ROOT%{_libdir}/*.la
%{__rm} $RPM_BUILD_ROOT%{_libdir}/%{name}/vmods/*.la

%if %{with source}
# prepare tree for VMOD build
install -d $RPM_BUILD_ROOT%{_usrsrc}/%{name}-%{version}/{include,bin/{varnishtest,varnishd},lib/libvmod_std}

# add extra headers
cp -pn include/*.h $RPM_BUILD_ROOT%{_usrsrc}/%{name}-%{version}/include
cp -p bin/varnishd/*.h $RPM_BUILD_ROOT%{_usrsrc}/%{name}-%{version}/bin/varnishd

for a in $RPM_BUILD_ROOT%{_includedir}/%{name}/*.h; do
	f=${a#$RPM_BUILD_ROOT}
	ln -sf $f $RPM_BUILD_ROOT%{_usrsrc}/%{name}-%{version}/include
done

ln -s %{_bindir}/varnishtest $RPM_BUILD_ROOT%{_usrsrc}/%{name}-%{version}/bin/varnishtest
ln -s %{_sbindir}/varnishd $RPM_BUILD_ROOT%{_usrsrc}/%{name}-%{version}/bin/varnishd
cp -p lib/libvmod_std/vmod.py $RPM_BUILD_ROOT%{_usrsrc}/%{name}-%{version}/lib/libvmod_std

# add pkg config variable for eash access
%{__sed} -i -e '/^vmoddir/a srcdir=%{_usrsrc}/%{name}-%{version}' \
	$RPM_BUILD_ROOT%{_pkgconfigdir}/varnishapi.pc
%endif

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
%doc LICENSE README.md ChangeLog etc/*.vcl
%dir %attr(750,root,root) %{_sysconfdir}/%{name}
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
%attr(755,root,root) %{_bindir}/varnishlog-json
%attr(755,root,root) %{_bindir}/varnishncsa
%attr(755,root,root) %{_bindir}/varnishstat
%attr(755,root,root) %{_bindir}/varnishstat_help_gen
%attr(755,root,root) %{_bindir}/varnishtest
%attr(755,root,root) %{_bindir}/varnishtop
%attr(755,root,root) %{_bindir}/vtest
%dir %{_libdir}/%{name}
%dir %{_libdir}/%{name}/vmods
%{_libdir}/%{name}/vmods/libvmod_blob.so
%{_libdir}/%{name}/vmods/libvmod_cookie.so
%{_libdir}/%{name}/vmods/libvmod_directors.so
%{_libdir}/%{name}/vmods/libvmod_h2.so
%{_libdir}/%{name}/vmods/libvmod_math.so
%{_libdir}/%{name}/vmods/libvmod_proxy.so
%{_libdir}/%{name}/vmods/libvmod_purge.so
%{_libdir}/%{name}/vmods/libvmod_std.so
%{_libdir}/%{name}/vmods/libvmod_tls.so
%{_libdir}/%{name}/vmods/libvmod_unix.so
%{_libdir}/%{name}/vmods/libvmod_vtc.so
%dir %{_datadir}/varnish
%dir %{_datadir}/varnish/vcc
%{_datadir}/varnish/vcc/vmod_blob.vcc
%{_datadir}/varnish/vcc/vmod_cookie.vcc
%{_datadir}/varnish/vcc/vmod_directors.vcc
%{_datadir}/varnish/vcc/vmod_h2.vcc
%{_datadir}/varnish/vcc/vmod_math.vcc
%{_datadir}/varnish/vcc/vmod_proxy.vcc
%{_datadir}/varnish/vcc/vmod_purge.vcc
%{_datadir}/varnish/vcc/vmod_std.vcc
%{_datadir}/varnish/vcc/vmod_tls.vcc
%{_datadir}/varnish/vcc/vmod_unix.vcc
%{_datadir}/varnish/vcc/vmod_vtc.vcc
%dir %{_datadir}/varnish/vcl
%{_datadir}/varnish/vcl/devicedetect.vcl
%{_mandir}/man1/varnishadm.1*
%{_mandir}/man1/varnishd.1*
%{_mandir}/man1/varnishhist.1*
%{_mandir}/man1/varnishlog.1*
%{_mandir}/man1/varnishncsa.1*
%{_mandir}/man1/varnishstat.1*
%{_mandir}/man1/varnishtest.1*
%{_mandir}/man1/varnishtop.1*
%{_mandir}/man3/vmod_blob.3*
%{_mandir}/man3/vmod_cookie.3*
%{_mandir}/man3/vmod_directors.3*
%{_mandir}/man3/vmod_h2.3*
%{_mandir}/man3/vmod_math.3*
%{_mandir}/man3/vmod_proxy.3*
%{_mandir}/man3/vmod_purge.3*
%{_mandir}/man3/vmod_std.3*
%{_mandir}/man3/vmod_unix.3*
%{_mandir}/man3/vmod_vtc.3*
%{_mandir}/man7/varnish-cli.7*
%{_mandir}/man7/varnish-counters.7*
%{_mandir}/man7/vcl.7*
%{_mandir}/man7/vcl-backend.7*
%{_mandir}/man7/vcl-probe.7*
%{_mandir}/man7/vcl-step.7*
%{_mandir}/man7/vcl-var.7*
%{_mandir}/man7/vsl.7*
%{_mandir}/man7/vsl-query.7*
%{_mandir}/man7/vtc.7*
%dir /var/lib/varnish
%dir /var/run/varnish
%{systemdtmpfilesdir}/%{name}.conf

%dir %attr(751,root,root) /var/log/varnish
%dir %attr(750,root,root) /var/log/archive/varnish

%files libs
%defattr(644,root,root,755)
%{_libdir}/libvarnishapi.so.*.*.*
%ghost %{_libdir}/libvarnishapi.so.3

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_datadir}/varnish/vmodtool.py
%attr(755,root,root) %{_datadir}/varnish/vsctool.py
%{_includedir}/varnish
%{_libdir}/libvarnishapi.so
%{_pkgconfigdir}/varnishapi.pc
%{_aclocaldir}/varnish-legacy.m4
%{_aclocaldir}/varnish.m4

%if %{with static_libs}
%files static
%defattr(644,root,root,755)
%{_libdir}/libvarnishapi.a
%endif

%if %{with source}
%files source
%defattr(644,root,root,755)
%{_usrsrc}/%{name}-%{version}
%endif
