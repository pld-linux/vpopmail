# TODO: uid/gid 70 are reserved for other purposes (uid_gid.db.txt)
#       update (at least 5.3.4 was available some time ago)

# for tests
%define		_without_ldap	1
%define		_without_mysql  1
%define		_without_ucspi	1

Summary:	virtual domains for qmail
Summary(pl):	domeny wirtualne dla qmaila
Name:		vpopmail
Version:	5.3.3
Release:	0.01
License:	GPL v2
Group:		Networking/Daemons
Source0:	http://www.inter7.com/devel/%{name}-%{version}.tar.gz
# Source0-md5:	fa7c7d46c673da7e955311d618f6302e
Patch0:		%{name}-nonroot.patch
URL:		http://inter7.com/vpopmail/
BuildRequires:	autoconf
BuildRequires:	automake
%{!?_without_mysql:BuildRequires:	mysql-devel}
%{!?_without_ldap:BuildRequires:	openldap-devel}
BuildRequires:	qmail >= 1.03
%{!?_without_ucspi:BuildRequires:	ucspi-tcp >= 0.88}
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(postun):	/usr/sbin/userdel
Requires(postun):	/usr/sbin/groupdel
%{!?_without_ldap:Requires:	openldap}
Requires:	qmail >= 1.03
Requires:	qmail-pop3d
%{!?_without_sqweb:Requires:	sqwebmail >= 3.0}
%{!?_without_ucspi:Requires:	ucspi-tcp >= 0.88}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
vpopmail is a collection of programs to automate creation and
maintence of non /etc/passwd virutal domain email and pop accounts
for qmail installations.

%description -l pl
vpopmail to kolekcja programów s³u¿±cych automatyzacji tworzenia
i zarz±dzania kontami pocztowymi w domenach wirtualnych, odrêbnych
od hase³ sk³adowanych w pliku /etc/passwd

%package devel
Summary:	Vpopmail development includes
Summary(pl):	Pliki nag³ówkowe bibliotek vpopmail
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}

%description devel
The vpopmail package contains all the include files.

%description devel -l pl
Pakiet zawiera pliki nag³ówkowe.

%define         dest		/var/lib/vpopmail

%prep
%setup -q
%patch0 -p1

%build
%{__aclocal}
%{__autoconf}
%{__automake}
%configure \
	--prefix=%{dest} \
	%{!?_without_ucspi:--enable-roaming-users=y} \
	%{!?_without_sqweb:--enable-sqwebmail-pass=y} \
	%{!?_without_ldap:--enable-ldap=y} \
	%{!?_without_mysql:--enable-mysql=y} \
	--enable-vpopuser=vpopmail \
	--enable-vpopgroup=vchkpw \
	--enable-clear-passwd=n \
	--enable-logging=e \
	--enable-log-name=vpopmail \
	--enable-qmail-ext=y \
	--enable-defaultquota=100000 \
	%{!?_without_ucspi:--enable-tcpserver-file=/etc/vpopmail/tcp.smtp} \
	--enable-libdir=/usr/lib
%{__make}

%install
rm -rf $RPM_BUILD_ROOT

#%{__make} install \
#        DESTDIR=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{dest}/domains\
	   %{!?_without_ucspi: $RPM_BUILD_ROOT/etc/vpopmail/} \
	   $RPM_BUILD_ROOT%{_sbindir} \
	   $RPM_BUILD_ROOT%{_includedir}/vpopmail \
	   $RPM_BUILD_ROOT%{_docdir}

install vpopmail.h	$RPM_BUILD_ROOT%{_includedir}/vpopmail
install config.h	$RPM_BUILD_ROOT%{_includedir}/vpopmail
install config.h	$RPM_BUILD_ROOT%{_includedir}/vpopmail/vpopmail_config.h
install vauth.h		$RPM_BUILD_ROOT%{_includedir}/vpopmail
install vchkpw vdelivermail clearopensmtp vadddomain \
	vdeldomain vpasswd vadduser vdeluser vaddaliasdomain vsetuserquota \
	vpopbull vdeloldusers vmoduser valias vuserinfo vmkpasswd vipmap \
	vdominfo vconvert vqmaillocal vkill \
	$RPM_BUILD_ROOT%{_sbindir}

#install $RPM_BUILD_ROOT%{dest}/domains

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ -n "`getgid vchkpw`" ]; then
	if [ "`getgid vchkpw`" != "70" ]; then
		echo "Error: group vpopmail doesn't have gid=70. Correct this before installing vpopmail." 1>&2
		exit 1
	fi
else
	echo "Adding group vchkpw GID=70."
	/usr/sbin/groupadd -g 70 vchkpw || exit 1
fi
if [ -n "`id -u named 2>/dev/null`" ]; then
	if [ "`id -u vpopmail`" != "70" ]; then
		echo "Error: user vpopmail doesn't have uid=70. Correct this before installing vpopmail." 1>&2
		exit 1
	fi
else
	echo "Adding user vpopmail UID=70."
	/usr/sbin/useradd -u 70 -g 70 -d /dev/null -s /bin/false -c "VPOPMAIL user" vpopmail || exit 1
fi

%postun
if [ "$1" = "0" ]; then
	echo "Removing user vpopmail."
	/usr/sbin/userdel vpopmail
	echo "Removing group vpopmail."
	/usr/sbin/groupdel vchkpw
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog FAQ NEWS TODO UPGRADE UPGRADE.tren README.* doc/doc_html doc/man_html ldap oracle
%attr(755,vpopmail,vchkpw) %{_sbindir}/*
%dir %{dest}
%attr(700,vpopmail,vchkpw) %dir %{dest}/domains
%{!?_without_ucspi: %attr(700,vpopmail,vchkpw) %dir /etc/vpopmail}

%files devel
%defattr(644,root,root,755)
%{_includedir}/vpopmail
