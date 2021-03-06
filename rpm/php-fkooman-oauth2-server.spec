%global composer_vendor         fkooman
%global composer_project        oauth2-server
%global composer_namespace      %{composer_vendor}/OAuth/Server

%global github_owner            fkooman
%global github_name             php-oauth2-server

%global commit0 3aac9a41a9c3d47a0b5e91345cb78abfa282736c
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

Name:       php-%{composer_vendor}-%{composer_project}
Version:    1.0.0
Release:    1%{?dist}
Summary:    Very simple OAuth 2.0 server

Group:      System Environment/Libraries
License:    MIT

URL:        https://github.com/%{github_owner}/%{github_name}
Source0:    %{url}/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz

BuildArch:  noarch

BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-libsodium
BuildRequires:  php-date
BuildRequires:  php-hash
BuildRequires:  php-json
BuildRequires:  php-pcre
BuildRequires:  php-pdo
BuildRequires:  php-standard
BuildRequires:  php-composer(fedora/autoloader)
BuildRequires:  php-composer(paragonie/constant_time_encoding)
BuildRequires:  %{_bindir}/phpunit

Requires:   php(language) >= 5.4.0
Requires:   php-libsodium
Requires:   php-date
Requires:   php-hash
Requires:   php-json
Requires:   php-pcre
Requires:   php-pdo
Requires:   php-standard
Requires:   php-composer(fedora/autoloader)
Requires:   php-composer(paragonie/constant_time_encoding)

Provides:   php-composer(%{composer_vendor}/%{composer_project}) = %{version}

%description
This is a very simple OAuth 2.0 server for integration in your own 
application. It has minimal dependencies, but still tries to be secure. 
The main purpose is to be compatible with PHP 5.4.

%prep
%setup -n %{github_name}-%{commit0}

%build
cat <<'AUTOLOAD' | tee src/autoload.php
<?php
require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Autoload::addPsr4('fkooman\\OAuth\\Server\\', __DIR__);
\Fedora\Autoloader\Dependencies::required(array(
    '%{_datadir}/php/ParagonIE/ConstantTime/autoload.php',
));
AUTOLOAD

%install
mkdir -p %{buildroot}%{_datadir}/php/%{composer_namespace}
cp -pr src/* %{buildroot}%{_datadir}/php/%{composer_namespace}

%check
mkdir vendor
cat << 'EOF' | tee vendor/autoload.php
<?php
require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Dependencies::required(array(
    '%{buildroot}/%{_datadir}/php/%{composer_namespace}/autoload.php',
));
\Fedora\Autoloader\Autoload::addPsr4('fkooman\\OAuth\\Server\\Tests\\', dirname(__DIR__) . '/tests');
EOF

%{_bindir}/phpunit --verbose

%files
%dir %{_datadir}/php/fkooman
%dir %{_datadir}/php/fkooman/OAuth
%{_datadir}/php/%{composer_namespace}
%doc README.md CHANGES.md composer.json
%license LICENSE

%changelog
* Thu Jul 06 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-1
- initial package
