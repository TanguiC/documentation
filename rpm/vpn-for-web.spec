%global composer_vendor         eduvpn
%global composer_project        vpn-for-web
%global composer_namespace      SURFnet/VPN/Web

%global github_owner            eduvpn
%global github_name             vpn-for-web
%global github_commit           4e72c3943d7d462d6b84255e108813120dc33c0b
%global github_short            %(c=%{github_commit}; echo ${c:0:7})

Name:       vpn-for-web
Version:    1.0.0
Release:    0.40%{?dist}
Summary:    VPN for Web

Group:      Applications/Internet
License:    AGPLv3+

URL:        https://github.com/%{github_owner}/%{github_name}
Source0:    %{url}/archive/%{github_commit}/%{name}-%{version}-%{github_short}.tar.gz
Source1:    %{name}-httpd.conf

BuildArch:  noarch
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n) 

BuildRequires:  %{_bindir}/phpunit
BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-filter
BuildRequires:  php-pecl-imagick
BuildRequires:  php-json
BuildRequires:  php-libsodium
BuildRequires:  php-mbstring
BuildRequires:  php-pcre
BuildRequires:  php-session
BuildRequires:  php-spl
BuildRequires:  php-standard
BuildRequires:  php-composer(twig/twig) < 2
BuildRequires:  php-composer(fkooman/oauth2-client)
BuildRequires:  php-composer(fkooman/secookie)
BuildRequires:  php-composer(paragonie/constant_time_encoding)
BuildRequires:  php-composer(fedora/autoloader)

Requires:   php(language) >= 5.4.0
Requires:   php-cli
Requires:   php-filter
Requires:   php-pecl-imagick
Requires:   php-json
Requires:   php-libsodium
Requires:   php-mbstring
Requires:   php-pcre
Requires:   php-session
Requires:   php-spl
Requires:   php-standard
Requires:   php-composer(twig/twig) < 2
Requires:   php-composer(fkooman/oauth2-client)
Requires:   php-composer(fkooman/secookie)
Requires:   php-composer(paragonie/constant_time_encoding)
Requires:   php-composer(fedora/autoloader)
%if 0%{?fedora} >= 24
Requires:   httpd-filesystem
%else
# EL7 does not have httpd-filesystem
Requires:   httpd
%endif

Requires(post): /usr/sbin/semanage
Requires(postun): /usr/sbin/semanage

%description
VPN for Web.

%prep
%setup -qn %{github_name}-%{github_commit} 

sed -i "s|require_once sprintf('%s/vendor/autoload.php', dirname(__DIR__));|require_once '%{_datadir}/%{name}/src/%{composer_namespace}/autoload.php';|" bin/*
sed -i "s|require_once sprintf('%s/vendor/autoload.php', dirname(__DIR__));|require_once '%{_datadir}/%{name}/src/%{composer_namespace}/autoload.php';|" web/*.php
sed -i "s|dirname(__DIR__)|'%{_datadir}/%{name}'|" bin/*

%build
cat <<'AUTOLOAD' | tee src/autoload.php
<?php
require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Autoload::addPsr4('SURFnet\\VPN\\Web\\', __DIR__);
\Fedora\Autoloader\Dependencies::required(array(
    '%{_datadir}/php/Twig/autoload.php',
    '%{_datadir}/php/fkooman/OAuth/Client/autoload.php',
    '%{_datadir}/php/fkooman/SeCookie/autoload.php',
    '%{_datadir}/php/ParagonIE/ConstantTime/autoload.php',
));
AUTOLOAD

%install
install -m 0644 -D -p %{SOURCE1} %{buildroot}%{_sysconfdir}/httpd/conf.d/%{name}.conf

mkdir -p %{buildroot}%{_datadir}/%{name}
cp -pr web views %{buildroot}%{_datadir}/%{name}
mkdir -p %{buildroot}%{_datadir}/%{name}/src/%{composer_namespace}
cp -pr src/* %{buildroot}%{_datadir}/%{name}/src/%{composer_namespace}

mkdir -p %{buildroot}%{_sysconfdir}/%{name}
cp -pr config/config.php.example %{buildroot}%{_sysconfdir}/%{name}/config.php
ln -s ../../../etc/%{name} %{buildroot}%{_datadir}/%{name}/config

mkdir -p %{buildroot}%{_localstatedir}/lib/%{name}
ln -s ../../../var/lib/%{name} %{buildroot}%{_datadir}/%{name}/data

mkdir -p %{buildroot}%{_bindir}
(
cd bin
for phpFileName in $(ls *)
do
    binFileName=$(basename ${phpFileName} .php)
    cp -pr ${phpFileName} %{buildroot}%{_bindir}/%{name}-${binFileName}
    chmod 0755 %{buildroot}%{_bindir}/%{name}-${binFileName}
done
)

%post
semanage fcontext -a -t httpd_sys_rw_content_t '%{_localstatedir}/lib/%{name}(/.*)?' 2>/dev/null || :
restorecon -R %{_localstatedir}/lib/%{name} || :

# remove template cache if it is there
rm -rf %{_localstatedir}/lib/%{name}/tpl/* >/dev/null 2>/dev/null || :

%postun
if [ $1 -eq 0 ] ; then  # final removal
semanage fcontext -d -t httpd_sys_rw_content_t '%{_localstatedir}/lib/%{name}(/.*)?' 2>/dev/null || :
fi

%files
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf
%dir %attr(0750,root,apache) %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/config.php
%{_bindir}/*
%{_datadir}/%{name}/src
%{_datadir}/%{name}/web
%{_datadir}/%{name}/data
%{_datadir}/%{name}/views
%{_datadir}/%{name}/config
%dir %attr(0700,apache,apache) %{_localstatedir}/lib/%{name}
%doc README.md CHANGES.md composer.json config/config.php.example
%license LICENSE

%changelog
* Wed Jun 14 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.40
- rebuilt

* Wed Jun 07 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.39
- rebuilt

* Wed Jun 07 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.38
- rebuilt

* Mon Jun 05 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.37
- rebuilt

* Sun Jun 04 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.36
- rebuilt

* Sun Jun 04 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.35
- rebuilt

* Sat Jun 03 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.34
- rebuilt

* Fri Jun 02 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.33
- rebuilt

* Thu Jun 01 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.32
- rebuilt

* Wed May 31 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.31
- rebuilt

* Tue May 30 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.30
- rebuilt

* Tue May 30 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.29
- rebuilt

* Tue May 30 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.28
- rebuilt

* Tue May 30 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.27
- rebuilt
