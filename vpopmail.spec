# TODO: uid/gid 70 are reserved for other purposes (uid_gid.db.txt)
#       update (at least 5.3.4 was available some time ago)

# TODO: give them some descriptive comments
%bcond_with ldap
%bcond_with mysql
%bcond_without sqweb
%bcond_with ucspi

Summary:	Virtual domains for qmail
Summary(es):	Dominios virtuales para qmail
Summary(pl):	Domeny wirtualne dla qmaila
Name:		vpopmail
Version:	5.3.3
Release:	0.2
License:	GPL v2
Group:		Networking/Daemons
Source0:	http://www.inter7.com/devel/%{name}-%{version}.tar.gz
# Source0-md5:	fa7c7d46c673da7e955311d618f6302e
Patch0:		%{name}-nonroot.patch
Patch1:		%{name}-vmysql.patch
Patch2:		%{name}-missing-qmail.patch
URL:		http://inter7.com/vpopmail/
BuildRequires:	autoconf
BuildRequires:	automake
%{?with_mysql:BuildRequires:	mysql-devel}
%{?with_ldap:BuildRequires:	openldap-devel}
%{?with_ucspi:BuildRequires:	ucspi-tcp >= 0.88}
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(postun):	/usr/sbin/userdel
Requires(postun):	/usr/sbin/groupdel
%{?with_ldap:Requires:	openldap}
Requires:	qmail >= 1.03
Requires:	qmail-pop3
%{?with_sqweb:Requires:	sqwebmail >= 3.0}
%{?with_ucspi:Requires:	ucspi-tcp >= 0.88}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define	varqmail	/var/qmail

%description
vpopmail is a collection of programs to automate creation and
maintence of non /etc/passwd virtual domain email and POP accounts
for qmail installations.

%description -l es
vpopmail es una colección de programas para automatizar la creación
y el mantenimiento de dominios virtuales de E-mail y cuentas POP
independientes de /etc/passwd.

%description -l pl
vpopmail to kolekcja programów s³u¿±cych automatyzacji tworzenia
i zarz±dzania kontami pocztowymi w domenach wirtualnych, odrêbnych
od hase³ sk³adowanych w pliku /etc/passwd.

%package devel
Summary:	Vpopmail development includes
Summary(es):	Ficheros de desarrollo de vpopmail
Summary(pl):	Pliki nag³ówkowe bibliotek vpopmail
Group:		Development/Libraries
#Requires:	%{name}-libs = %{version}

%description devel
The vpopmail package contains all the include files.

%description devel -l es
El paquete vpopmail contiene todos los ficheros de inclusión.

%description devel -l pl
Pakiet zawiera pliki nag³ówkowe.

%define         dest		/var/lib/vpopmail

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
%{__aclocal}
%{__autoconf}
%{__automake}
%configure \
	--prefix=%{dest} \
	--enable-qmaildir=%{varqmail} \
	--enable-qmail-newu=%{varqmail}/bin/qmail-newu \
	--enable-qmail-inject=%{varqmail}/bin/qmail-inject \
	--enable-qmail-newmrh=%{varqmail}/bin/qmail-newmrh \
	%{?with_ucspi:--enable-roaming-users=y} \
	%{?with_sqweb:--enable-sqwebmail-pass=y} \
	%{?with_ldap:--enable-ldap=y} \
	%{?with_mysql:--enable-mysql=y} \
	--enable-vpopuser=vpopmail \
	--enable-vpopgroup=vchkpw \
	--enable-clear-passwd=n \
	--enable-logging=e \
	--enable-log-name=vpopmail \
	--enable-qmail-ext=y \
	--enable-defaultquota=100000 \
	%{?with_ucspi:--enable-tcpserver-file=/etc/vpopmail/tcp.smtp} \
	--enable-libdir=/usr/lib
%{__make}

%install
rm -rf $RPM_BUILD_ROOT

#%{__make} install \
#        DESTDIR=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{dest}/domains\
	   %{?with_ucspi:$RPM_BUILD_ROOT/etc/vpopmail/} \
	   $RPM_BUILD_ROOT%{_sbindir} \
	   $RPM_BUILD_ROOT%{_includedir}/vpopmail \
	   $RPM_BUILD_ROOT{%{_docdir},%{_libdir}}

install vpopmail.h	$RPM_BUILD_ROOT%{_includedir}/vpopmail
install config.h	$RPM_BUILD_ROOT%{_includedir}/vpopmail
install config.h	$RPM_BUILD_ROOT%{_includedir}/vpopmail/vpopmail_config.h
install vauth.h		$RPM_BUILD_ROOT%{_includedir}/vpopmail
install vchkpw vdelivermail clearopensmtp vadddomain \
	vdeldomain vpasswd vadduser vdeluser vaddaliasdomain vsetuserquota \
	vpopbull vdeloldusers vmoduser valias vuserinfo vmkpasswd vipmap \
	vdominfo vconvert vqmaillocal vkill \
	$RPM_BUILD_ROOT%{_sbindir}

install libvpopmail.a $RPM_BUILD_ROOT%{_libdir}
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
%{?with_ucspi: %attr(700,vpopmail,vchkpw) %dir /etc/vpopmail}

%files devel
%defattr(644,root,root,755)
%{_includedir}/vpopmail
%attr(755,root,root) %{_libdir}/libvpopmail.a
