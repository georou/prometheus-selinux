%global  prometheus_user	prometheus

# Relabel files
%global relabel_files() %{_sbindir}/restorecon -RF %{_sysconfdir}/prometheus %{_usr}/local/bin/promtool %{_usr}/local/bin/prometheus /opt/prometheus &> /dev/null || :

%global selinux_policyver 3.13.1-40

Name:           alertmanager
Version:        0.14.0
Release:        1%{?dist}
Summary:        Alertmanager CentOS 7 rpm package

License:        ASL 2.0
URL:            http://prometheus.io
Source0:        %{name}-%{version}.linux-amd64.tar.gz
Source1:	%{name}.service

BuildRequires:	systemd
Requires:	systemd
Requires(pre):	shadow-utils
Requires(post): selinux-policy-base >= %{selinux_policyver}, policycoreutils, systemd

%description
Install alertmanager from source

%prep
%setup -q -n %{name}-%{version}.linux-amd64

%install
if [ -d %{buildroot} ] ; then
  rm -rf %{buildroot}
fi

install -Dp -m 0755 amtool %{buildroot}%{_usr}/local/bin/amtool
install -Dp -m 0755 alertmanager %{buildroot}%{_usr}/local/bin/alertmanager

install -Dp -m 0640 simple.yml %{buildroot}/%{_sysconfdir}/alertmanager/simple.yml

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
/usr/local/bin/amtool
/usr/local/bin/alertmanager

%defattr(-,%{prometheus_user},%{prometheus_user},750)
%config(noreplace) %{_sysconfdir}/alertmanager/*
%dir /opt/alertmanager
%dir /etc/alertmanager

%changelog
* Thu Mar 22 2018 georou - 0.14.0-1
- Initial creation
