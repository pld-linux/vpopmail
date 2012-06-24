#
# Conditional build:
%bcond_with	ldap	# with LDAP support
%bcond_with	mysql	# with MySQL support
%bcond_without	sqweb	# don't use sqwebmail
%bcond_with	ucspi	# use ucspi-tcp
#
Summary:	Virtual domains for qmail
Summary(es.UTF-8):	Dominios virtuales para qmail
Summary(pl.UTF-8):	Domeny wirtualne dla qmaila
Name:		vpopmail
Version:	5.4.0
%define	bver	rc1
Release:	0.%{bver}.2
License:	GPL v2
Group:		Networking/Daemons
Source0:	http://dl.sourceforge.net/vpopmail/%{name}-%{version}-%{bver}.tar.gz
# Source0-md5:	3a9edac0e60e4fb1e06d009bd11ade3b
Patch0:		%{name}-nonroot.patch
Patch1:		%{name}-missing-qmail.patch
URL:		http://inter7.com/vpopmail.html
BuildRequires:	autoconf
BuildRequires:	automake
%{?with_mysql:BuildRequires:	mysql-devel}
%{?with_ldap:BuildRequires:	openldap-devel >= 2.4.6}
%{?with_ucspi:BuildRequires:	ucspi-tcp >= 0.88}
BuildRequires:	rpmbuild(macros) >= 1.202
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
%{?with_ldap:Requires:	openldap}
Requires:	qmail >= 1.03
Requires:	qmail-pop3
%{?with_sqweb:Requires:	sqwebmail >= 3.0}
%{?with_ucspi:Requires:	ucspi-tcp >= 0.88}
Provides:	group(vchkpw)
Provides:	user(vpopmail)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		varqmail	/var/qmail
%define		dest		/var/lib/vpopmail

%description
vpopmail is a collection of programs to automate creation and
maintence of non /etc/passwd virtual domain email and POP accounts
for qmail installations.

%description -l es.UTF-8
vpopmail es una colección de programas para automatizar la creación
y el mantenimiento de dominios virtuales de E-mail y cuentas POP
independientes de /etc/passwd.

%description -l pl.UTF-8
vpopmail to kolekcja programów służących automatyzacji tworzenia
i zarządzania kontami pocztowymi w domenach wirtualnych, odrębnych
od haseł składowanych w pliku /etc/passwd.

%package devel
Summary:	Vpopmail development includes
Summary(es.UTF-8):	Ficheros de desarrollo de vpopmail
Summary(pl.UTF-8):	Pliki nagłówkowe bibliotek vpopmail
Group:		Development/Libraries
#Requires:	%{name}-libs = %{version}

%description devel
This package contains header files for vpopmail library.

%description devel -l es.UTF-8
El paquete vpopmail contiene todos los ficheros de inclusión.

%description devel -l pl.UTF-8
Ten pakiet zawiera pliki nagłówkowe biblioteki vpopmail.

%prep
%setup -q -n %{name}-%{version}-%{bver}
%patch0 -p1
%patch1 -p1

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
	%{?with_mysql:--enable-auth-module=mysql=y} \
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
%groupadd -g 121 vchkpw
%useradd -u 121 -g 121 -d /usr/share/empty -s /bin/false -c "VPOPMAIL user" vpopmail

%postun
if [ "$1" = "0" ]; then
	%userremove vpopmail
	%groupremove vchkpw
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog FAQ README* UPGRADE doc/doc_html doc/man_html ldap oracle
%attr(755,vpopmail,vchkpw) %{_sbindir}/*
%dir %{dest}
%attr(700,vpopmail,vchkpw) %dir %{dest}/domains
%{?with_ucspi:%attr(700,vpopmail,vchkpw) %dir /etc/vpopmail}

%files devel
%defattr(644,root,root,755)
%{_libdir}/libvpopmail.a
%{_includedir}/vpopmail
