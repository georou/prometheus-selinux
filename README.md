# prometheus-selinux

**This policy is designed to be a base to build upon.** Currently I would consider this in beta

The main focus of this policy is:
* To be run without docker
* node_exporter
* alertmanager
* extensible to other exporters 

The current policy allows you to setup a Prometheus server and scrape targets with node_exporter and recieve alerts with alertmanager. Other exporters will be added as I find a need to use them. I am happy for pull requests to add features if you've already done them. For a front end, grafana is recommended and I have a policy created for that too: https://github.com/georou/grafana-selinux

In an effort to make the policy handle all the different types of exporters more cleanly, I have created a template interface to use that will setup the basic framework for each exporter:
promethuesd_t, $1_prometheusd_exporter_t for exporters and $1_prometheusd_t for alertmanager (future pushgateway will be added).

How-to add exporters:
* Name and create the interface template in the .te file. Eg: prometheus_exporter_template(namehere) This will create relevent labels from the .if file. If you need to create more for your exporter, you need to declare them in the .te file.
* Create a local policy section (use node_exporter's as an example) for the new exporter in the .te file and add permissions as needed.

*Included are service files that indicate where you will be storing logs and data by default. Remember to label your directory if you don't choose these defaults.*


## node_exporter Information
If you don't use the default port of 9100/tcp, you will need to label it with: node_prometheusd_exporter_port_t

The following collectors for node_exporter are untested and partially implemented(see commented code in .te):
```--collector.gmond --collector.megacli --collector.runit --collector.supervisord```

No doubt more permissions could be needed for the exisiting collectors that work, please keep an eye out for AVC denails.

## Alertmanager Information
If you don't use the default port of 9093/tcp, you will need to label it with: alertmanager_prometheusd_port_t

The default mesh address does work but the actual mesh functionality is currently untested. 

## Installation
```sh
# Clone the repo
git clone https://github.com/georou/prometheus-selinux.git

# Optional - Copy relevant .if interface file to /usr/share/selinux/devel/include to expose them when building and for future modules
install -Dp -m 0664 -o root -g root prometheusd.if /usr/share/selinux/devel/include/myapplications/prometheusd.if

# Compile the selinux module (see below)

# Install the SELinux policy module. Compile it before hand to ensure proper compatibility (see below)
semodule -i prometheusd.pp

# Create required directories
install -d -m 0750 -o prometheus -g prometheus /etc/{alertmanager,prometheus}

# Restore all the correct context labels after creating the directories and setting owner,group permissions
restorecon -RvF /etc/{alertmanager,prometheus}
restorecon -RvF /etc/systemd/system/{alertmanager.service,prometheus.service,node-exporter.service}
restorecon -RvF /opt/{alertmanager,prometheus}
restorecon -RvF /usr/local/bin/{alertmanager,node_exporter,prometheus,promtool}

# Label alertmananger default port. Change if needed.
semanage port -a -t alertmanager_prometheusd_port_t -p tcp 9093

# Start prometheus stack
systemctl start prometheus.service alertmanager.service node-exporter.service

# Ensure it's working in the proper confinement
ps -eZ | grep prometheus
```

## How To Compile The Module Locally (Needed before installing)
Ensure you have the `selinux-policy-devel` package installed.
```sh
# Ensure you have the devel packages
yum install selinux-policy-devel setools-console
# Change to the directory containing the .if, .fc & .te files
cd prometheus-selinux
make -f /usr/share/selinux/devel/Makefile prometheusd.pp
semodule -i prometheusd.pp
```

## Debugging and Troubleshooting

* If you're getting permission errors, uncomment permissive in the .te file and try again. Re-check logs for any issues. Or `semanage permissive -a prometheusd_t`
* Easy way to add in allow rules is the below command, then copy or redirect into the .te module. Rebuild and re-install:
* Don't forget to actually look at what is suggested. audit2allow will most likely go for a coarse grained permission!

```sh
ausearch -m avc,user_avc,selinux_err -ts recent | audit2allow -R
```
If you get a could not open interface info [/var/lib/sepolgen/interface_info] error. 
Ensure policycoreutils-devel is installed and/or run: `sepolgen-ifgen`

## Compatibility Notes
Built on CentOS 7.4 at the time with:
```
selinux-policy-targeted-3.13.1-166.el7_4.7.noarch
libselinux-2.5-11.el7.x86_64
libselinux-python-2.5-11.el7.x86_64
selinux-policy-3.13.1-166.el7_4.7.noarch
selinux-policy-devel-3.13.1-166.el7_4.7.noarch
```
