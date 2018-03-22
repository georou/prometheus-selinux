%global  prometheus_user	prometheus

# Relabel files
%global relabel_files() %{_sbindir}/restorecon -RF %{_sysconfdir}/prometheus %{_usr}/local/bin/promtool %{_usr}/local/bin/prometheus /opt/prometheus &> /dev/null || :

%global selinux_policyver 3.13.1-40

Name:           prometheus
Version:        2.2.1
Release:        1%{?dist}
Summary:        Prometheus CentOS 7 rpm package

License:        ASL 2.0
URL:            http://prometheus.io
Source0:        %{name}-%{version}.linux-amd64.tar.gz
Source1:	%{name}.service

BuildRequires:	systemd
Requires:	systemd
Requires(pre):	shadow-utils
Requires(post): selinux-policy-base >= %{selinux_policyver}, policycoreutils, systemd

%description
Install prometheus from source

%prep
%setup -q -n %{name}-%{version}.linux-amd64

%install
if [ -d %{buildroot} ] ; then
  rm -rf %{buildroot}
fi

install -p -d -m 0750 %{buildroot}/opt/prometheus/{consoles,console_libraries}

install -Dp -m 0755 promtool %{buildroot}%{_usr}/local/bin/promtool
install -Dp -m 0755 prometheus %{buildroot}%{_usr}/local/bin/prometheus

install -p -m 0755 consoles/* %{buildroot}/opt/prometheus/consoles
install -p -m 0755 console_libraries/* %{buildroot}/opt/prometheus/console_libraries

install -Dp -m 0640 prometheus.yml %{buildroot}%{_sysconfdir}/prometheus/prometheus.yml

install -Dp -m 0644 %{SOURCE1} %{buildroot}/usr/lib/systemd/system/%{name}.service


%pre
getent group %{prometheus_user} >/dev/null || groupadd -r %{prometheus_user}
getent passwd %{prometheus_user} >/dev/null || \
    useradd -r -g %{prometheus_user} -M -d /opt/prometheus -s /sbin/nologin \
    -c "Prometheus monitoring" %{prometheus_user}
exit 0


%post
%systemd_post %{name}.service

if /usr/sbin/selinuxenabled ; then
    %relabel_files
fi


%preun
%systemd_preun %{name}.service
%postun
%systemd_postun %{name}.service


%clean
if [ -d %{buildroot} ] ; then
  rm -rf %{buildroot}
fi

%files
%license LICENSE
%doc NOTICE
/usr/lib/systemd/system/%{name}.service
/usr/local/bin/promtool
/usr/local/bin/prometheus
%defattr(-,%{prometheus_user},%{prometheus_user},750)
%config(noreplace) %{_sysconfdir}/prometheus/*
%dir /etc/prometheus
%dir /opt/prometheus
%dir /opt/prometheus/consoles
%dir /opt/prometheus/console_libraries
/opt/prometheus/consoles/index.html.example
/opt/prometheus/consoles/node-cpu.html
/opt/prometheus/consoles/node-disk.html
/opt/prometheus/consoles/node.html
/opt/prometheus/consoles/node-overview.html
/opt/prometheus/consoles/prometheus.html
/opt/prometheus/consoles/prometheus-overview.html
/opt/prometheus/console_libraries/menu.lib
/opt/prometheus/console_libraries/prom.lib


%changelog
* Tue Mar 20 2018 georou - 2.2.1-1
- Updated to new version

* Sun Mar 11 2018 georou - 2.2.0-1
- Updated to new version

* Sat Mar 10 2018 georou - 2.1.0-1
- Initial creation
