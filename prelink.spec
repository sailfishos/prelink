Name:       prelink
Summary:    An ELF prelinking utility
Version:    0.4.6
Release:    4
Group:      System/Base
License:    GPLv2+
Source0:    http://people.redhat.com/jakub/prelink/prelink-20111012.tar.bz2
Source1:    prelink.conf
Source2:    prelink.cron
Source3:    prelink.sysconfig
Patch0:     prelink-20100106-arm-fix.patch
Patch1:     prelink-ld-linux-armhf.patch
Requires:   glibc >= 2.2.4-18
Requires:   coreutils
Requires:   findutils
Requires:   util-linux
Requires:   /bin/awk
Requires:   /bin/grep
BuildRequires:  elfutils-libelf-devel-static
BuildRequires:  glibc-static

%description
The prelink package contains a utility which modifies ELF shared libraries
and executables, so that far fewer relocations need to be resolved at runtime
and thus programs come up faster.

%package doc
Summary:   Documentation for %{name}
Group:     Documentation
Requires:  %{name} = %{version}-%{release}
Obsoletes: %{name}-docs

%description doc
Man pages for %{name}.

%prep
%setup -q -n %{name}

# prelink-20100106-arm-fix.patch
%patch0 -p1
%ifarch armv7hl armv7tnhl armv7nhl armv7thl 
# prelink-ld-linux-armhf.patch
%patch1 -p2
%endif

%build
sed -i -e '/^prelink_LDADD/s/$/ -lpthread/' src/Makefile.{am,in}

%configure --disable-static \
    --disable-shared

make %{?_smp_mflags}

%install
rm -rf %{buildroot}
%make_install

mkdir -p %{buildroot}%{_sysconfdir}/rpm
cp -a %{SOURCE1} %{buildroot}%{_sysconfdir}
mkdir -p %{buildroot}%{_sysconfdir}/{sysconfig,cron.daily,prelink.conf.d}
cp -a %{SOURCE2} %{buildroot}%{_sysconfdir}/cron.daily/prelink
cp -a %{SOURCE3} %{buildroot}%{_sysconfdir}/sysconfig/prelink
chmod 755 %{buildroot}%{_sysconfdir}/cron.daily/prelink
chmod 644 %{buildroot}%{_sysconfdir}/{sysconfig/prelink,prelink.conf}
cat > %{buildroot}%{_sysconfdir}/rpm/macros.prelink <<"EOF"
# rpm-4.1 verifies prelinked libraries using a prelink undo helper.
#       Note: The 2nd token is used as argv[0] and "library" is a
#       placeholder that will be deleted and replaced with the appropriate
#       library file path.
%%__prelink_undo_cmd     /usr/sbin/prelink prelink -y library
EOF
chmod 644 %{buildroot}%{_sysconfdir}/rpm/macros.prelink

mkdir -p %{buildroot}/var/{lib/misc,log/prelink}
touch %{buildroot}/var/lib/misc/prelink.full
touch %{buildroot}/var/lib/misc/prelink.quick
touch %{buildroot}/var/lib/misc/prelink.force
touch %{buildroot}/var/log/prelink/prelink.log
install -d %{buildroot}%{_defaultdocdir}/%{name}-%{version}
cp doc/prelink.pdf %{buildroot}%{_defaultdocdir}/%{name}-%{version}
echo "%{_defaultdocdir}/%{name}-%{version}/prelink.pdf" >> documentation.list

%check
#echo ====================TESTING=========================
#make -C testsuite check-harder
#make -C testsuite check-cycle
#echo ====================TESTING END=====================

%post
touch /var/lib/misc/prelink.force

%files
%defattr(-,root,root,-)
%license COPYING
%verify(not md5 size mtime) %config(noreplace) %{_sysconfdir}/prelink.conf
%verify(not md5 size mtime) %config(noreplace) %{_sysconfdir}/sysconfig/prelink
%{_sysconfdir}/rpm/macros.prelink
%dir %attr(0755,root,root) %{_sysconfdir}/prelink.conf.d
%{_sysconfdir}/cron.daily/prelink
%{_prefix}/sbin/prelink
%{_prefix}/bin/execstack
%attr(0644,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /var/lib/misc/prelink.full
%attr(0644,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /var/lib/misc/prelink.quick
%attr(0644,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /var/lib/misc/prelink.force
%dir /var/log/prelink
%attr(0644,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /var/log/prelink/prelink.log

%files doc
%defattr(-,root,root,-)
%{_mandir}/man8/%{name}.*
%{_mandir}/man8/execstack.*
%{_docdir}/%{name}-%{version}
