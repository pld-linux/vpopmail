Summary:	virtual domains for qmail
Summary(pl):	domeny wirtualne dla qmaila
Name:		vpopmail
Version:	5.3.3
Release:	0.1
License:	GPL
Group:		Networking/Daemons
Source0:	http://www.inter7.com/devel/%{name}-%{version}.tar.gz
URL:		http://inter7.com/vpopmail/
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
vpopmail is a collection of programs to automate creation and
maintence of non /etc/passwd virutal domain email and pop accounts
for qmail installations.

%description -l pl
vpopmail to kolekcja programów s³u¿±cych automatyzacji tworzenia
i zarz±dzania kontami pocztowymi w domenach wirtualnych, odrêbnych
od hase³ sk³adowanych w pliku /etc/passwd

%define         destination	/var/lib/vpopmail

%prep
getuid () {
    id $1|sed -e 's/^uid=//' -e 's/(.*//'
}

if [ $(getuid) != 0 ]; then
    echo You must be root to build this package
    exit 2
fi

%setup -q

%build

getgroup() {
    id $1|sed -e 's/.*gid=[^ ]*(//' -e 's/).*//'
}

group_exist() {
    groupmod $1 > /dev/null 2>&1
}

user_exist() {
    id $1 > /dev/null 2>&1 
}

if ! group_exist vchkpw; then
    groupadd -g 66 vchkpw
fi

if ! user_exist vpopmail; then
    useradd -u 66 -d %{destination} -g vchkpw -s /bin/sh -m vpopmail
elif [ "$(getgroup vpopmail)" != "vchkpw" ]; then
    usermod -g vchkpw vpopmail
fi

%configure2_13 \
	--prefix=%{destination} \
	--enable-vpopuser=vpopmail \
	--enable-vpopgroup=vchkpw \
	--enable-roaming-users=y \
	--enable-clear-passwd=n \
	--enable-logging=e \
	--enable-log-name=vpopmail \
	--enable-qmail-ext=y \
	--enable-defaultquota=100000 \
	--enable-mysql=y \
	--enable-libdir=/usr/lib
	#       --enable-default-domain=name 
	
%{__make}

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT/%{destination}
chown vpopmail.vchkpw $RPM_BUILD_ROOT/%{destination}
make DESTDIR=$RPM_BUILD_ROOT install-strip

%clean
rm -rf $RPM_BUILD_ROOT

%post

%postun

%files
%defattr(644,root,root,755)
%doc *.gz
%attr(755,vpopmail,vchkpw) %{_?}/*
